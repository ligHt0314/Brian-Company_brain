"""Build DigiPlus Services's reproducible, entirely fictional IT services company.
Reviewed fixture claims are anchored to exact readable passages, never canned answers.
Run this script to regenerate JSON records, manifest, human-readable handbook and UI guide.
"""

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from build_workflows import build

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures/digiplus"
BASE_ENTITIES = [
    {
        "id": "project:atlas-portal",
        "kind": "Project",
        "label": "Atlas Client Portal",
        "aliases": ["Portal Launch", "portal launch", "Launch"],
    },
    {
        "id": "project:client-insights",
        "kind": "Project",
        "label": "Client Insights",
        "aliases": ["Dashboard", "Launch"],
    },
    {
        "id": "project:delivery-operations",
        "kind": "Project",
        "label": "Delivery Operations",
        "aliases": ["Delivery"],
    },
    {"id": "service:portal", "kind": "Service", "label": "Portal API", "aliases": []},
    {
        "id": "service:identity",
        "kind": "Service",
        "label": "Identity Gateway",
        "aliases": ["Platform Engineering"],
    },
    {"id": "service:reporting", "kind": "Service", "label": "Analytics API", "aliases": []},
    {"id": "service:messages", "kind": "Service", "label": "Notification Service", "aliases": []},
    {"id": "team:platform", "kind": "Team", "label": "Platform Engineering", "aliases": []},
    {"id": "team:integrations", "kind": "Team", "label": "Integrations", "aliases": []},
    {"id": "team:data", "kind": "Team", "label": "Data Systems", "aliases": []},
    {"id": "person:maya", "kind": "Person", "label": "Maya Rao", "aliases": ["Maya"]},
    {"id": "person:dev", "kind": "Person", "label": "Dev Shah", "aliases": ["Dev"]},
    {"id": "person:leah", "kind": "Person", "label": "Leah Chen", "aliases": ["Leah"]},
    {"id": "person:omar", "kind": "Person", "label": "Omar Ali", "aliases": ["Omar"]},
    {"id": "person:nina", "kind": "Person", "label": "Nina Park", "aliases": ["Nina"]},
    {"id": "person:eli", "kind": "Person", "label": "Eli Morgan", "aliases": ["Eli"]},
    {
        "id": "customer:northstar",
        "kind": "Customer",
        "label": "Northstar Logistics",
        "aliases": ["Northstar"],
    },
    {"id": "customer:cedar", "kind": "Customer", "label": "Cedar Health", "aliases": []},
    {"id": "ticket:T-101", "kind": "Ticket", "label": "T-101", "aliases": []},
    {"id": "ticket:T-102", "kind": "Ticket", "label": "T-102", "aliases": []},
    {"id": "ticket:T-103", "kind": "Ticket", "label": "T-103", "aliases": []},
    {"id": "ticket:T-104", "kind": "Ticket", "label": "T-104", "aliases": []},
    {"id": "ticket:T-105", "kind": "Ticket", "label": "T-105", "aliases": []},
    {"id": "ticket:T-106", "kind": "Ticket", "label": "T-106", "aliases": []},
    {"id": "ticket:T-107", "kind": "Ticket", "label": "T-107", "aliases": []},
    {"id": "ticket:T-108", "kind": "Ticket", "label": "T-108", "aliases": []},
    {"id": "decision:D-101", "kind": "Decision", "label": "D-101", "aliases": []},
    {"id": "decision:D-102", "kind": "Decision", "label": "D-102", "aliases": []},
    {"id": "decision:D-103", "kind": "Decision", "label": "D-103", "aliases": []},
    {"id": "decision:D-104", "kind": "Decision", "label": "D-104", "aliases": []},
    {"id": "commitment:C-101", "kind": "Commitment", "label": "C-101", "aliases": []},
    {"id": "commitment:C-102", "kind": "Commitment", "label": "C-102", "aliases": []},
    {"id": "commitment:C-103", "kind": "Commitment", "label": "C-103", "aliases": []},
]
CORE = [
    [
        "directory:digiplus",
        "directory",
        "DigiPlus Services · team directory",
        ["all_employees"],
        "2026-10-14T04:00:00Z",
        "Synthetic organization directory. All registry names and aliases are shared with employees.",
        [
            [
                "person:maya",
                "MEMBER_OF",
                "team:platform",
                None,
                "Maya Rao is a member of Platform Engineering.",
            ],
            ["person:dev", "MEMBER_OF", "team:integrations", None, "Dev Shah is a member of Integrations."],
            [
                "person:leah",
                "MEMBER_OF",
                "team:platform",
                None,
                "Leah Chen is a member of Platform Engineering.",
            ],
            ["person:omar", "MEMBER_OF", "team:data", None, "Omar Ali is a member of Data Systems."],
            ["person:nina", "MEMBER_OF", "team:integrations", None, "Nina Park is a member of Integrations."],
            ["person:eli", "MEMBER_OF", "team:data", None, "Eli Morgan is a member of Data Systems."],
        ],
    ],
    [
        "doc:portal-architecture",
        "document",
        "Atlas Client Portal · architecture",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "Identity verification relies on verified client identities. Dependency changes require a release review.",
        [
            [
                "project:atlas-portal",
                "USES",
                "service:portal",
                None,
                "Atlas Client Portal uses Portal API.",
            ],
            [
                "service:portal",
                "DEPENDS_ON",
                "service:identity",
                None,
                "Portal API depends on Identity Gateway.",
            ],
            [
                "service:portal",
                "OWNED_BY",
                "team:platform",
                None,
                "Portal API has primary owner Platform Engineering.",
            ],
            ["person:maya", "WORKED_ON", "service:portal", None, "Maya Rao worked on Portal API."],
            [
                "person:leah",
                "WORKED_ON",
                "project:atlas-portal",
                None,
                "Leah Chen worked on Atlas Client Portal.",
            ],
        ],
    ],
    [
        "doc:identity-runbook",
        "document",
        "Identity Gateway · operational runbook",
        ["engineering"],
        "2026-08-20T04:00:00Z",
        "Runbook from the previous operating cycle. Confirm ownership before paging a team.",
        [
            [
                "service:identity",
                "OWNED_BY",
                "team:platform",
                None,
                "Identity Gateway has primary owner Platform Engineering.",
            ],
            ["person:maya", "WORKED_ON", "service:identity", None, "Maya Rao worked on Identity Gateway."],
        ],
    ],
    [
        "doc:northstar-rollout",
        "document",
        "Northstar Logistics · rollout commitment",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "The promised rollout includes identity verification. This is synthetic customer information.",
        [
            [
                "commitment:C-101",
                "REQUIRES",
                "project:atlas-portal",
                None,
                "C-101 requires Atlas Client Portal.",
            ],
            [
                "commitment:C-101",
                "MADE_TO",
                "customer:northstar",
                None,
                "C-101 is made to Northstar Logistics.",
            ],
            ["commitment:C-101", "DUE_ON", None, "2026-10-18", "C-101 is due on 2026-10-18."],
        ],
    ],
    [
        "doc:portal-brief",
        "document",
        "Atlas Client Portal · project brief",
        ["all_employees"],
        "2026-10-14T04:00:00Z",
        "Atlas Client Portal is the secure self-service platform for Northstar Logistics. Alias: Portal Launch. Its technical dependencies are "
        "documented in engineering records.",
        [
            [
                "person:leah",
                "WORKED_ON",
                "project:atlas-portal",
                None,
                "Leah Chen worked on Atlas Client Portal.",
            ]
        ],
    ],
    [
        "doc:dashboard-overview",
        "document",
        "Client Insights · project overview",
        ["all_employees"],
        "2026-10-14T04:00:00Z",
        "",
        [
            [
                "project:client-insights",
                "USES",
                "service:reporting",
                None,
                "Client Insights uses Analytics API.",
            ],
            [
                "service:reporting",
                "OWNED_BY",
                "team:data",
                None,
                "Analytics API has primary owner Data Systems.",
            ],
            [
                "commitment:C-102",
                "REQUIRES",
                "project:client-insights",
                None,
                "C-102 requires Client Insights.",
            ],
            [
                "commitment:C-102",
                "MADE_TO",
                "customer:cedar",
                None,
                "C-102 is made to Cedar Health.",
            ],
            ["commitment:C-102", "DUE_ON", None, "2026-10-30", "C-102 is due on 2026-10-30."],
        ],
    ],
    [
        "doc:leadership-note",
        "document",
        "Leadership · commercial planning",
        ["leadership"],
        "2026-10-14T04:00:00Z",
        "CONFIDENTIAL_DIGIPLUS_COPPER_731. Fictional leadership-only commercial planning marker.",
        [
            [
                "project:atlas-portal",
                "OWNED_BY",
                "person:leah",
                None,
                "Atlas Client Portal has primary owner Leah Chen.",
            ]
        ],
    ],
    [
        "chat:handoff",
        "chat",
        "Engineering handoff · Identity Gateway",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "Exported conversation, 14 October. The earlier runbook has not been reconciled with this handoff claim.",
        [
            [
                "service:identity",
                "OWNED_BY",
                "team:integrations",
                None,
                "Identity Gateway now has primary owner Integrations.",
            ],
            ["person:dev", "WORKED_ON", "service:identity", None, "Dev Shah worked on Identity Gateway."],
        ],
    ],
    [
        "chat:identity-help",
        "chat",
        "Identity Gateway · implementation help",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "Maya and Dev shared their implementation experience. Contribution is not formal ownership.",
        [
            ["person:maya", "WORKED_ON", "service:identity", None, "Maya Rao worked on Identity Gateway."],
            ["person:dev", "WORKED_ON", "service:identity", None, "Dev Shah worked on Identity Gateway."],
            ["person:nina", "WORKED_ON", "service:portal", None, "Nina Park worked on Portal API."],
        ],
    ],
    [
        "chat:portal-planning",
        "chat",
        "Portal Launch · release planning",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "Planning discussion: investigate dependencies and the customer promise before release review.",
        [
            [
                "person:leah",
                "WORKED_ON",
                "project:atlas-portal",
                None,
                "Leah Chen worked on Atlas Client Portal.",
            ],
            [
                "person:maya",
                "WORKED_ON",
                "project:atlas-portal",
                None,
                "Maya Rao worked on Atlas Client Portal.",
            ],
            ["person:dev", "WORKED_ON", "service:portal", None, "Dev Shah worked on Portal API."],
        ],
    ],
    [
        "chat:dashboard-planning",
        "chat",
        "Dashboard · planning notes",
        ["all_employees"],
        "2026-10-14T04:00:00Z",
        "",
        [
            [
                "person:omar",
                "WORKED_ON",
                "project:client-insights",
                None,
                "Omar Ali worked on Client Insights.",
            ],
            ["person:eli", "WORKED_ON", "service:reporting", None, "Eli Morgan worked on Analytics API."],
        ],
    ],
    [
        "chat:ambiguous-alias",
        "chat",
        "Shared Launch alias · naming discussion",
        ["all_employees"],
        "2026-10-14T04:00:00Z",
        "Both Atlas Client Portal and Client Insights are sometimes called Launch. Ask which project is intended.\n\n",
        [],
    ],
    [
        "ticket:T-101",
        "ticket",
        "T-101 · Identity verification check",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-101", "BLOCKS", "service:identity", None, "T-101 blocks Identity Gateway."],
            ["ticket:T-101", "STATUS", None, "blocked", "T-101 has status blocked."],
        ],
    ],
    [
        "ticket:T-102",
        "ticket",
        "T-102 · Portal smoke tests",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-102", "BLOCKS", "service:portal", None, "T-102 blocks Portal API."],
            ["ticket:T-102", "STATUS", None, "done", "T-102 has status done."],
        ],
    ],
    [
        "ticket:T-103",
        "ticket",
        "T-103 · Analytics backfill",
        ["all_employees"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-103", "BLOCKS", "service:reporting", None, "T-103 blocks Analytics API."],
            ["ticket:T-103", "STATUS", None, "open", "T-103 has status open."],
        ],
    ],
    [
        "ticket:T-104",
        "ticket",
        "T-104 · Notification delivery",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-104", "BLOCKS", "service:messages", None, "T-104 blocks Notification Service."],
            ["ticket:T-104", "STATUS", None, "in_progress", "T-104 has status in_progress."],
        ],
    ],
    [
        "ticket:T-105",
        "ticket",
        "T-105 · Retired identity policy cleanup",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-105", "BLOCKS", "service:identity", None, "T-105 blocks Identity Gateway."],
            ["ticket:T-105", "STATUS", None, "cancelled", "T-105 has status cancelled."],
        ],
    ],
    [
        "ticket:T-106",
        "ticket",
        "T-106 · Identity audit review",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-106", "BLOCKS", "service:identity", None, "T-106 blocks Identity Gateway."],
            ["ticket:T-106", "STATUS", None, "done", "T-106 has status done."],
            ["person:maya", "WORKED_ON", "ticket:T-106", None, "Maya Rao worked on T-106."],
            ["person:dev", "WORKED_ON", "ticket:T-106", None, "Dev Shah worked on T-106."],
        ],
    ],
    [
        "ticket:T-107",
        "ticket",
        "T-107 · Notification metrics",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [
            ["ticket:T-107", "BLOCKS", "service:messages", None, "T-107 blocks Notification Service."],
            ["ticket:T-107", "STATUS", None, "done", "T-107 has status done."],
        ],
    ],
    [
        "ticket:T-108",
        "ticket",
        "T-108 · Untriaged delivery check",
        ["engineering"],
        "2026-10-17T03:30:00Z",
        "",
        [["ticket:T-108", "BLOCKS", "service:messages", None, "T-108 blocks Notification Service."]],
    ],
    [
        "decision:D-101",
        "decision",
        "D-101 · Identity verification requirement",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "",
        [
            [
                "decision:D-101",
                "ABOUT",
                "project:atlas-portal",
                None,
                "D-101 is about Atlas Client Portal: identity verification is required; unverified identities are ruled out because Northstar Logistics requires verified identity before client access is granted for the promised rollout.",
            ]
        ],
    ],
    [
        "decision:D-102",
        "decision",
        "D-102 · Portal identity validation",
        ["engineering"],
        "2026-10-14T04:00:00Z",
        "",
        [
            [
                "decision:D-102",
                "ABOUT",
                "service:portal",
                None,
                "D-102 is about Portal API: validate identity before issuing an access confirmation.",
            ]
        ],
    ],
    [
        "decision:D-103",
        "decision",
        "D-103 · Analytics backfill",
        ["all_employees"],
        "2026-10-14T04:00:00Z",
        "",
        [
            [
                "decision:D-103",
                "ABOUT",
                "project:client-insights",
                None,
                "D-103 is about Client Insights: complete the backfill before the analytics review.",
            ]
        ],
    ],
    [
        "decision:D-104",
        "decision",
        "D-104 · Identity audit trail",
        ["engineering"],
        "2026-06-01T04:00:00Z",
        "",
        [
            [
                "decision:D-104",
                "ABOUT",
                "service:identity",
                None,
                "D-104 is about Identity Gateway: keep an identity audit trail for operational investigation.",
            ]
        ],
    ],
]
entities = list(BASE_ENTITIES)
sources = []


