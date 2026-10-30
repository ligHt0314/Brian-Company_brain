"""Real source-revision edits: scope, concurrency, status reasoning and preserved claims."""

import json
from app.domain.models import Candidate, SourceEnvelope
from app.ingestion.service import FIXTURES
from conftest import login, ask


def test_status_edit_preserves_contributions_and_supports_any_ticket(world):
    repo, store, ingest, client = world
    login(client, "Engineer")
    assert client.get("/api/v1/sources/ticket:T-106/ticket").status_code == 403
    login(client, "Lead")
    details = client.get("/api/v1/sources/ticket:T-106/ticket").json()
    assert details["status"] == "done" and details["blocked_entities"] == ["service:identity"]
    old_revision = details["expected_revision_id"]
    edited = client.post(
        "/api/v1/sources/ticket:T-106/ticket-status",
        json={"status": "open", "expected_revision_id": old_revision},
    )
    assert edited.status_code == 200, edited.text
    job = client.get("/api/v1/jobs/" + edited.json()["job_ids"][0]).json()
    assert job["status"] == "complete", job
    claims, _ = repo.claims(["ticket:T-106"])
    assert {c.subject_id for c in claims if c.predicate == "WORKED_ON"} == {"person:maya", "person:dev"}
    assert {c.scalar for c in claims if c.predicate == "STATUS"} == {"open"}
    assert len(repo.revisions("ticket:T-106")) == 2
    for c in claims:
        passage = repo.evidence(c.evidence.id, ["ticket:T-106"])
        assert passage and passage["quote"] == c.evidence.quote
    stale = client.post(
        "/api/v1/sources/ticket:T-106/ticket-status",
        json={"status": "done", "expected_revision_id": old_revision},
    )
    assert stale.status_code == 409
    hidden = client.get("/api/v1/sources/not-real/ticket")
    assert hidden.status_code == 404


def test_ticket_completion_changes_risk_without_fixture_shortcut(world):
    repo, store, ingest, client = world
    login(client, "Lead")
    before = ask(client, "What could block Atlas Client Portal?")
    details = client.get("/api/v1/sources/ticket:T-101/ticket").json()
    receipt = client.post(
        "/api/v1/sources/ticket:T-101/ticket-status",
        json={"status": "done", "expected_revision_id": details["expected_revision_id"]},
    ).json()
    assert client.get("/api/v1/jobs/" + receipt["job_ids"][0]).json()["status"] == "complete"
    after = ask(client, "What could block Atlas Client Portal?", previous_run_id=before["run_id"])
    assert not any(
        f["category"] == "blocker" and "ticket:T-101" in f["entity_ids"] for f in after["findings"]
    )
    assert after["conflicts"] and any(
        "updated status is done" in c["text"] for c in after["changes"]["removed"]
    )
    details = client.get("/api/v1/sources/ticket:T-101/ticket").json()
    restored = client.post(
        "/api/v1/sources/ticket:T-101/ticket-status",
        json={"status": "blocked", "expected_revision_id": details["expected_revision_id"]},
    ).json()
    assert client.get("/api/v1/jobs/" + restored["job_ids"][0]).json()["status"] == "complete"
    assert any(f["category"] == "blocker" for f in ask(client, "What could block Atlas Client Portal?")["findings"])


def test_status_edit_preserves_pending_claim_and_validity(world):
    repo, store, ingest, client = world
    record = json.loads((FIXTURES / "ticket_T-106.json").read_text())
    envelope = SourceEnvelope.model_validate(record["envelope"])
    envelope.source_id = "ticket:reviewed-status"
    envelope.expected_revision_id = None
    candidates = [Candidate.model_validate(c) for c in record["claims"]]
    pending = next(c for c in candidates if c.predicate == "WORKED_ON")
    pending.extraction_score = 0.4
    pending.valid_to_ms = 1780000000000
    assert ingest.import_source(envelope, "operator", candidates, True)["status"] == "complete"
    login(client, "Lead")
    details = client.get("/api/v1/sources/ticket:reviewed-status/ticket").json()
    receipt = client.post(
        "/api/v1/sources/ticket:reviewed-status/ticket-status",
        json={"status": "blocked", "expected_revision_id": details["expected_revision_id"]},
    ).json()
    job = client.get("/api/v1/jobs/" + receipt["job_ids"][0]).json()
    assert job["status"] == "complete" and job["pending"] == 1
    rid = repo.source("ticket:reviewed-status")["active_revision_id"]
    rows = repo.query(
        "MATCH (r:SourceRevision {id:$rid})-[:HAS_CHUNK]->(ch)<-[:SUPPORTED_BY]-(c:Claim) WHERE c.review_state='pending' RETURN c.valid_to_ms",
        {"rid": rid},
    )
    assert rows == [[1780000000000]]
