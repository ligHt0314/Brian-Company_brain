"""Bounded, deterministic reasoning over source-authorized FalkorDB claims."""

import re
import time
from collections import defaultdict
from app.config import settings
from app.domain.models import (
    Answer,
    AgentToolStep,
    Block,
    Claim,
    Entity,
    Edge,
    Finding,
    GraphDTO,
    PathDTO,
    Scope,
    Metrics,
    uid,
    now_iso,
)
from app.ingestion.service import registry
from app.agent.provider import Provider
from app.agent.loop import investigate_with_tools
from app.agent.tools import KnowledgeChanged


def classify(question: str) -> str:
    q = question.lower()
    if any(x in q for x in ["owner", "owns", "worked on", "who has", "newer chat"]):
        return "owner_lookup"
    if any(x in q for x in ["why", "decision", "unverified identities", "rule out"]):
        return "decision_lookup"
    if any(x in q for x in ["if ", "unavailable", "fails", "impact"]):
        return "change_impact"
    if any(x in q for x in ["block", "risk", "launch", "promise", "commitment is affected"]):
        return "release_risk"
    return "evidence_search"


def resolve(question: str, entities: list[Entity]) -> list[Entity]:
    q = question.lower()
    aliases = defaultdict(set)
    for e in entities:
        for alias in [e.label, *e.aliases]:
            aliases[alias.lower()].add(e.id)
    matches = []
    for e in entities:
        for alias in [e.label, *e.aliases]:
            if re.search(r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)", q):
                matches.append((len(alias), e, len(aliases[alias.lower()])))
    if not matches:
        return []
    tickets = list({e.id: e for _, e, _ in matches if e.kind == "Ticket"}.values())
    if tickets:
        return tickets
    # A shared shorthand never overrides a more specific uniquely matched name.
    preferred = [m for m in matches if m[2] == 1] or matches
    longest = max(m[0] for m in preferred)
    return list({e.id: e for n, e, _ in preferred if n == longest}.values())


def search_evidence(question: str, claims: list[Claim]) -> list[Claim]:
    stop = {
        "what",
        "which",
        "could",
        "does",
        "this",
        "that",
        "with",
        "from",
        "have",
        "about",
        "would",
        "there",
        "their",
        "why",
        "did",
        "the",
        "and",
        "for",
        "our",
        "who",
        "how",
        "was",
        "are",
        "has",
        "can",
        "enough",
    }
    tokens = {
        word for word in re.findall(r"[a-z0-9]+", question.lower()) if len(word) > 2 and word not in stop
    }
    ranked = []
    for c in claims:
        words = set(re.findall(r"[a-z0-9]+", c.evidence.quote.lower()))
        score = len(words.intersection(tokens))
        if score >= 2:
            ranked.append((score, c))
    return [c for _, c in sorted(ranked, key=lambda row: row[0], reverse=True)[:16]]


