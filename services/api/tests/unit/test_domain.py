import pytest
from pydantic import ValidationError
from app.domain.models import Candidate, SourceEnvelope
from app.ingestion.service import chunks, validate_candidates, registry


def candidate(**kw):
    return Candidate(
        subject_id="ticket:T-101", predicate="STATUS", scalar="blocked", quote="blocked", start=0, end=7, **kw
    )


def test_exact_unicode_spans():
    body = "🙂 Maya Rao worked on Identity Gateway."
    quote = "Maya Rao worked on Identity Gateway."
    c = Candidate(
        subject_id="person:maya",
        predicate="WORKED_ON",
        object_id="service:identity",
        quote=quote,
        start=2,
        end=len(body),
    )
    validate_candidates(body, [c], registry())
    with pytest.raises(ValueError):
        validate_candidates(body, [c.model_copy(update={"start": 1})], registry())


def test_predicate_types_and_scalar_rules():
    with pytest.raises(ValidationError):
        candidate(object_id="team:platform")
    with pytest.raises(ValidationError):
        Candidate(
            subject_id="ticket:T-101", predicate="STATUS", scalar="ready", quote="ready", start=0, end=5
        )
    c = Candidate(
        subject_id="person:maya",
        predicate="USES",
        object_id="service:identity",
        quote="uses",
        start=0,
        end=4,
    )
    with pytest.raises(ValueError):
        validate_candidates("uses", [c], registry())


def test_mutation_fields_and_timestamps():
    values = dict(
        source_id="doc:test",
        kind="document",
        title="Test",
        source_updated_at="2026-10-17T00:00:00Z",
        acl_groups=["engineering"],
        body="",
    )
    with pytest.raises(ValidationError):
        SourceEnvelope(**values, groups=["leadership"])
    values["source_updated_at"] = "2026-10-17T00:00:00"
    with pytest.raises(ValidationError):
        SourceEnvelope(**values)


def test_chunk_bounds_and_overlap():
    text = "x" * 5000
    parts = chunks(text)
    assert all(len(p) <= 2500 and text[a:b] == p for a, b, p in parts)
    assert parts[0][0] == 0 and parts[-1][1] == len(text)
    assert all(parts[i + 1][0] < parts[i][1] for i in range(len(parts) - 1))


def test_alias_resolution_prefers_unique_name():
    from app.domain.models import Entity
    from app.reasoning.investigate import resolve

    entities = [Entity.model_validate(e) for e in registry()]
    assert [e.id for e in resolve("Investigate launch risks for Portal Launch", entities)] == [
        "project:atlas-portal"
    ]
    assert sorted(e.id for e in resolve("What could block Launch?", entities)) == [
        "project:atlas-portal",
        "project:client-insights",
    ]


def test_model_schema_repair_is_bounded(monkeypatch):
    from app.agent.provider import Provider
    from app.domain.models import Plan
    from app.config import settings
    import app.agent.provider as provider_module

    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_model", "test-model")
    calls = []

    class Result:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "invalid-json"}}]}

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def post(self, *args, **kwargs):
            calls.append(kwargs)
            return Result()

    monkeypatch.setattr(provider_module.httpx, "Client", Client)
    with pytest.raises(ValueError, match="schema validation"):
        Provider().structured(Plan, "Test only", {})
    assert len(calls) == 2


def test_model_offsets_are_anchored_only_to_unique_exact_quotes(monkeypatch):
    from app.agent.provider import Provider
    from app.domain.models import Extraction

    quote = "Maya Rao worked on Notification Service."
    body = "🙂 " + quote
    c = Candidate(
        subject_id="person:maya",
        predicate="WORKED_ON",
        object_id="service:messages",
        quote=quote,
        start=0,
        end=10,
    )
    provider = Provider()
    monkeypatch.setattr(provider, "structured", lambda *args: Extraction(claims=[c.model_copy()]))
    extracted = provider.extract(body, registry())
    assert extracted.claims[0].start == 2 and extracted.claims[0].end == len(body)
    validate_candidates(body, extracted.claims, registry())
    with pytest.raises(ValueError, match="exact, unambiguous"):
        provider.extract("This quote is absent.", registry())
    with pytest.raises(ValueError, match="exact, unambiguous"):
        provider.extract("x " + quote + " " + quote, registry())


def test_gemini_request_parameters_and_deadline(monkeypatch):
    from app.agent.provider import Provider
    from app.config import settings
    import app.agent.provider as provider_module
    import time

    monkeypatch.setattr(settings, "llm_api_key", "unit-key")
    monkeypatch.setattr(settings, "llm_model", "gemini-3.1-flash-lite")
    monkeypatch.setattr(settings, "llm_base_url", "https://generativelanguage.googleapis.com/v1beta/openai")
    captured = []

    class Result:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {"message": {"content": '{"intent":"release_risk","entity_id":"project:atlas-portal"}'}}
                ]
            }

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def post(self, *args, **kwargs):
            captured.append(kwargs["json"])
            return Result()

    monkeypatch.setattr(provider_module.httpx, "Client", Client)
    assert Provider().plan("What could block Portal Launch?", registry()).intent == "release_risk"
    assert captured[0]["temperature"] == 1 and captured[0]["reasoning_effort"] == "minimal"
    assert captured[0]["max_completion_tokens"] == 4096
    with pytest.raises(TimeoutError, match="deadline"):
        Provider(deadline=time.monotonic() - 1).plan("Test", registry())
    assert len(captured) == 1