def entity(id, kind, label, aliases=()):
    entities.append(dict(id=id, kind=kind, label=label, aliases=list(aliases)))
    return id


projects = [e["id"] for e in entities if e["kind"] == "Project"]
for slug, label in [
    ("claims-automation", "Claims Automation"),
    ("infrastructure-alerts", "Infrastructure Alerts"),
    ("consultant-scheduling", "Consultant Scheduling"),
    ("client-success", "Client Success"),
    ("partner-workspace", "Partner Workspace"),
    ("service-desk-modernization", "Service Desk Modernization"),
    ("managed-cloud-migration", "Managed Cloud Migration"),
]:
    projects.append(entity("project:" + slug, "Project", label))
services = [e["id"] for e in entities if e["kind"] == "Service"]
for slug, label in [
    ("delivery-console", "Delivery Console"),
    ("workflow-engine", "Workflow Engine"),
    ("claims", "Claims API"),
    ("monitor", "Resource Monitor"),
    ("configuration", "Configuration Registry"),
    ("success", "Success Hub"),
    ("partner-api", "Partner API"),
    ("support", "Support Queue"),
    ("billing", "Billing API"),
    ("events", "Event Pipeline"),
    ("staffing", "Staffing Scheduler"),
    ("search", "Knowledge Search"),
]:
    services.append(entity("service:" + slug, "Service", label))
