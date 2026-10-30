"""Scale and provenance checks for the medium-sized, readable demo corpus."""

import json
from collections import Counter
from app.ingestion.service import FIXTURES, registry, validate_candidates
from app.domain.models import Candidate
from conftest import login, ask


def test_complete_dataset_and_pagination(world):
    repo, store, ingest, client = world
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    assert Counter(e["kind"] for e in registry()) == manifest["entity_counts"]
    assert len(manifest["sources"]) == 200 and manifest["claim_count"] == 432
    for item in manifest["sources"]:
        record = json.loads((FIXTURES / item["path"]).read_text())
        validate_candidates(
            record["envelope"]["body"], [Candidate.model_validate(c) for c in record["claims"]], registry()
        )
    login(client, "Lead")
    first = client.get("/api/v1/sources?limit=100").json()
    second = client.get("/api/v1/sources?limit=100&offset=100").json()
    assert first["total"] == 200 and len(first["items"]) == len(second["items"]) == 100
    assert len({s["id"] for s in first["items"] + second["items"]}) == 200
    assert len(client.get("/api/v1/entities/search").json()) == 180
    claims, truncated = repo.claims(
        [s["id"] for s in repo.sources(["all_employees", "engineering", "leadership"])]
    )
    assert len(claims) == 432 and not truncated
    assert len([c for c in claims if c.predicate == "MEMBER_OF"]) == 40
    login(client, "Engineer")
    assert client.get("/api/v1/sources?limit=100").json()["total"] == 196
    login(client, "Viewer")
    visible = client.get("/api/v1/sources?limit=100").json()
    assert visible["total"] == 23
    assert all("leadership" not in s["id"] for s in visible["items"])


def test_other_stories_and_cross_project_impact(world):
    repo, store, ingest, client = world
    login(client)
    delivery = ask(client, "What could block Delivery Operations?")
    assert any(f["category"] == "blocker" and "ticket:T-109" in f["entity_ids"] for f in delivery["findings"])
    refund = ask(client, "What could block Claims Automation?")
    assert any(f["category"] == "blocker" and "ticket:T-101" in f["entity_ids"] for f in refund["findings"])
    impact = ask(client, "What may be affected if Identity Gateway becomes unavailable?")
    text = " ".join(b["text"] for b in impact["blocks"])
    assert all(name in text for name in ["Atlas Client Portal", "Claims Automation", "Managed Cloud Migration"])
    assert all(e["evidence_ids"] for e in impact["graph"]["edges"])
    assert "does not establish an outage" in text


def test_service_impact_keeps_three_dependency_hop_limit(world):
    from app.domain.models import SourceEnvelope
    from app.reasoning.investigate import Investigator

    repo, store, ingest, client = world
    links = [("service:configuration", "service:search"), ("service:search", "service:support")]
    texts = ["Configuration Registry depends on Knowledge Search.", "Knowledge Search depends on Support Queue."]
    body = "\n\n".join(texts)
    candidates = [
        Candidate(
            subject_id=s,
            predicate="DEPENDS_ON",
            object_id=o,
            quote=quote,
            start=body.index(quote),
            end=body.index(quote) + len(quote),
        )
        for (s, o), quote in zip(links, texts)
    ]
    envelope = SourceEnvelope(
        source_id="doc:hop-budget",
        kind="document",
        title="Synthetic long dependency path",
        source_updated_at="2026-10-17T03:30:00Z",
        acl_groups=["engineering"],
        body=body,
    )
    assert ingest.import_source(envelope, "operator", candidates, True)["status"] == "complete"
    # Resource Monitor -> Configuration Registry -> Knowledge Search -> Support Queue is 3 DEPENDS_ON hops.
    # Support Queue -> Notification Service would be hop 4 and must be excluded.
    answer = Investigator(repo).run(
        "hop_budget",
        "What may be affected if Notification Service becomes unavailable?",
        ["all_employees", "engineering"],
    )
    assert not any(
        "project:infrastructure-alerts" in f.entity_ids for f in answer.findings if f.category == "conditional_impact"
    )
    assert answer.scope.truncated
    node_ids = {n.id for n in answer.graph.nodes}
    assert all(e.source_entity_id in node_ids and e.target_entity_id in node_ids for e in answer.graph.edges)
