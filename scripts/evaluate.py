"""Deterministic regression evaluation against isolated real FalkorDB graphs.
Human semantic support scoring and live-model scoring are separate, unclaimed gates.
"""

import json
import secrets
import platform
import statistics
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient
from app.reasoning.investigate import Investigator
from app.main import app
import app.main as main
from app.config import ROOT, settings
from app.graph.repository import Repository
from app.ingestion.service import Ingestion, FIXTURES
from app.memory.store import Store
from app.domain.models import SourceEnvelope, Candidate, now_iso

# This harness is a deterministic regression gate; live runs use verify_live_model.py.
settings.llm_api_key = ""

cases = [json.loads(line) for line in (ROOT / "evals/questions.jsonl").read_text().splitlines()]
results = []
headers = {"origin": "http://localhost:3000", "x-brain-csrf": "1"}


def login(client, persona):
    r = client.post("/api/v1/demo/session", json={"persona": persona})
    r.raise_for_status()


def ask(client, question, previous=None):
    sid = client.post("/api/v1/sessions", json={}).json()["id"]
    payload = {"session_id": sid, "question": question}
    if previous:
        payload["previous_run_id"] = previous
    r = client.post("/api/v1/investigations", json=payload)
    r.raise_for_status()
    for _ in range(60):
        a = client.get("/api/v1/investigations/" + r.json()["run_id"]).json()
        if a["status"] == "complete":
            return a
        if a["status"] == "failed":
            raise RuntimeError(a["error"])
        time.sleep(0.5)
    raise TimeoutError("Run timeout")


for case in cases:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Repository("company_brain_eval_" + secrets.token_hex(8))
        store = Store(str(Path(tmp) / "ops.sqlite"))
        ingestion = Ingestion(repo, store)
        ingestion.seed()
        main.repo, main.store, main.ingestion = repo, store, ingestion
        try:
            with TestClient(app, headers=headers) as client:
                login(client, case["persona"])
                setup = case.get("setup")
                previous = None
                job = None
                epoch = repo.epoch()
                if setup == "compare_done":
                    previous = ask(client, case["question"])["run_id"]
                if setup in {"t101_done", "compare_done", "t101_invalid"}:
                    r = client.post(
                        "/api/v1/demo/apply-revision",
                        json={"fixture_id": "t101_invalid" if setup == "t101_invalid" else "t101_done"},
                    )
                    job = client.get("/api/v1/jobs/" + r.json()["job_ids"][0]).json()
                if setup == "unchanged":
                    record = json.loads((FIXTURES / "ticket_T-101.json").read_text())
                    job = ingestion.import_source(
                        SourceEnvelope.model_validate(record["envelope"]),
                        "operator",
                        [Candidate.model_validate(c) for c in record["claims"]],
                        True,
                    )
                if setup == "revoke_and_reopen":
                    saved = ask(client, case["question"])
                    login(client, "Lead")
                    client.post("/api/v1/demo/apply-revision", json={"fixture_id": "restrict_runbook"})
                    login(client, "Engineer")
                    answer = client.get("/api/v1/investigations/" + saved["run_id"]).json()
                else:
                    answer = ask(client, case["question"], previous)
                text = " ".join(b["text"] for b in answer["blocks"])
                payload = json.dumps(answer)
                checks = []
                if "state" in case:
                    checks.append(answer["answer_state"] == case["state"])
                checks.extend(term in text for term in case.get("contains", []))
                checks.extend(term not in payload for term in case.get("forbidden", []))
                checks.extend(
                    any(e["predicate"] == p for e in answer["graph"]["edges"])
                    for p in case.get("predicates", [])
                )
                checks.extend(
                    any(e["source_id"] == sid for e in answer["evidence"])
                    for sid in case.get("source_ids", [])
                )
                if "blocker" in case:
                    checks.append(
                        any(f["category"] == "blocker" for f in answer["findings"]) == case["blocker"]
                    )
                if "job_state" in case:
                    checks.append(job["status"] == case["job_state"])
                if case.get("same_epoch"):
                    checks.append(repo.epoch() == epoch and job["unchanged"])
                if case.get("empty_body"):
                    checks.append(not answer["blocks"] and not answer["evidence"])
                if case.get("candidate_ids"):
                    checks.append(sorted(e["id"] for e in answer["candidates"]) == case["candidate_ids"])
                if case.get("removed_status"):
                    checks.append(
                        any(
                            "updated status is " + case["removed_status"] in c["text"] and c["evidence_ids"]
                            for c in answer["changes"]["removed"]
                        )
                    )
                ev_ids = {e["id"] for e in answer["evidence"]}
                checks.append(
                    all(
                        set(b["evidence_ids"]) <= ev_ids and (b["kind"] != "fact" or b["evidence_ids"])
                        for b in answer["blocks"]
                    )
                )
                checks.append(
                    all(set(e["evidence_ids"]) <= ev_ids and e["claim_ids"] for e in answer["graph"]["edges"])
                )
                results.append(
                    {
                        "id": case["id"],
                        "passed": all(checks),
                        "checks": len(checks),
                        "state": answer["answer_state"],
                        "execution_mode": answer["execution_mode"],
                        "metrics": answer["metrics"],
                        "human_factual_support": "not_scored",
                    }
                )
        except Exception as exc:
            results.append(
                {
                    "id": case["id"],
                    "passed": False,
                    "error": type(exc).__name__,
                    "human_factual_support": "not_scored",
                }
            )
        finally:
            repo.graph.delete()
            store.db.close()