teams = [e["id"] for e in entities if e["kind"] == "Team"]
for slug, label in [
    ("delivery", "Delivery Operations"),
    ("applications", "Application Engineering"),
    ("client-support", "Client Support"),
    ("service-ops", "Service Operations"),
    ("reliability", "Site Reliability"),
]:
    teams.append(entity("team:" + slug, "Team", label))
people = [e["id"] for e in entities if e["kind"] == "Person"]
for name in [
    "Aarav Mehta",
    "Isha Patel",
    "Rohan Das",
    "Ananya Sen",
    "Kabir Khan",
    "Meera Nair",
    "Arjun Iyer",
    "Sara Thomas",
    "Vikram Joshi",
    "Diya Kapoor",
    "Neel Gupta",
    "Tara Bose",
    "Aditya Rao",
    "Zoya Malik",
    "Rehan Shah",
    "Anika Jain",
    "Kiran Menon",
    "Pooja Desai",
    "Amit Verma",
    "Sana Sheikh",
    "Raj Malhotra",
    "Nisha Reddy",
    "Varun Sethi",
    "Riya Bhat",
    "Yash Kulkarni",
    "Aditi Roy",
    "Manav Suri",
    "Simran Kaur",
    "Siddharth Pai",
    "Kavya Rao",
    "Ibrahim Noor",
    "Priya Dutta",
    "Harsh Arora",
    "Lina Fernandes",
]:
    people.append(entity("person:" + name.lower().replace(" ", "-"), "Person", name))
