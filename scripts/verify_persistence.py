"""Controlled local synthetic-demo outage/restart rehearsal. Requires dev graph port.
Run only while no other operator is mutating this demo.
"""

import json
import subprocess
import time
import httpx
from app.graph.repository import Repository
from app.config import settings, ROOT
from app.domain.models import now_iso

if not settings.demo_mode or settings.falkordb_graph != "company_brain_digiplus_services":
    raise SystemExit("This check is restricted to the configured synthetic demo graph.")
repo = Repository()
compose = ["docker", "compose", "-f", "compose.yaml", "-f", "compose.dev.yaml"]


def command(*args):
    return subprocess.run(
        [*compose, *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def snapshot():
    return {
        "nodes": repo.query("MATCH (n) RETURN count(n)")[0][0],
        "claims": repo.query("MATCH (n:Claim) RETURN count(n)")[0][0],
        "sources": len(repo.sources(["all_employees", "engineering", "leadership"])),
        "epoch": repo.epoch(),
        "review_ids": sorted(t["id"] for t in repo.tasks()),
    }


def wait_ready(client):
    for _ in range(30):
        try:
            if client.get("/health/ready").status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(1)
    raise RuntimeError("Stack did not recover")


headers = {"origin": "http://localhost:3000", "x-brain-csrf": "1"}
with httpx.Client(base_url="http://127.0.0.1:3000/api/v1", headers=headers, timeout=15) as client:
    wait_ready(client)
    client.post("/demo/session", json={"persona": "Engineer"}).raise_for_status()
    session = client.post("/sessions", json={}).json()["id"]
    run = client.post(
        "/investigations", json={"session_id": session, "question": "What could block Atlas Client Portal?"}
    ).json()["run_id"]
    for _ in range(30):
        result = client.get("/investigations/" + run).json()
        if result["status"] == "complete":
            break
        time.sleep(0.2)
    assert result["status"] == "complete"
    before = snapshot()
    assert before["sources"] == 200 and before["review_ids"]
    config = {}
    for name in ["dir", "appendonly", "appendfsync"]:
        config.update(repo.db.connection.config_get(name))
    saved = command("exec", "-T", "falkordb", "redis-cli", "SAVE")
    command("stop", "falkordb")
    try:
        live = client.get("/health/live").status_code
        ready = client.get("/health/ready").status_code
        pending = client.post(
            "/investigations", json={"session_id": session, "question": "What could block Atlas Client Portal?"}
        ).json()["run_id"]
        for _ in range(30):
            failed = client.get("/investigations/" + pending).json()
            if failed["status"] == "failed":
                break
            time.sleep(0.2)
        assert live == 200 and ready == 503
        assert failed["status"] == "failed" and "blocks" not in failed and "answer" not in failed
    finally:
        command("start", "falkordb")
    wait_ready(client)
    after_graph = snapshot()
    assert after_graph == before
    command("restart", "api")
    wait_ready(client)
    reopened = client.get("/investigations/" + run)
    reopened.raise_for_status()
    assert reopened.json()["status"] == "complete" and reopened.json()["blocks"] == result["blocks"]
    after_api = snapshot()
    assert after_api == before
    report = {
        "generated_at": now_iso(),
        "configuration": config,
        "save_result": saved,
        "before": before,
        "after_graph_restart": after_graph,
        "after_api_restart": after_api,
        "outage": {
            "liveness_status": live,
            "readiness_status": ready,
            "investigation_status": failed["status"],
            "fabricated_answer": False,
        },
        "saved_run_reopened": True,
        "same_identity_cookie_survived": True,
        "limitation": "Controlled SAVE and graceful stop/start. Not a power-loss test.",
    }
    path = ROOT / "artifacts/persistence.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(
        "PASS: graph/claims/epoch/reviews preserved, saved run reopened after API restart; graph outage returned no answer."
    )