# Warm retrieval uses its own random graph, never an inherited/working graph name.
warm = []
with tempfile.TemporaryDirectory() as tmp:
    sample_repo = Repository("company_brain_eval_" + secrets.token_hex(8))
    sample_store = Store(str(Path(tmp) / "warm.sqlite"))
    try:
        Ingestion(sample_repo, sample_store).seed()
        for index in range(30):
            answer = Investigator(sample_repo).run(
                "benchmark_" + str(index), "What could block Atlas Client Portal?", ["all_employees", "engineering"]
            )
            warm.append(answer.metrics.duration_ms)
    finally:
        sample_repo.graph.delete()
        sample_store.db.close()
manifest = json.loads((FIXTURES / "manifest.json").read_text())
report = {
    "generated_at": now_iso(),
    "mode": "configured_model" if settings.llm_api_key else "deterministic",
    "fixture_seed": manifest["seed_version"],
    "hardware": platform.platform() + " " + platform.machine(),
    "graph_image": "falkordb/falkordb:v4.14.11",
    "python": platform.python_version(),
    "prompt_version": "1.2",
    "passed": sum(r["passed"] for r in results),
    "total": len(results),
    "results": results,
    "warm_latency": {
        "sample_size": len(warm),
        "median_ms": statistics.median(warm),
        "p95_ms": sorted(warm)[int(0.95 * len(warm)) - 1],
        "scope": "engine-only, local FalkorDB, synthetic corpus; excludes HTTP/browser latency",
    },
    "human_factual_support": "Not scored. Citation-ID validity is not semantic entailment.",
    "live_extraction": "Excluded from this offline regression gate; see artifacts/gemini-live-verification.json.",
    "cost": "Not measured; no invented pricing.",
}
out = ROOT / "evals/results"
out.mkdir(exist_ok=True)
(out / "latest.json").write_text(json.dumps(report, indent=2) + "\n")
(out / "latest.md").write_text(
    f"# Observed evaluation\n\n{report['passed']}/{report['total']} deterministic cases passed on {report['generated_at']}.\n\n30 warm engine runs: median {report['warm_latency']['median_ms']} ms, p95 {report['warm_latency']['p95_ms']} ms. Engine-only timing on {report['hardware']}; not browser latency.\n\nHuman factual support is unscored. Live model extraction is unverified without a key. No cost comparison or GraphRAG superiority claim is made.\n"
)
print(json.dumps({k: v for k, v in report.items() if k not in {"results"}}, indent=2))
for r in results:
    if not r["passed"]:
        print("FAILED", r)
raise SystemExit(0 if report["passed"] == len(results) else 1)