customers = [e["id"] for e in entities if e["kind"] == "Customer"]
for slug, label in [
    ("sunrise", "Summit Banking"),
    ("family", "Meridian Insurance"),
    ("city", "Harbor Telecom"),
    ("fresh", "Vertex Manufacturing"),
    ("happy", "Aster Education"),
    ("neighbour", "Cobalt Energy"),
    ("value", "Pioneer Travel"),
    ("organic", "Oakridge Media"),
]:
    customers.append(entity("customer:" + slug, "Customer", label))
for n in range(109, 161):
    entity(f"ticket:T-{n}", "Ticket", f"T-{n}")
for n in range(105, 125):
    entity(f"decision:D-{n}", "Decision", f"D-{n}")
for n in range(104, 113):
    entity(f"commitment:C-{n}", "Commitment", f"C-{n}")
labels = {e["id"]: e["label"] for e in entities}
verbs = {
    "USES": "uses",
    "DEPENDS_ON": "depends on",
    "BLOCKS": "blocks",
    "REQUIRES": "requires",
    "MADE_TO": "is made to",
    "OWNED_BY": "has primary owner",
    "MEMBER_OF": "is a member of",
    "WORKED_ON": "worked on",
    "ABOUT": "is about",
    "STATUS": "has status",
    "DUE_ON": "is due on",
}