class Investigator:
    def __init__(self, repo):
        self.repo = repo

    def run(
        self,
        run_id: str,
        question: str,
        groups: list[str],
        entity_id: str | None = None,
        context_id: str | None = None,
        stage=lambda _: None,
    ) -> Answer:
        started = time.monotonic()
        self.repo.local.count = 0
        self.repo.local.duration_ms = 0
        provider = Provider(deadline=started + max(0.5, settings.run_timeout_ms / 1000 - 1))
        for attempt in range(2):
            stage("Finding the project")
            with self.repo.lock:
                epoch = self.repo.epoch()
                sources = self.repo.sources(groups)
                allowed = [s["id"] for s in sources]
                claims, truncated = self.repo.claims(allowed)
            # The registry is an explicitly employee-visible directory, never extracted private labels.
            entities = [Entity.model_validate(e) for e in registry()]
            candidates = resolve(question, entities)
            intent = classify(question)
            selected = next((e for e in entities if e.id == entity_id), None)
            if entity_id and selected is None:
                candidates = []
            elif selected:
                candidates = [selected]
            elif (
                not candidates
                and context_id
                and re.search(
                    r"\b(it|its|this|that|those|same|again)\b|what changed|status now|any updates|which customer commitment",
                    question.lower(),
                )
            ):
                candidates = [e for e in entities if e.id == context_id]
            live_plan = False
            planning_failed = False
            if not candidates and not entity_id:
                hits = search_evidence(question, claims)
                if hits:
                    best = hits[0]
                    chosen_id = best.subject_id
                    candidates = [e for e in entities if e.id == chosen_id]
            if provider.enabled:
                try:
                    plan = provider.plan(question, [e.model_dump() for e in entities])
                    intent = plan.intent
                    live_plan = True
                    if not candidates and plan.entity_id:
                        candidates = [e for e in entities if e.id == plan.entity_id]
                except Exception:
                    planning_failed = True
            tool_trace = []
            tool_agent_used = False
            tool_agent_failed = False
            base = dict(
                run_id=run_id,
                intent=intent,
                graph_epoch=epoch,
                generated_at=now_iso(),
                scenario_time=settings.demo_clock_iso,
                scope=Scope(visible_sources_considered=len(sources), truncated=truncated),
            )
            if len(candidates) > 1:
                answer = Answer(
                    **base,
                    answer_state="clarification",
                    candidates=candidates,
                    blocks=[
                        Block(kind="uncertainty", text="Which entity do you mean? Choose one to continue.")
                    ],
                )
            elif not candidates:
                answer = Answer(
                    **base,
                    answer_state="insufficient_evidence",
                    blocks=[
                        Block(
                            kind="uncertainty",
                            text="No matching entity was found in the visible indexed scope. Try a project, service, ticket, or commitment name.",
                        )
                    ],
                )
            else:
                stage("Following dependencies")
                selected_claims = claims
                if live_plan:
                    try:
                        selected_claims, tool_trace, tool_truncated = investigate_with_tools(
                            provider, self.repo, question, intent, candidates[0], groups, epoch, stage
                        )
                        base["scope"].truncated = base["scope"].truncated or tool_truncated
                        tool_agent_used = True
                    except KnowledgeChanged:
                        if attempt == 0:
                            continue
                        raise ValueError("knowledge_changed")
                    except Exception:
                        selected_claims = claims
                        tool_agent_failed = True
                answer = self.derive(base, question, candidates[0], entities, selected_claims)
            answer.agent_trace = [AgentToolStep.model_validate(t.model_dump()) for t in tool_trace]
            if live_plan and not tool_agent_failed:
                answer.execution_mode = "live_model"
            if tool_agent_failed:
                answer.scope.warnings.append(
                    "Model tool selection unavailable; showing deterministic graph findings."
                )
            if planning_failed:
                answer.scope.warnings.append(
                    "Model planning unavailable; deterministic question routing was used."
                )
            stage("Checking sources")
            if self.repo.epoch() != epoch:
                if attempt == 0:
                    continue
                raise ValueError("knowledge_changed")
            # Optional model summary is derived and constrained to cited inference; graph facts stay deterministic.
            if (
                provider.enabled
                and answer.evidence
                and not tool_agent_failed
                and time.monotonic() - started < 19
            ):
                try:
                    result = provider.synthesize(
                        question,
                        [b.model_dump() for b in answer.blocks],
                        [e.model_dump() for e in answer.evidence],
                    )
                    valid = {e.id for e in answer.evidence}
                    extras = [
                        b
                        for b in result.blocks
                        if b.kind == "inference" and b.evidence_ids and set(b.evidence_ids) <= valid
                    ]
                    if extras:
                        answer.blocks.extend(extras[:1])
                        answer.execution_mode = "live_model"
                except Exception:
                    answer.scope.warnings.append(
                        "Model synthesis unavailable; showing deterministic evidence findings."
                    )
            stage("Preparing findings")
            if self.repo.epoch() != epoch:
                if attempt == 0:
                    continue
                raise ValueError("knowledge_changed")
            answer.metrics = Metrics(
                duration_ms=round((time.monotonic() - started) * 1000),
                graph_query_count=self.repo.local.count,
                graph_duration_ms=round(self.repo.local.duration_ms, 3),
                model_calls=provider.calls,
                agent_tool_calls=len(tool_trace) if tool_agent_used else 0,
                agent_rounds=max((t.round for t in tool_trace), default=0) if tool_agent_used else 0,
                model_id=settings.llm_model if provider.calls else None,
            )
            if answer.metrics.duration_ms > settings.run_timeout_ms:
                raise TimeoutError("Investigation exceeded its execution budget")
            return answer
        raise ValueError("knowledge_changed")

    def derive(
        self, base: dict, question: str, entity: Entity, entities: list[Entity], claims: list[Claim]
    ) -> Answer:
        labels = {e.id: e.label for e in entities}
        kinds = {e.id: e.kind for e in entities}
        answer = Answer(**base, entity_id=entity.id, answer_state="supported")
        by_subject = defaultdict(list)
        for c in claims:
            by_subject[c.subject_id].append(c)
        selected: dict[str, Claim] = {}
        path_claims: list[list[Claim]] = []

        def use(items):
            for c in items:
                selected[c.id] = c
            return list(dict.fromkeys(c.evidence.id for c in items))

        def block(text, items, kind="fact"):
            answer.blocks.append(Block(kind=kind, text=text, evidence_ids=use(items)))

        def finding(category, title, items, ids, path=None):
            pid = uid("path", *[c.id for c in path]) if path else None
            f = Finding(
                id=uid("finding", category, *ids),
                category=category,
                title=title,
                entity_ids=ids,
                evidence_ids=use(items),
                path_id=pid,
            )
            answer.findings.append(f)
            if path:
                path_claims.append(path)
            return f

        def reach(start):
            paths = {start: []}
            queue = [(start, 0)]
            while queue:
                current, depth = queue.pop(0)
                for c in by_subject[current]:
                    if c.predicate not in {"USES", "DEPENDS_ON"} or not c.object_id:
                        continue
                    next_depth = depth + int(c.predicate == "DEPENDS_ON")
                    if next_depth > 3:
                        answer.scope.truncated = True
                        continue
                    if c.object_id not in paths:
                        paths[c.object_id] = paths[current] + [c]
                        queue.append((c.object_id, next_depth))
            return paths

        def commitments(project_id):
            result = []
            for c in claims:
                if c.predicate == "REQUIRES" and c.object_id == project_id:
                    details = [x for x in by_subject[c.subject_id] if x.predicate in {"MADE_TO", "DUE_ON"}]
                    result.append((c, details))
            return result

        def owners(ids):
            for sid in sorted(ids):
                owned = [c for c in by_subject[sid] if c.predicate == "OWNED_BY"]
                scopes = defaultdict(list)
                for c in owned:
                    scopes[c.scope].append(c)
                for scope, items in scopes.items():
                    values = {c.object_id for c in items}
                    if len(values) > 1:
                        title = f"{labels[sid]} ownership needs confirmation"
                        block(
                            f"{labels[sid]} has competing primary ownership claims: "
                            + ", ".join(labels[x] for x in sorted(values))
                            + ". Recency alone does not resolve them.",
                            items,
                            "uncertainty",
                        )
                        f = finding("ownership_conflict", title, items, [sid])
                        answer.conflicts.append(f)
                    elif items:
                        block(f"{labels[sid]} has primary owner {labels[items[0].object_id]}.", items)
                contributors = [c for c in claims if c.predicate == "WORKED_ON" and c.object_id == sid]
                contributors = list({(c.subject_id, c.object_id): c for c in contributors}.values())
                if contributors and (
                    answer.intent == "owner_lookup" or len({c.object_id for c in owned}) > 1
                ):
                    people = list(dict.fromkeys(labels[c.subject_id] for c in contributors))
                    block(
                        "People with relevant work on "
                        + labels[sid]
                        + ": "
                        + ", ".join(people)
                        + ". Contribution does not establish ownership.",
                        contributors,
                    )
                if not owned and answer.intent == "owner_lookup":
                    block(
                        f"No primary ownership evidence was found for {labels[sid]} in the visible indexed scope.",
                        [],
                        "uncertainty",
                    )

        q = question.lower()
        if any(term in q for term in ["contract amount", "contract value", "salary", "budget", "how much"]):
            answer.answer_state = "insufficient_evidence"
            block("No evidence for that value was found in the visible indexed scope.", [], "uncertainty")
            return answer
        if answer.intent == "owner_lookup":
            owners({entity.id})
        elif answer.intent == "decision_lookup":
            relevant = [
                c
                for c in claims
                if c.predicate == "ABOUT" and (c.object_id == entity.id or c.subject_id == entity.id)
            ]
            for c in relevant:
                block(c.evidence.quote, [c])
                finding(
                    "decision", labels[c.subject_id] + " · decision context", [c], [c.subject_id, c.object_id]
                )
        elif answer.intent in {"release_risk", "change_impact"}:
            project_paths = {}
            if kinds[entity.id] == "Project":
                project_paths[entity.id] = reach(entity.id)
            elif kinds[entity.id] == "Service":
                for e in entities:
                    if e.kind == "Project":
                        paths = reach(e.id)
                        if entity.id in paths:
                            project_paths[e.id] = paths
            elif kinds[entity.id] == "Ticket":
                targets = {c.object_id for c in by_subject[entity.id] if c.predicate == "BLOCKS"}
                for e in entities:
                    if e.kind == "Project":
                        paths = reach(e.id)
                        if targets.intersection(paths):
                            project_paths[e.id] = paths
            elif kinds[entity.id] == "Commitment":
                for c in by_subject[entity.id]:
                    if c.predicate == "REQUIRES":
                        project_paths[c.object_id] = reach(c.object_id)
            mentioned_projects = {
                e.id
                for e in entities
                if e.kind == "Project"
                and any(
                    re.search(r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)", q)
                    for alias in [e.label, *e.aliases]
                    if alias.lower() != "launch"
                )
            }
            if entity.kind == "Ticket" and mentioned_projects:
                project_paths = {
                    pid: paths for pid, paths in project_paths.items() if pid in mentioned_projects
                }
            relevant_ids = set()
            for project_id, paths in project_paths.items():
                relevant_ids.update(paths)
                promise_items = commitments(project_id)
                if answer.intent == "change_impact" and entity.id in paths:
                    route = paths[entity.id]
                    items = route + [x for c, details in promise_items for x in [c, *details]]
                    block(
                        f"If {entity.label} becomes unavailable, {labels[project_id]} and its connected commitments may be affected through these dependencies. This does not establish an outage or delay.",
                        items,
                        "inference",
                    )
                    finding(
                        "conditional_impact",
                        labels[project_id] + " may be affected",
                        items,
                        [entity.id, project_id],
                        route,
                    )
                    # An impact question explains possible downstream effects; unrelated
                    # work items must not crowd the dependency and promise evidence out.
                    continue
                blockers = []
                for c in claims:
                    if c.predicate != "BLOCKS" or c.object_id not in paths:
                        continue
                    if kinds[entity.id] == "Ticket" and c.subject_id != entity.id:
                        continue
                    status = [x for x in by_subject[c.subject_id] if x.predicate == "STATUS"]
                    values = {x.scalar for x in status}
                    route = paths[c.object_id] + [c]
                    if len(values) != 1:
                        block(
                            f"{labels[c.subject_id]} has missing or conflicting status evidence; its blocker state is unresolved.",
                            [c, *status],
                            "uncertainty",
                        )
                        finding(
                            "unresolved_status",
                            labels[c.subject_id] + " status needs confirmation",
                            [c, *status],
                            [c.subject_id, project_id],
                            route,
                        )
                    elif next(iter(values)) in {"open", "in_progress", "blocked"}:
                        blockers.append(c)
                        items = route + status + [x for pc, details in promise_items for x in [pc, *details]]
                        block(
                            f"{labels[c.subject_id]} blocks {labels[c.object_id]} and is {status[0].scalar.replace('_', ' ')}. {labels[project_id]} reaches it through the dependency path.",
                            route + status,
                        )
                        finding(
                            "blocker",
                            labels[c.subject_id] + " · " + labels[c.object_id],
                            items,
                            [c.subject_id, project_id],
                            route,
                        )
                    elif kinds[entity.id] == "Ticket":
                        block(
                            f"{labels[c.subject_id]} has status {status[0].scalar}; it is not an active blocker under the current rule.",
                            [c, *status],
                        )
                if answer.intent == "release_risk" and not blockers:
                    block(
                        f"No confirmed active blockers were found for {labels[project_id]} in the visible indexed scope. This does not establish launch readiness.",
                        [],
                        "uncertainty",
                    )
                for pc, details in promise_items:
                    customer = next((labels[x.object_id] for x in details if x.predicate == "MADE_TO"), None)
                    due = next((x.scalar for x in details if x.predicate == "DUE_ON"), None)
                    text = f"{labels[pc.subject_id]} requires {labels[project_id]}"
                    if customer:
                        text += f" and is made to {customer}"
                    if due:
                        text += f"; due {due} (end of day, Asia/Kolkata)"
                    block(text + ".", [pc, *details])
                    path_claims.append([pc, *[x for x in details if x.object_id]])
                for c in claims:
                    if c.predicate == "ABOUT" and c.object_id == project_id:
                        block(c.evidence.quote, [c])
            if answer.intent == "release_risk" and entity.kind != "Ticket":
                owners(relevant_ids)
            if not project_paths:
                block(
                    "No supported project dependency path was found in the visible indexed scope.",
                    [],
                    "uncertainty",
                )
        else:
            direct = [c for c in by_subject[entity.id]]
            if any(x in q for x in ["status", "done", "blocked"]):
                direct = [c for c in direct if c.predicate == "STATUS"]
            elif any(x in q for x in ["due", "when"]):
                direct = [c for c in direct if c.predicate == "DUE_ON"]
            elif "customer" in q or "made to" in q or "for?" in q:
                direct = [c for c in direct if c.predicate == "MADE_TO"]
            elif "service" in q or " use" in q:
                direct = [c for c in direct if c.predicate in {"USES", "DEPENDS_ON"}]
            for c in direct:
                block(c.evidence.quote, [c])
        if not selected:
            answer.answer_state = "insufficient_evidence"
            if not answer.blocks:
                block("No supporting evidence was found in the visible indexed scope.", [], "uncertainty")
        elif answer.conflicts:
            answer.answer_state = "conflict"
        elif answer.scope.truncated:
            answer.answer_state = "partial"
        # A complete citation bundle is returned or its dependent statement is removed.
        chosen = list(selected.values())[:32]
        valid = {c.evidence.id for c in chosen}
        if len(selected) > 32:
            answer.scope.truncated = True
            answer.scope.warnings.append(
                "The evidence budget was reached. Narrow the question for more detail."
            )
            if answer.answer_state == "supported":
                answer.answer_state = "partial"
        answer.blocks = [b for b in answer.blocks if set(b.evidence_ids) <= valid]
        answer.findings = [f for f in answer.findings if set(f.evidence_ids) <= valid]
        answer.conflicts = [f for f in answer.conflicts if set(f.evidence_ids) <= valid]
        answer.evidence = [c.evidence for c in chosen]
        conflict_claims = {
            c.id for c in chosen if any(c.evidence.id in f.evidence_ids for f in answer.conflicts)
        }
        edges = [
            Edge(
                id=uid("edge", c.id),
                source_entity_id=c.subject_id,
                target_entity_id=c.object_id,
                predicate=c.predicate,
                claim_ids=[c.id],
                evidence_ids=[c.evidence.id],
                conflict=c.id in conflict_claims,
            )
            for c in chosen
            if c.object_id
        ]
        used_nodes = {e.source_entity_id for e in edges} | {e.target_entity_id for e in edges}
        nodes = [e for e in entities if e.id in used_nodes][:30]
        node_ids = {e.id for e in nodes}
        projected_edges = [
            e for e in edges if e.source_entity_id in node_ids and e.target_entity_id in node_ids
        ][:50]
        if len(projected_edges) < len(edges):
            answer.scope.truncated = True
            answer.scope.warnings.append(
                "The graph display budget was reached; narrow the question to inspect more paths."
            )
            if answer.answer_state == "supported":
                answer.answer_state = "partial"
        edge_ids = {e.id for e in projected_edges}
        graph_paths = [
            PathDTO(
                id=uid("path", *[c.id for c in path]),
                edge_ids=[uid("edge", c.id) for c in path if c.object_id],
            )
            for path in path_claims
            if all(not c.object_id or uid("edge", c.id) in edge_ids for c in path)
        ]
        answer.graph = GraphDTO(nodes=nodes, edges=projected_edges, paths=graph_paths)
        for c in chosen:
            if c.evidence.is_stale:
                answer.scope.warnings.append(
                    f"Stale source: {c.evidence.source_title}. Recency does not settle conflicting assertions."
                )
        answer.scope.warnings = list(dict.fromkeys(answer.scope.warnings))
        return answer
