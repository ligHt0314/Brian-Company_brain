import httpx
import os
import time

base = os.environ.get("BRAIN_API_URL", "http://127.0.0.1:8000") + "/api/v1"
headers = {"origin": os.environ.get("BRAIN_ORIGIN", "http://localhost:3000"), "x-brain-csrf": "1"}
with httpx.Client(base_url=base, headers=headers, timeout=30) as client:
    ready = client.get("/health/ready")
    ready.raise_for_status()
    client.post("/demo/session", json={"persona": "Engineer"}).raise_for_status()
    session = client.post("/sessions", json={}).json()["id"]
    response = client.post(
        "/investigations", json={"session_id": session, "question": "What could block Atlas Client Portal?"}
    )
    response.raise_for_status()
    for _ in range(40):
        result = client.get("/investigations/" + response.json()["run_id"]).json()
        if result["status"] == "complete":
            break
        if result["status"] == "failed":
            raise RuntimeError(result["error"])
        time.sleep(0.5)
    assert result["status"] == "complete"
    assert any(f["category"] == "blocker" for f in result["findings"]), (
        "Seed blocker absent: apply this smoke test to a fresh scenario"
    )
    assert result["conflicts"]
    print(
        f"PASS: {result['answer_state']}, {len(result['evidence'])} evidence excerpts, {result['metrics']['duration_ms']} ms, {result['execution_mode']}"
    )