def fact(s, p, o=None, scalar=None, text=None):
    return dict(
        subject_id=s,
        predicate=p,
        object_id=o,
        scalar=scalar,
        quote=text or f"{labels[s]} {verbs[p]} {labels.get(o, scalar)}.",
    )


def source(id, kind, title, facts, groups=("engineering",), updated="2026-10-16T04:00:00Z", intro=""):
    body = (intro + "\n\n" if intro else "") + "\n\n".join(f["quote"] for f in facts)
    claims = []
    pos = 0
    for f in facts:
        start = body.index(f["quote"], pos)
        pos = start + len(f["quote"])
        claims.append(dict(f, start=start, end=pos, scope="primary", extraction_score=1.0))
    sources.append(
        dict(
            envelope=dict(
                schema_version="1.0",
                source_id=id,
                kind=kind,
                title=title,
                source_updated_at=updated,
                acl_groups=list(groups),
                body=body,
            ),
            claims=claims,
        )
    )


for id, kind, title, groups, updated, intro, facts in CORE:
    source(
        id,
        kind,
        title,
        [fact(s, p, o, scalar, quote) for s, p, o, scalar, quote in facts],
        groups,
        updated,
        intro,
    )
# Rewrite the canonical decision into ordinary service-delivery language, preserving exact quoted provenance.
for record in list(sources):
    if record["envelope"]["source_id"] == "decision:D-101":
        sources.remove(record)
        source(
            "decision:D-101",
            "decision",
            "D-101 · Verify identity before granting client access",
            [
                fact(
                    "decision:D-101",
                    "ABOUT",
                    projects[0],
                    text="D-101 is about Atlas Client Portal: unverified identities are ruled out because Northstar Logistics requires verified identity before client access is granted. This prevents client users seeing an access confirmation when the identity provider has not verified the account.",
                )
            ],
        )
        break
