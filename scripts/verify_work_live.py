"""Opt-in paid-provider check on a random disposable graph, never the working workspace."""

import json
import secrets
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient
from app import main
from app.main import app
from app.config import settings, ROOT
from app.graph.repository import Repository
from app.memory.store import Store
from app.ingestion.service import Ingestion


def check(response):
    if response.status_code != 200:
        raise RuntimeError(
            f"Workflow request returned {response.status_code}: {response.json().get('error', {}).get('message', 'failed')}"
        )
    return response.json()


if not settings.llm_api_key or not settings.llm_model:
    raise SystemExit("Configure a provider key and model before running this opt-in check.")
report = {"model": settings.llm_model, "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
repo = Repository("company_brain_live_work_" + secrets.token_hex(8))
started = time.monotonic()
try:
    with tempfile.TemporaryDirectory() as directory:
        store = Store(str(Path(directory) / "ops.sqlite"))
        ingestion = Ingestion(repo, store)
        ingestion.seed()
        main.repo, main.store, main.ingestion = repo, store, ingestion
        with TestClient(app, headers={"origin": "http://localhost:3000", "x-brain-csrf": "1"}) as client:
            check(client.post("/api/v1/demo/session", json={"persona": "Lead"}))
            notes = (
                "Northstar handover, 30 October 2026. Dev Shah missed the meeting. "
                "Decision: require recorded client approval before the portal rollout.\n\n"
                "Maya Rao will validate the tenant mapping by 2026-11-02.\n\n"
                "Leah Chen will obtain the client acceptance sign-off by 2026-11-03.\n\n"
                "The identity ownership conflict remains unresolved; do not assume the newer chat wins."
            )
            m = check(
                client.post(
                    "/api/v1/meetings",
                    json={
                        "title": "Northstar tenant handover verification",
                        "kind": "handover",
                        "agenda": "Acceptance and identity ownership",
                        "notes": notes,
                        "scheduled_at": "2026-10-30T04:30:00Z",
                        "participant_ids": ["person:maya", "person:dev", "person:leah"],
                        "absent_ids": ["person:dev"],
                        "project_id": "project:atlas-portal",
                        "acl_groups": ["engineering"],
                    },
                )
            )
            draft = check(client.post("/api/v1/meetings/" + m["id"] + "/recap"))
            assert draft["mode"] == "live_model" and len(draft["recap"]["actions"]) >= 2
            assert all(a["quote"] in notes for a in draft["recap"]["actions"])
            detail = check(
                client.post(
                    "/api/v1/meetings/" + m["id"] + "/confirm-recap",
                    json={"expected_version": m["version"], "draft_id": draft["id"], "recap": draft["recap"]},
                )
            )
            action = detail["actions"][0]
            next_meeting = check(
                client.post(
                    "/api/v1/meetings",
                    json={
                        "title": "Northstar follow-up verification",
                        "kind": "meeting",
                        "agenda": "Close validation",
                        "notes": "Review the tenant validation outcome.",
                        "scheduled_at": "2026-11-03T04:30:00Z",
                        "participant_ids": ["person:maya", "person:dev"],
                        "project_id": "project:atlas-portal",
                        "acl_groups": ["engineering"],
                        "previous_meeting_id": m["id"],
                        "carry_action_ids": [action["id"]],
                    },
                )
            )
            carried = check(client.get("/api/v1/meetings/" + next_meeting["id"]))["actions"][0]
            assert carried["id"] == action["id"] and len(carried["meeting_ids"]) == 2
            updated = check(
                client.patch(
                    "/api/v1/actions/" + action["id"],
                    json={"expected_version": carried["version"], "owner_id": "person:dev"},
                )
            )
            final = check(
                client.patch(
                    "/api/v1/actions/" + action["id"],
                    json={
                        "expected_version": updated["version"],
                        "status": "done",
                        "outcome": "Tenant mapping verified; client approval recorded.",
                    },
                )
            )
            brief = check(
                client.post("/api/v1/meetings/" + m["id"] + "/brief", json={"recipient_id": "person:dev"})
            )
            assert brief["mode"] == "live_model"
            assert all(set(b["reference_ids"]) <= set(brief["references"]) for b in brief["blocks"])
            check(client.post("/api/v1/demo/session", json={"persona": "Viewer"}))
            assert client.get("/api/v1/meetings/" + m["id"]).status_code == 404
            assert all(a["id"] != action["id"] for a in check(client.get("/api/v1/actions")))
            report.update(
                status="passed",
                extracted_actions=len(detail["actions"]),
                decisions=len(detail["meeting"]["decisions"]),
                knowledge_links=len(detail["meeting"]["knowledge_links"]),
                brief_blocks=len(brief["blocks"]),
                carry_preserved_identity=True,
                final_status=final["status"],
                viewer_isolated=True,
            )
        store.db.close()
except Exception as exc:
    report.update(status="failed", error_type=type(exc).__name__, message=str(exc)[:300])
finally:
    repo.graph.delete()
    report["duration_seconds"] = round(time.monotonic() - started, 2)
    path = ROOT / "artifacts/digiplus-live-workflow.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
if report["status"] != "passed":
    raise SystemExit(1)
