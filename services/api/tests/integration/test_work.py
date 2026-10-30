"""Meetings, carry-forward identity, evidence and model failure isolation."""

import json
from app.work.models import Recap, BriefOutput, BriefBlock
from app.agent.provider import Provider
from app.work.service import Work
from conftest import login


def payload(**changes):
    return {
        "title": "Client portal handover",
        "kind": "handover",
        "agenda": "Review identity validation and open work",
        "notes": "Decision: require client acceptance. Maya Rao will validate the portal by 2026-11-02.",
        "scheduled_at": "2026-10-30T09:00:00+05:30",
        "participant_ids": ["person:maya", "person:dev"],
        "absent_ids": ["person:dev"],
        "project_id": "project:atlas-portal",
        "acl_groups": ["engineering"],
        **changes,
    }


def create(client, **changes):
    response = client.post("/api/v1/meetings", json=payload(**changes))
    assert response.status_code == 200, response.text
    return response.json()


def confirm(client, meeting):
    response = client.post(
        f"/api/v1/meetings/{meeting['id']}/confirm-recap",
        json={
            "expected_version": meeting["version"],
            "recap": {
                "summary": "Client acceptance gates handover.",
                "decisions": [
                    {"text": "Require acceptance.", "quote": "Decision: require client acceptance."}
                ],
                "actions": [
                    {
                        "text": "Validate the portal",
                        "quote": "Maya Rao will validate the portal by 2026-11-02.",
                        "owner_id": "person:maya",
                        "due_date": "2026-11-02",
                    }
                ],
                "knowledge_source_ids": [],
            },
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_seed_idempotence_and_role_scope(world):
    repo, store, _, client = world
    login(client, "Lead")
    assert len(client.get("/api/v1/meetings").json()) == 40
    assert len(client.get("/api/v1/actions").json()) == 100
    epoch = repo.epoch()
    Work(repo, store).seed()
    assert repo.epoch() == epoch
    login(client, "Viewer")
    assert len(client.get("/api/v1/meetings").json()) == 4
    assert client.post("/api/v1/meetings", json=payload()).status_code == 403


def test_carry_forward_preserves_identity_and_history(world):
    repo, store, _, client = world
    login(client)
    m = create(client)
    detail = confirm(client, m)
    action = detail["actions"][0]
    next_meeting = create(
        client, previous_meeting_id=m["id"], carry_action_ids=[action["id"]], notes="Next checkpoint"
    )
    current = client.get("/api/v1/meetings/" + next_meeting["id"]).json()["actions"][0]
    assert current["id"] == action["id"] and current["origin_meeting_id"] == m["id"]
    assert current["meeting_ids"] == [m["id"], next_meeting["id"]]
    assert current["due_date"] == "2026-11-02"
    assert current["history"][-1]["event"] == "action_carried_forward"
    revised = client.patch(
        "/api/v1/actions/" + action["id"],
        json={"expected_version": current["version"], "owner_id": "person:dev"},
    ).json()
    assert revised["history"][-1]["event"] == "action_reassigned"
    assert (
        client.patch(
            "/api/v1/actions/" + action["id"],
            json={"expected_version": current["version"], "status": "done", "outcome": "Verified"},
        ).status_code
        == 409
    )
    assert (
        client.patch(
            "/api/v1/actions/" + action["id"], json={"expected_version": revised["version"], "status": "done"}
        ).status_code
        == 422
    )
    closed = client.patch(
        "/api/v1/actions/" + action["id"],
        json={
            "expected_version": revised["version"],
            "status": "done",
            "outcome": "Client signed off on the validated portal.",
        },
    )
    assert closed.status_code == 200, closed.text
    assert closed.json()["history"][-1]["event"] == "action_closed"
    assert (
        client.post(
            "/api/v1/meetings", json=payload(previous_meeting_id=m["id"], carry_action_ids=[action["id"]])
        ).status_code
        == 409
    )
    assert repo.query("MATCH (r:WorkRevision) RETURN count(r)")[0][0] > 140


def test_quote_validation_and_invalid_people(world):
    _, _, _, client = world
    login(client)
    assert client.post("/api/v1/meetings", json=payload(participant_ids=["unknown"])).status_code == 422
    assert client.post("/api/v1/meetings", json=payload(acl_groups=["leadership"])).status_code == 403
    assert client.post("/api/v1/meetings", json=payload(scheduled_at="2026-10-30T09:00")).status_code == 422
    m = create(client)
    bad = client.post(
        "/api/v1/meetings/" + m["id"] + "/actions",
        json={"expected_version": 1, "text": "Invented work", "quote": "Not present in the notes"},
    )
    assert bad.status_code == 422
    login(client, "Viewer")
    assert client.get("/api/v1/meetings/" + m["id"]).status_code == 404
    assert all(x["id"] != m["id"] for x in client.get("/api/v1/meetings").json())


def test_ai_draft_confirmation_and_brief_references(world, monkeypatch):
    repo, _, _, client = world
    login(client)
    m = create(client)

    def generate(self, schema, prompt, data):
        assert not repo.lock._is_owned(), "Provider called inside the mutation lock"
        if schema is Recap:
            return Recap(
                summary="Validate the portal before handover.",
                actions=[
                    {
                        "text": "Validate portal",
                        "quote": "Maya Rao will validate the portal by 2026-11-02.",
                        "owner_id": "person:maya",
                        "due_date": "2026-11-02",
                    }
                ],
            )
        assert schema is BriefOutput
        return BriefOutput(
            blocks=[BriefBlock(text="Portal validation remains open.", reference_ids=[m["id"]])]
        )

    monkeypatch.setattr(Provider, "structured", generate)
    draft = client.post("/api/v1/meetings/" + m["id"] + "/recap").json()
    assert draft["mode"] == "live_model"
    result = client.post(
        "/api/v1/meetings/" + m["id"] + "/confirm-recap",
        json={"expected_version": 1, "draft_id": draft["id"], "recap": draft["recap"]},
    )
    assert result.status_code == 200, result.text
    assert len(result.json()["actions"]) == 1
    brief = client.post("/api/v1/meetings/" + m["id"] + "/brief", json={"recipient_id": "person:dev"})
    assert brief.status_code == 200 and brief.json()["mode"] == "live_model"
    assert m["id"] in brief.json()["references"]
    assert (
        client.post(
            "/api/v1/meetings/" + m["id"] + "/confirm-recap",
            json={"expected_version": 1, "recap": draft["recap"]},
        ).status_code
        == 409
    )


def test_provider_failures_keep_notes_and_show_manual_context(world, monkeypatch):
    _, _, _, client = world
    login(client)
    m = create(client)

    def fail(*args, **kwargs):
        raise TimeoutError("private-provider-secret-must-not-leak")

    monkeypatch.setattr(Provider, "structured", fail)
    response = client.post("/api/v1/meetings/" + m["id"] + "/recap")
    assert response.status_code == 503
    assert "secret" not in response.text
    assert client.get("/api/v1/meetings/" + m["id"]).json()["meeting"]["notes"] == m["notes"]
    brief = client.post("/api/v1/meetings/" + m["id"] + "/brief", json={"recipient_id": "person:dev"}).json()
    assert brief["mode"] == "manual_context" and brief["warning"]


def test_knowledge_access_revocation_hides_saved_context(world):
    repo, _, _, client = world
    login(client, "Lead")
    m = create(client)
    result = client.post(
        "/api/v1/meetings/" + m["id"] + "/confirm-recap",
        json={
            "expected_version": 1,
            "recap": {
                "summary": "Review identity operations",
                "decisions": [],
                "actions": [],
                "knowledge_source_ids": ["doc:identity-runbook"],
            },
        },
    )
    assert result.status_code == 200, result.text
    source = repo.source("doc:identity-runbook")
    client.patch(
        "/api/v1/sources/doc:identity-runbook/access",
        json={"expected_revision_id": source["active_revision_id"], "acl_groups": ["leadership"]},
    )
    login(client)
    assert client.get("/api/v1/meetings/" + m["id"]).status_code == 409
    assert all(x["id"] != m["id"] for x in client.get("/api/v1/meetings").json())


def test_request_ids_and_log_file(world):
    from app.config import settings

    _, _, _, client = world
    login(client)
    response = client.get("/api/v1/meetings")
    correlation = response.headers["x-request-id"]
    rows = [json.loads(line) for line in open(settings.log_path).read().splitlines()]
    assert any(r["request_id"] == correlation and r["event"] == "request_completed" for r in rows)
    assert all("level" in r and "timestamp" in r for r in rows)


def test_notes_versions_invalidate_ai_drafts_and_remain_after_confirmation(world, monkeypatch):
    _, _, _, client = world
    login(client)
    m = create(client)
    monkeypatch.setattr(
        Provider,
        "structured",
        lambda self, schema, prompt, data: Recap(summary="Client acceptance gates release."),
    )
    draft = client.post("/api/v1/meetings/" + m["id"] + "/recap").json()
    notes = client.patch(
        "/api/v1/meetings/" + m["id"] + "/notes",
        json={"expected_version": 1, "notes": m["notes"] + "\nNew client context."},
    )
    assert notes.status_code == 200
    assert (
        client.post(
            "/api/v1/meetings/" + m["id"] + "/confirm-recap",
            json={"expected_version": 2, "draft_id": draft["id"], "recap": draft["recap"]},
        ).status_code
        == 409
    )
    m["version"] = 2
    detail = confirm(client, m)
    assert (
        client.patch(
            "/api/v1/meetings/" + m["id"] + "/notes",
            json={"expected_version": detail["meeting"]["version"], "notes": "Replace evidence"},
        ).status_code
        == 409
    )
    action = detail["actions"][0]
    updated = client.patch(
        "/api/v1/actions/" + action["id"],
        json={
            "expected_version": action["version"],
            "owner_id": "person:dev",
            "status": "done",
            "outcome": "Validation accepted.",
        },
    ).json()
    assert [h["event"] for h in updated["history"][-2:]] == ["action_reassigned", "action_closed"]


def test_rejected_requests_have_correlated_errors(world):
    _, _, _, client = world
    response = client.post("/api/v1/meetings", json=payload(), headers={"origin": "https://wrong.example"})
    assert response.status_code == 403
    assert response.headers["x-request-id"] == response.json()["error"]["request_id"]


def test_followup_brief_includes_authorized_previous_decisions(world, monkeypatch):
    _, _, _, client = world
    login(client)
    parent = create(client)
    action = confirm(client, parent)["actions"][0]
    follow = create(
        client,
        previous_meeting_id=parent["id"],
        carry_action_ids=[action["id"]],
        notes="Review outstanding work.",
    )

    def generate(self, schema, prompt, data):
        assert parent["id"] in data["references"]
        assert "Decision: require client acceptance." in data["references"][parent["id"]]
        return BriefOutput(
            blocks=[
                BriefBlock(
                    text="Client acceptance was required in the prior session.", reference_ids=[parent["id"]]
                )
            ]
        )

    monkeypatch.setattr(Provider, "structured", generate)
    brief = client.post(
        "/api/v1/meetings/" + follow["id"] + "/brief", json={"recipient_id": "person:dev"}
    ).json()
    assert brief["mode"] == "live_model" and parent["id"] in brief["references"]