uses = dict(
    zip(
        projects,
        [
            services[0],
            services[2],
            "service:delivery-console",
            "service:claims",
            "service:monitor",
            "service:staffing",
            "service:success",
            "service:partner-api",
            "service:support",
            "service:billing",
        ],
    )
)
dependencies = {
    "service:portal": "service:identity",
    "service:delivery-console": "service:workflow-engine",
    "service:workflow-engine": "service:events",
    "service:claims": "service:identity",
    "service:monitor": "service:configuration",
    "service:staffing": "service:monitor",
    "service:success": "service:messages",
    "service:partner-api": "service:configuration",
    "service:support": "service:messages",
    "service:billing": "service:identity",
    "service:reporting": "service:events",
    "service:search": "service:configuration",
}
explain = dict(
    zip(
        services,
        [
            "the API serving client portal requests",
            "the shared identity verification gateway",
            "the service producing client delivery reports",
            "the system delivering incident and project notifications",
            "the console tracking client delivery milestones",
            "the engine coordinating approval workflows",
            "the API processing insurance claims",
            "the system monitoring infrastructure capacity",
            "the registry of deployed applications and configuration",
            "the hub tracking client success follow-ups",
            "the API used by delivery partners",
            "the queue for client support requests",
            "the service managing client invoicing",
            "the pipeline carrying operational events",
            "the scheduler allocating consultants",
            "the search service for team knowledge",
        ],
    )
)
project_summary = [
    "Deliver a secure self-service portal for Northstar Logistics.",
    "Give Cedar Health a consolidated view of delivery metrics.",
    "Coordinate application delivery milestones for Summit Banking.",
    "Automate claims workflows for Meridian Insurance.",
    "Monitor production capacity for Harbor Telecom.",
    "Schedule consulting teams for Vertex Manufacturing.",
    "Coordinate client success follow-ups for Aster Education.",
    "Deliver a partner workspace for Cobalt Energy.",
    "Modernize the support desk for Pioneer Travel.",
    "Migrate Oakridge Media to managed cloud operations.",
]
for i, p in enumerate(projects[3:], 3):
    source(
        "doc:" + p.split(":")[1] + "-brief",
        "document",
        labels[p] + " · plain-language project brief",
        [fact(people[6 + i], "WORKED_ON", p)],
        ("all_employees",),
        intro=project_summary[i] + " This project is part of the fictional DigiPlus Services demonstration.",
    )
    facts = [fact(p, "USES", uses[p])]
    if uses[p] in dependencies:
        facts.append(fact(uses[p], "DEPENDS_ON", dependencies[uses[p]]))
    source(
        "doc:" + p.split(":")[1] + "-plan",
        "document",
        labels[p] + " · delivery plan",
        facts,
        intro="Business purpose: "
        + project_summary[i]
        + " The facts below show which systems the project needs.",
    )
for i, s in enumerate(services[4:], 4):
    facts = [fact(s, "OWNED_BY", teams[i % 8])]
    if s in dependencies:
        facts.append(fact(s, "DEPENDS_ON", dependencies[s]))
    source(
        "doc:" + s.split(":")[1] + "-runbook",
        "document",
        labels[s] + " · working guide",
        facts,
        intro=labels[s]
        + " means "
        + explain[s]
        + ". An owner is the team responsible for keeping this system working.",
    )
for i, s in enumerate(services):
    facts = [fact(people[(i + 12) % 40], "WORKED_ON", s)]
    # A documented collaboration is not another ownership claim.
    source(
        "chat:" + s.split(":")[1] + "-weekly",
        "chat",
        labels[s] + " · weekly handover",
        facts,
        intro="Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.",
    )
for i, p in enumerate(people):
    # Keep canonical contributors scoped to their existing work; add credible independent project history.
    s = services[4 + i % 12]
    source(
        "doc:work-" + p.split(":")[1],
        "document",
        labels[p] + " · contribution notes",
        [fact(p, "WORKED_ON", s), fact(p, "WORKED_ON", projects[2 + i % 8])],
        intro="A record of work performed, not a claim about seniority, availability or ownership. "
        + labels[s]
        + " is "
        + explain[s]
        + ".",
    )
