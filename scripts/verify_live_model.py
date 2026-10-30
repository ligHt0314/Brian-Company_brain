"""Explicit live-model gate. Uses synthetic data and an isolated FalkorDB graph.
No secrets, headers, provider error bodies or private prompts are printed.
"""

import json
import secrets
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient
from app.config import settings, ROOT
from app.domain.models import now_iso
from app.graph.repository import Repository
from app.ingestion.service import Ingestion
from app.memory.store import Store
from app.main import app
from app.agent.provider import Provider
import app.main as main

if not settings.llm_api_key or not settings.llm_model:
    raise SystemExit("Configure LLM_API_KEY and LLM_MODEL first")
body = "Maya Rao worked on Notification Service.\n\nNotification Service depends on Identity Gateway."
source_id = "doc:live-gemini-verification"
report = {
    "generated_at": now_iso(),
    "model": settings.llm_model,
    "prompt_version": "1.2",
    "synthetic": True,
    "scope": "isolated graph; working demo was not changed",
    "passed": False,
}
repo = Repository("company_brain_live_" + secrets.token_hex(8))
original_next_tools = Provider.next_tools


def record_tools(self, *args, **kwargs):
    decision = original_next_tools(self, *args, **kwargs)
    report.setdefault("tool_decisions", []).append(decision.model_dump(exclude_none=True))
    return decision


Provider.next_tools = record_tools
with tempfile.TemporaryDirectory() as tmp:
    store = Store(str(Path(tmp) / "ops.sqlite"))
    settings.upload_dir = str(Path(tmp) / "originals")
    ingestion = Ingestion(repo, store)
    ingestion.seed()
    main.repo, main.store, main.ingestion = repo, store, ingestion
    started = time.monotonic()
    try:
        with TestClient(app, headers={"origin": "http://localhost:3000", "x-brain-csrf": "1"}) as client:
            client.post("/api/v1/demo/session", json={"persona": "Lead"}).raise_for_status()
            metadata = {
                "source_id": source_id,
                "kind": "document",
                "title": "Live Gemini verification · synthetic evidence",
                "source_updated_at": settings.demo_clock_iso,
                "acl_groups": ["engineering"],
            }
            pending = client.post(
                "/api/v1/imports",
                data={"metadata": json.dumps(metadata)},
                files={"files": ("new-live-evidence.md", body, "text/markdown")},
            )
            pending.raise_for_status()
            job = client.get("/api/v1/jobs/" + pending.json()["job_ids"][0]).json()
            report["import"] = {k: job.get(k) for k in ["status", "accepted", "pending", "revision_id"]}
            report["import_duration_ms"] = round((time.monotonic() - started) * 1000)
            if job["status"] != "complete":
                report["failure_stage"] = "import"
                report["safe_error"] = job.get("error", "Import did not complete")[:180]
                raise RuntimeError("Live import failed")
            claims, _ = repo.claims(
                [s["id"] for s in repo.sources(["all_employees", "engineering", "leadership"])]
            )
            live_claims = [c for c in claims if c.evidence.source_id == source_id]
            required = {
                ("person:maya", "WORKED_ON", "service:messages"),
                ("service:messages", "DEPENDS_ON", "service:identity"),
            }
            assert required <= {(c.subject_id, c.predicate, c.object_id) for c in live_claims}
            assert all(
                c.evidence.extraction_method == "model" and c.evidence.ingestion_mode == "live_import"
                for c in live_claims
            )
            assert all(c.evidence.quote in body for c in live_claims)
            report["extracted_claims"] = [
                {
                    "subject_id": c.subject_id,
                    "predicate": c.predicate,
                    "object_id": c.object_id,
                    "evidence_id": c.evidence.id,
                    "quote": c.evidence.quote,
                }
                for c in live_claims
            ]

            def ask(question):
                sid = client.post("/api/v1/sessions", json={}).json()["id"]
                pending = client.post(
                    "/api/v1/investigations", json={"session_id": sid, "question": question}
                )
                pending.raise_for_status()
                result = client.get("/api/v1/investigations/" + pending.json()["run_id"])
                result.raise_for_status()
                answer = result.json()
                assert answer["status"] == "complete"
                return answer

            answer = ask("Who has worked on Notification Service?")
            assert answer["execution_mode"] == "live_model"
            assert any(
                e["source_id"] == source_id and e["extraction_method"] == "model" for e in answer["evidence"]
            )
            assert any("Maya Rao" in b["text"] and b["evidence_ids"] for b in answer["blocks"])
            report["new_document_investigation"] = {
                k: answer[k] for k in ["execution_mode", "answer_state", "intent", "metrics"]
            }
            release = ask("What could block Atlas Client Portal, and which customer commitment is affected?")
            report["release_investigation"] = {
                k: release[k]
                for k in ["execution_mode", "answer_state", "intent", "metrics", "scope", "agent_trace"]
            }
            assert release["execution_mode"] == "live_model" and release["intent"] == "release_risk"
            assert 1 <= release["metrics"]["agent_tool_calls"] <= 6
            assert release["metrics"]["agent_rounds"] <= 2
            assert any(
                f["category"] == "blocker" and "ticket:T-101" in f["entity_ids"] for f in release["findings"]
            )
            assert release["conflicts"]
            client.post("/api/v1/demo/session", json={"persona": "Viewer"}).raise_for_status()
            viewer = ask("Who has worked on Notification Service?")
            assert not viewer["evidence"] and source_id not in json.dumps(viewer)
            report["viewer_isolation_passed"] = True
            report["passed"] = True
    except Exception as exc:
        report["error_type"] = type(exc).__name__
    finally:
        Provider.next_tools = original_next_tools
        repo.graph.delete()
        store.db.close()
report["total_duration_ms"] = round((time.monotonic() - started) * 1000)
report["human_semantic_score"] = "not_scored"
path = ROOT / "artifacts/gemini-live-verification.json"
path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 1)
