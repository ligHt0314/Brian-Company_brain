"""Reproducible service-delivery meetings and handovers, with exact note evidence."""

import json
from pathlib import Path


def build(root: Path):
    folder = root / "fixtures/digiplus"
    directory = json.loads((folder / "registry.json").read_text())
    people = [e for e in directory if e["kind"] == "Person"]
    projects = [e for e in directory if e["kind"] == "Project"]
    clients = [e for e in directory if e["kind"] == "Customer"]
    meetings, actions = [], []
    scenarios = [
        (
            "The client's identity sandbox rejects one tenant. The operational runbook names Platform Engineering, but the engineering handover names Integrations; ownership needs explicit resolution.",
            "Resolve Identity Gateway ownership before the client cutover.",
            [
                "Tenant mapping validation",
                "Ownership decision",
                "SSO regression report",
                "Client cutover approval",
            ],
        ),
        (
            "Two reporting feeds disagree on the definition of a completed delivery. The client missed the mapping workshop, so silence cannot be treated as acceptance.",
            "Keep both reconciliation results until the client signs the metric definition.",
            [
                "Metric definition sign-off",
                "Feed reconciliation",
                "Client workshop reschedule",
                "Report acceptance",
            ],
        ),
        (
            "The release approver is on leave during a client freeze. Workflow Engine and Event Pipeline are shared with reporting; a delayed event can affect more than one milestone.",
            "Require a named backup approver and preserve the release freeze.",
            [
                "Backup approver confirmation",
                "Event ordering validation",
                "Freeze exception review",
                "Release evidence pack",
            ],
        ),
        (
            "A claims partner changed its reference format. Operations needs a traceable reference and a human review path when a claim cannot be reconciled.",
            "Keep manual review for claims without a verifiable partner reference.",
            [
                "Partner reference contract",
                "Claims reconciliation",
                "Manual review runbook",
                "Acceptance test matrix",
            ],
        ),
        (
            "A noisy infrastructure alert paged two teams, while one capacity threshold never fired. Monitoring ownership and escalation coverage must be agreed before wider rollout.",
            "Deduplicate pages and test escalation with the incoming support engineer.",
            [
                "Alert deduplication",
                "Capacity threshold test",
                "Escalation coverage",
                "Monitoring acceptance",
            ],
        ),
        (
            "Two client projects requested the same consultant for overlapping dates. The staffing API also permits duplicate allocation on a retry.",
            "Reserve consultant capacity once and escalate conflicting client priorities.",
            [
                "Allocation conflict review",
                "Staffing idempotency test",
                "Client priority agreement",
                "Coverage schedule",
            ],
        ),
        (
            "Client success has three unanswered acceptance requests. A delivery handover must explain the missing decision and retain the original due date.",
            "Carry unanswered client approvals forward without silently extending the deadline.",
            [
                "Acceptance reminder draft",
                "Escalation owner confirmation",
                "Client feedback review",
                "Handover checklist",
            ],
        ),
        (
            "A partner still uses the previous API contract. Configuration Registry is shared with Infrastructure Alerts, so a contract change needs cross-team regression evidence.",
            "Run partner compatibility checks before retiring the previous contract.",
            [
                "Partner contract comparison",
                "Compatibility regression",
                "Shared registry impact review",
                "Partner release confirmation",
            ],
        ),
        (
            "The support transition includes commercially sensitive staffing commitments. The incoming lead needs the escalation matrix and outstanding acceptance disputes.",
            "Restrict the commercial handover and require closure evidence for disputed items.",
            [
                "Escalation matrix review",
                "Staffing commitment check",
                "Disputed closure review",
                "Support readiness decision",
            ],
        ),
        (
            "The cloud migration rehearsal restored the application but missed one access policy. Rollback ownership and post-migration support must be explicit.",
            "Repeat restore and identity-policy checks before the managed support handover.",
            [
                "Restore rehearsal",
                "Access policy verification",
                "Rollback ownership",
                "Managed support acceptance",
            ],
        ),
    ]
    previous = {}
    for i, project in enumerate(projects):
        team = [people[(i * 3 + j) % len(people)] for j in range(5)]
        client = clients[i]
        context, decision_text, topics = scenarios[i]
        shared = []
        for round_number, day in enumerate([18, 22, 26, 30]):
            key = f"meeting:{project['id'].split(':')[1]}:{round_number + 1}"
            at = f"2026-10-{day:02}T04:30:00+00:00"
            groups = ["leadership"] if i == 8 else ["all_employees"] if i == 9 else ["engineering"]
            kind = "handover" if round_number in {1, 3} else "meeting"
            phase = [
                "Kickoff and discovery",
                "Leave coverage handover",
                "Delivery checkpoint",
                "Client support transition",
            ][round_number]
            carry = [a for a in shared if a["status"] not in {"done", "cancelled"}][:2]
            m = {
                "id": key,
                "title": f"{project['label']} · {phase}",
                "kind": kind,
                "agenda": f"Review {client['label']} delivery milestones, unresolved actions, ownership and acceptance criteria.",
                "notes": "",
                "scheduled_at": at,
                "participant_ids": [p["id"] for p in team],
                "absent_ids": [team[0]["id"]] if round_number in {1, 2} else [],
                "project_id": project["id"],
                "acl_groups": groups,
                "previous_meeting_id": previous.get(project["id"]),
                "action_ids": [a["id"] for a in carry],
                "status": "planned" if round_number == 3 else "completed",
                "summary": "",
                "decisions": [],
                "knowledge_links": [],
                "version": 1,
                "created_at": at,
                "updated_at": at,
                "history": [{"at": at, "actor": "seed", "event": "meeting_created", "detail": phase}],
                "recap_confirmed": round_number < 2,
            }
            for a in carry:
                a["meeting_ids"].append(key)
                a["version"] += 1
                a["updated_at"] = at
                a["history"].append(
                    {"at": at, "actor": "seed", "event": "action_carried_forward", "detail": key}
                )
            if round_number < 3:
                intro = (
                    f"{project['label']} delivery session for {client['label']}. "
                    f"{team[0]['label']} is on leave; {team[1]['label']} is taking over coordination. "
                    + context
                    + " Preserve the evidence and escalate missing decisions."
                )
                decision = f"Decision: {decision_text}"
                quotes = []
                count = 4 if round_number < 2 else 2
                for j in range(count):
                    person = team[(j + 1) % len(team)]
                    due = f"2026-10-{min(31, day + 3 + j):02}" if round_number < 2 else f"2026-11-{j + 1:02}"
                    topic = topics[(j + round_number) % len(topics)]
                    quote = (
                        f"{person['label']} will complete {topic.lower()} for {project['label']} by {due}."
                    )
                    quotes.append(quote)
                    aid = f"action:{i + 1:02}:{round_number + 1}:{j + 1}"
                    status = (
                        ["done", "cancelled", "blocked", "open"][j]
                        if round_number == 0
                        else ["done", "in_progress", "open", "blocked"][j]
                        if round_number == 1
                        else ["open", "in_progress"][j]
                    )
                    outcome = (
                        "Client evidence and approval recorded in the release checklist."
                        if status == "done"
                        else "Client scope changed; replaced by the updated acceptance checklist."
                        if status == "cancelled"
                        else ""
                    )
                    a = {
                        "id": aid,
                        "title": f"{topic} · {project['label']}",
                        "owner_id": person["id"],
                        "due_date": due,
                        "status": status,
                        "outcome": outcome,
                        "version": 1,
                        "origin_meeting_id": key,
                        "meeting_ids": [key],
                        "quote": quote,
                        "created_at": at,
                        "updated_at": at,
                        "acl_groups": groups,
                        "history": [{"at": at, "actor": "seed", "event": "action_created", "detail": quote}],
                    }
                    if status in {"done", "cancelled"}:
                        a["history"].append(
                            {"at": at, "actor": "seed", "event": "action_closed", "detail": outcome}
                        )
                    if round_number == 1 and j == 1:
                        a["history"].append(
                            {
                                "at": at,
                                "actor": "seed",
                                "event": "action_reassigned",
                                "detail": f"Coverage transferred from {team[0]['label']} to {person['label']} during leave.",
                            }
                        )
                    actions.append(a)
                    shared.append(a)
                    m["action_ids"].append(aid)
                m["notes"] = "\n\n".join(
                    [
                        intro,
                        decision,
                        *quotes,
                        "Open work must be reviewed at the next checkpoint. Do not assume that a missed meeting means approval.",
                    ]
                )
                if m["recap_confirmed"]:
                    m["summary"] = f"{client['label']}: {context} Decision: {decision_text}"
                    m["decisions"] = [
                        {
                            "text": decision_text,
                            "quote": decision,
                        }
                    ]
            previous[project["id"]] = key
            meetings.append(m)
    assert len(meetings) == 40 and len(actions) == 100
    (folder / "workflows.json").write_text(
        json.dumps({"meeting": meetings, "action": actions}, indent=2) + "\n"
    )
    (folder / "README.md").write_text("""# DigiPlus Services dataset

A fictional IT consulting and managed-services company, independent of any real DigiPlus organization.

- 40 people, 8 teams, 10 enterprise clients and 10 delivery projects.
- 16 shared systems, 60 tickets, 24 decisions and 12 commitments.
- 200 knowledge sources with 432 exact-span assertions.
- 40 connected meetings/handovers and 100 distinct action items, including repeated appearances of the same items in follow-ups.
- Missed meetings, leave coverage, overdue work, completed/cancelled outcomes and leadership-only context.

`registry.json` is the shared directory. `manifest.json` checksums the knowledge sources. `workflows.json` contains canonical seed meeting/action records and their exact note quotations. These are input records, not canned AI answers. New recaps and catch-up briefs use the configured provider and expose failures.

Regenerate with `python3 scripts/build_fixtures.py`. Startup only inserts missing records; it preserves your edits. See the root README for setup and the guided scenario. Keep this folder: it is needed at startup and runtime. Never add credentials or real client exports without review.
""")
    from hashlib import sha256

    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(
        meeting_count=40,
        action_count=100,
        workflow_sha256=sha256((folder / "workflows.json").read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print("Generated 40 meetings/handovers and 100 persistent action items.")


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