issues = [
    "Milestone status stops updating",
    "Claim reference missing from partner response",
    "Capacity reading differs from monitoring baseline",
    "Consultant allocation can be double-booked",
    "Client follow-up created twice",
    "Configuration update arrives late",
    "Support request not assigned",
    "Client invoice reconciliation fails",
    "Approval workflow references a missing reviewer",
    "Operational event arrives out of order",
    "Knowledge search misses common terms",
    "Incident notification arrives late",
]
# Background tickets are relevant to other stories; they do not all block the portal launch.
targets = [
    "service:delivery-console",
    "service:claims",
    "service:monitor",
    "service:staffing",
    "service:success",
    "service:partner-api",
    "service:support",
    "service:billing",
    "service:workflow-engine",
    "service:events",
    "service:search",
    "service:messages",
]
statuses = [
    "blocked",
    "open",
    "in_progress",
    "done",
    "done",
    "cancelled",
    "done",
    "open",
    "done",
    "done",
    "in_progress",
    "done",
]
for i, n in enumerate(range(109, 161)):
    target = targets[i % 12]
    status = statuses[i % 12]
    source(
        f"ticket:T-{n}",
        "ticket",
        f"T-{n} · {issues[i % 12]} (check {i // 12 + 1})",
        [
            fact(f"ticket:T-{n}", "BLOCKS", target),
            fact(f"ticket:T-{n}", "STATUS", scalar=status),
            fact(people[(i + 6) % 40], "WORKED_ON", f"ticket:T-{n}"),
        ],
        intro="A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.",
        updated="2026-10-17T03:30:00Z",
    )
rationales = [
    ("Show the last milestone update time", "so clients know when delivery information may be stale"),
    ("Keep a partner claim reference", "so support can trace the original claim"),
    ("Check capacity before assigning consultants", "so delivery teams avoid over-allocation"),
    ("Use one acceptance record per release", "so retries cannot record duplicate approval"),
    ("Explain failed invoice reconciliation", "so finance can resolve a mismatch without duplicate billing"),
    ("Keep configuration change history", "so the incoming engineer can explain the deployed state"),
    ("Send one notification per incident event", "so retries do not duplicate alerts"),
    ("Require human review of disputed closure", "so missing evidence cannot silently close an action"),
]
for i, n in enumerate(range(105, 125)):
    p = projects[2 + i % 8]
    title, why = rationales[i % 8]
    source(
        f"decision:D-{n}",
        "decision",
        f"D-{n} · {title}",
        [fact(f"decision:D-{n}", "ABOUT", p, text=f"D-{n} is about {labels[p]}: {title.lower()} {why}.")],
        intro="A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.",
    )
for i, n in enumerate(range(104, 113)):
    p = projects[1 + i % 9]
    customer = customers[1 + i % 9]
    source(
        f"doc:promise-C-{n}",
        "document",
        labels[customer] + " · " + labels[p] + " promise",
        [
            fact(f"commitment:C-{n}", "REQUIRES", p),
            fact(f"commitment:C-{n}", "MADE_TO", customer),
            fact(f"commitment:C-{n}", "DUE_ON", scalar=f"2026-10-{20 + i:02}"),
        ],
        intro="A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.",
    )
for i, t in enumerate(teams):
    source(
        "doc:team-" + t.split(":")[1],
        "document",
        labels[t] + " · team handbook",
        [fact(people[i], "MEMBER_OF", t)],
        ("all_employees",),
        intro="Fictional team guide. Read the directory for the full team membership; read system working guides for ownership evidence.",
    )
for i in range(3):
    source(
        f"doc:leadership-{i + 1}",
        "document",
        f"Leadership · internal planning note {i + 1}",
        [],
        ("leadership",),
        intro=f"CONFIDENTIAL_DIGIPLUS_PRIVATE_{i + 1}. Fictional leadership planning note, intentionally restricted for the permission demonstration. No real commercial information is present.",
    )
