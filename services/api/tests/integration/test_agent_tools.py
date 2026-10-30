import pytest
from pydantic import ValidationError
from app.agent.tools import ReadTools, ToolCall, ToolArguments, ToolDecision, KnowledgeChanged
from app.domain.models import Entity, Plan
from app.ingestion.service import registry
from app.reasoning.investigate import Investigator
from app.agent.provider import Synthesis


def call(tool_name, **args):
    return ToolCall(name=tool_name, arguments=ToolArguments(**args))


def test_tool_inputs_reject_commands_unknown_fields_and_excess_hops():
    with pytest.raises(ValidationError):
        ToolCall.model_validate({"name": "execute_cypher", "arguments": {"query": "MATCH (n) DELETE n"}})
    with pytest.raises(ValidationError):
        ToolCall.model_validate(
            {
                "name": "find_ownership",
                "arguments": {"entity_id": "service:identity", "url": "https://example.com"},
            }
        )
    with pytest.raises(ValidationError):
        call("trace_dependencies", entity_id="project:atlas-portal", max_business_hops=4)
    with pytest.raises(ValidationError):
        call("find_ownership", entity_id="service:identity", query="extra")


def test_read_tools_real_graph_scope_budgets_and_epoch(world):
    repo, store, ingest, client = world
    root = Entity.model_validate(next(e for e in registry() if e["id"] == "project:atlas-portal"))
    tools = ReadTools(repo, ["all_employees", "engineering"], repo.epoch(), root)
    with pytest.raises(ValueError, match="observed"):
        tools.execute(call("find_ownership", entity_id="service:identity"), 1)
    tools.execute(call("resolve_entity", name="Atlas Client Portal"), 0)
    context = tools.execute(call("get_project_context", entity_id=root.id), 1)
    paths = tools.execute(call("trace_dependencies", entity_id=root.id, max_business_hops=3), 1)
    assert {"service:portal", "service:identity"} <= set(paths.entity_ids)
    blockers = tools.execute(
        call("find_blockers", entity_ids=["project:atlas-portal", "service:portal", "service:identity"]),
        2,
    )
    assert any(c.predicate == "STATUS" and c.subject_id == "ticket:T-101" for c in blockers.claims)
    owners = tools.execute(call("find_ownership", entity_id="service:identity"), 2)
    assert {c.object_id for c in owners.claims if c.predicate == "OWNED_BY"} == {
        "team:platform",
        "team:integrations",
    }
    assert all(c.evidence.source_id != "doc:leadership-note" for r in tools.results for c in r.claims)
    assert any(c.predicate == "MADE_TO" for c in context.claims)
    tools.execute(call("find_ownership", entity_id="service:portal"), 2)
    with pytest.raises(ValueError, match="budget"):
        tools.execute(call("find_ownership", entity_id=root.id), 2)
    viewer = ReadTools(repo, ["all_employees"], repo.epoch(), root)
    result = viewer.execute(call("trace_dependencies", entity_id=root.id), 1)
    assert not result.claims
    changed = ReadTools(repo, ["all_employees", "engineering"], repo.epoch() - 1, root)
    with pytest.raises(KnowledgeChanged):
        changed.execute(call("resolve_entity", name="Atlas Client Portal"), 0)


def test_model_selects_two_rounds_from_actual_observations(world, monkeypatch):
    repo, store, ingest, client = world
    import app.reasoning.investigate as module

    observations = []

    class Model:
        enabled = True

        def __init__(self, **kw):
            self.calls = 0

        def plan(self, *args):
            self.calls += 1
            return Plan(intent="release_risk", entity_id="project:atlas-portal")

        def next_tools(self, q, intent, entity, results, remaining, round_number):
            self.calls += 1
            observations.append(results)
            if round_number == 1:
                return ToolDecision(
                    calls=[
                        call("get_project_context", entity_id=entity["id"]),
                        call("trace_dependencies", entity_id=entity["id"], max_business_hops=3),
                    ]
                )
            assert any("service:identity" in r["entity_ids"] for r in results)
            return ToolDecision(
                calls=[
                    call(
                        "find_blockers",
                        entity_ids=["project:atlas-portal", "service:portal", "service:identity"],
                    ),
                    call("find_ownership", entity_id="service:identity"),
                ],
                finish=True,
            )

        def synthesize(self, *args):
            self.calls += 1
            return Synthesis(blocks=[])

    monkeypatch.setattr(module, "Provider", Model)
    result = Investigator(repo).run(
        "test_agent", "What could block Atlas Client Portal?", ["all_employees", "engineering"]
    )
    assert (
        result.execution_mode == "live_model"
        and result.metrics.agent_tool_calls == 5
        and result.metrics.agent_rounds == 2
    )
    assert any(f.category == "blocker" for f in result.findings) and result.conflicts
    assert len(observations) == 2 and len(result.agent_trace) == 5
    assert "CONFIDENTIAL_DIGIPLUS" not in str(observations)


def test_incomplete_model_plan_falls_back_instead_of_claiming_no_blockers(world, monkeypatch):
    repo, store, ingest, client = world
    import app.reasoning.investigate as module

    class Model:
        enabled = True

        def __init__(self, **kw):
            self.calls = 0

        def plan(self, *args):
            self.calls += 1
            return Plan(intent="release_risk", entity_id="project:atlas-portal")

        def next_tools(self, *args):
            self.calls += 1
            return ToolDecision(
                calls=[call("get_project_context", entity_id="project:atlas-portal")], finish=True
            )

    monkeypatch.setattr(module, "Provider", Model)
    result = Investigator(repo).run(
        "test_fallback", "What could block Atlas Client Portal?", ["all_employees", "engineering"]
    )
    assert result.execution_mode == "deterministic"
    assert any(f.category == "blocker" for f in result.findings)
    assert any("tool selection unavailable" in w for w in result.scope.warnings)
