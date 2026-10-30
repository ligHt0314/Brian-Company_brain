"""Small provider boundary. No model output is executable or authoritative by itself."""

import json
import time
from urllib.parse import urlparse
import httpx
from app.config import settings, ROOT
from app.observability import event
from app.domain.models import Extraction, Plan, Block, Strict
from pydantic import ValidationError


class Synthesis(Strict):
    blocks: list[Block]


class Provider:
    def __init__(self, deadline: float | None = None):
        self.calls = 0
        self.deadline = deadline

    @property
    def enabled(self) -> bool:
        return bool(settings.llm_api_key and settings.llm_model)

    def structured(self, schema, prompt: str, data: dict):
        if not self.enabled:
            raise ValueError("Live extraction requires LLM_API_KEY and LLM_MODEL on the server")
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": json.dumps(data)}]
        for attempt in range(2):
            self.calls += 1
            remaining = self.deadline - time.monotonic() if self.deadline else 30.0
            if remaining <= 0.5:
                raise TimeoutError("Model request deadline reached")
            timeout = min(settings.llm_request_timeout_ms / 1000, max(0.1, remaining - 0.5))
            google = urlparse(settings.llm_base_url).hostname == "generativelanguage.googleapis.com"
            payload = {
                "model": settings.llm_model,
                "messages": messages,
                "temperature": 1 if google else 0,
                "response_format": {"type": "json_object"},
                "max_completion_tokens": 4096,
            }
            if google:
                payload["reasoning_effort"] = "minimal" if "flash-lite" in settings.llm_model else "low"
            with httpx.Client(timeout=httpx.Timeout(timeout, connect=min(3.0, timeout))) as client:
                started = time.monotonic()
                try:
                    response = client.post(
                        settings.llm_base_url.rstrip("/") + "/chat/completions",
                        headers={"Authorization": "Bearer " + settings.llm_api_key},
                        json=payload,
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                except Exception as exc:
                    event(
                        "ai_call",
                        level=30,
                        model=settings.llm_model,
                        outcome="failed",
                        error_type=type(exc).__name__,
                        duration_ms=round((time.monotonic() - started) * 1000),
                    )
                    raise
                event(
                    "ai_call",
                    model=settings.llm_model,
                    outcome="success",
                    duration_ms=round((time.monotonic() - started) * 1000),
                )
            try:
                return schema.model_validate_json(content)
            except (ValidationError, ValueError):
                event("ai_schema_invalid", level=30, model=settings.llm_model, attempt=attempt + 1)
                if attempt:
                    raise ValueError("Model response failed schema validation")
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": "Return only valid JSON matching this schema: "
                        + json.dumps(schema.model_json_schema()),
                    }
                )

    def extract(self, body: str, registry: list[dict]) -> Extraction:
        prompt = (ROOT / "services/api/app/prompts/extract-v1.txt").read_text()
        result = self.structured(
            Extraction, prompt, {"body": body, "registry": registry, "schema": Extraction.model_json_schema()}
        )
        # Exact quote text is authoritative for location. Models often count offsets incorrectly.
        # Correct offsets only when an unchanged quote occurs once; never repair invented text.
        for claim in result.claims:
            if body[claim.start : claim.end] == claim.quote:
                continue
            start = body.find(claim.quote)
            if start < 0 or body.find(claim.quote, start + 1) >= 0:
                raise ValueError("Extraction needs an exact, unambiguous source quotation")
            claim.start = start
            claim.end = start + len(claim.quote)
        return result

    def plan(self, question: str, entities: list[dict]) -> Plan:
        return self.structured(
            Plan,
            (ROOT / "services/api/app/prompts/planning-v1.1.txt").read_text(),
            {"question": question, "entities": entities, "schema": Plan.model_json_schema()},
        )

    def synthesize(self, question: str, blocks: list[dict], evidence: list[dict]) -> Synthesis:
        return self.structured(
            Synthesis,
            (ROOT / "services/api/app/prompts/synthesis-v1.1.txt").read_text(),
            {
                "question": question,
                "findings": blocks,
                "evidence": evidence,
                "schema": Synthesis.model_json_schema(),
            },
        )

    def next_tools(
        self,
        question: str,
        intent: str,
        entity: dict,
        observations: list[dict],
        remaining_calls: int,
        round_number: int,
    ):
        from app.agent.tools import ToolDecision

        return self.structured(
            ToolDecision,
            (ROOT / "services/api/app/prompts/tools-v1.2.txt").read_text(),
            {
                "question": question,
                "intent": intent,
                "selected_entity": entity,
                "observations": observations,
                "remaining_calls": remaining_calls,
                "round": round_number,
                "schema": ToolDecision.model_json_schema(),
            },
        )