source(
    "doc:delivery-story",
    "document",
    "Delivery Operations · how the delivery chain works",
    [
        fact(projects[2], "USES", "service:delivery-console"),
        fact("service:delivery-console", "DEPENDS_ON", "service:workflow-engine"),
    ],
    intro="A delivery manager reviews a client milestone. Delivery Operations uses the Delivery Console and its Workflow Engine approval chain. Follow the evidence to see which releases a missing approval could affect.",
)
source(
    "doc:demo-welcome",
    "document",
    "Start here · the DigiPlus Services story",
    [],
    ("all_employees",),
    intro="DigiPlus Services is a fictional IT consulting and managed services company. Start with Atlas Client Portal: an identity verification check is blocked, two teams disagree about the Identity Gateway owner, and Northstar Logistics has a rollout promise. Other projects cover client delivery, claims, infrastructure, consultant staffing, partner services and reports. All people and records are invented. The demonstration guide explains the questions to ask; the agent answers from indexed evidence, not this guide.",
)

# The first six memberships must keep Maya/Leah on Platform Engineering, Dev/Nina on Integrations.
assignments = {
    people[0]: teams[0],
    people[1]: teams[1],
    people[2]: teams[0],
    people[3]: teams[2],
    people[4]: teams[1],
    people[5]: teams[2],
}
for rec in sources:
    if rec["envelope"]["source_id"] == "directory:digiplus":
        sources.remove(rec)
        break
source(
    "directory:digiplus",
    "directory",
    "DigiPlus Services · team directory",
    [fact(p, "MEMBER_OF", assignments.get(p, teams[i % 8])) for i, p in enumerate(people)],
    ("all_employees",),
    intro="Forty invented employees help ten fictional enterprise clients deliver software and managed services. Team membership identifies colleagues, not service ownership.",
)
# Team handbooks carry no conflicting membership facts.
for rec in sources:
    if rec["envelope"]["source_id"].startswith("doc:team-"):
        rec["claims"] = []
        rec["envelope"]["body"] = (
            "DigiPlus Services fictional team handbook. "
            + rec["envelope"]["title"].split(" · ")[0]
            + " works with the other teams to deliver client projects and managed support. The shared directory records actual team membership in this demonstration."
        )

assert len(sources) == 200, len(sources)
assert len(entities) == 180, len(entities)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "registry.json").write_text(json.dumps(entities, indent=2) + "\n")
manifest = []
for rec in sources:
    path = rec["envelope"]["source_id"].replace(":", "_") + ".json"
    raw = json.dumps(rec, indent=2) + "\n"
    (OUT / path).write_text(raw)
    manifest.append(
        dict(source_id=rec["envelope"]["source_id"], path=path, sha256=sha256(raw.encode()).hexdigest())
    )
counts = dict(Counter(e["kind"] for e in entities))
claim_count = sum(len(r["claims"]) for r in sources)
summary = dict(
    company="DigiPlus Services",
    seed_version="2.0",
    scenario_clock="2026-10-17T04:30:00Z",
    synthetic=True,
    entity_counts=counts,
    source_count=len(sources),
    claim_count=claim_count,
    source_counts=dict(Counter(r["envelope"]["kind"] for r in sources)),
)
(OUT / "manifest.json").write_text(json.dumps(dict(summary, sources=manifest), indent=2) + "\n")
# Every record is readable without opening JSON; claim quotations remain identical.
handbook = [
    "# DigiPlus Services source book",
    "All people, clients and records below are fictional. Generated from the exact imported source bodies.",
    "",
]
for rec in sources:
    env = rec["envelope"]
    handbook.extend(
        [
            f"## {env['title']}",
            f"Record: {env['source_id']} · Access: {', '.join(env['acl_groups'])} · Updated: {env['source_updated_at']}",
            "",
            env["body"],
            "",
        ]
    )
# Documentation is optional; dataset regeneration must also work without docs/.
if (ROOT / "docs").is_dir():
    (ROOT / "docs/DigiPlus Services-Sourcebook.md").write_text("\n\n".join(handbook) + "\n")
(ROOT / "apps/web/lib/workspace-catalog.json").write_text(
    json.dumps(
        dict(
            summary,
            projects=[
                dict(
                    id=p,
                    name=labels[p],
                    purpose=project_summary[i],
                    question=f"What could block {labels[p]}?",
                    system=labels[uses[p]],
                )
                for i, p in enumerate(projects)
            ],
            glossary=[dict(name=labels[s], meaning=explain[s]) for s in services],
        ),
        indent=2,
    )
    + "\n"
)
print(json.dumps(summary, indent=2))


build(ROOT)
