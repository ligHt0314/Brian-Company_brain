import json
import os
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from functools import wraps
from typing import Annotated
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import asyncio
from app.config import settings
from app.observability import configure, event, request_id
from app.auth.policy import current_user, require, unavailable, serializer, PERSONAS
from app.domain.models import (
    Answer,
    Evidence,
    Entity,
    SourceList,
    RevisionMetadata,
    JobStatus,
    ReviewDTO,
    ConversationDTO,
    HistoryDTO,
    iso,
    SourceEnvelope,
    Candidate,
    InvestigateRequest,
    PersonaRequest,
    Me,
    ProposalRequest,
    ConfirmRequest,
    AccessRequest,
    RevisionRequest,
    TicketStatusRequest,
    TicketDetails,
    JobReceipt,
    uid,
    now_iso,
    ms,
    Change,
)
from app.graph.repository import Repository
from app.ingestion.service import Ingestion, registry, FIXTURES
from app.memory.store import Store
from app.reasoning.investigate import Investigator
from app.work.routes import router as work_router

configure()

repo = Repository()
store = Store(settings.sqlite_path)
ingestion = Ingestion(repo, store)
User = Annotated[Me, Depends(current_user)]
workers = set()
rate_buckets = defaultdict(deque)


def policy_snapshot(function):
    """Linearize access checks and payload reads against the same mutation lock."""

    @wraps(function)
    def wrapped(*args, **kwargs):
        with repo.lock:
            return function(*args, **kwargs)

    return wrapped


def error(status: int, code: str, message: str, retryable=False):
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "retryable": retryable,
                "request_id": request_id.get(),
            }
        },
    )


@asynccontextmanager
async def lifespan(app):
    if int(os.environ.get("WEB_CONCURRENCY", "1")) != 1:
        raise RuntimeError("Company Brain requires one API worker")
    if settings.app_env == "production" and (
        len(settings.session_secret) < 32 or settings.session_secret.startswith("local-")
    ):
        raise RuntimeError("Configure a strong SESSION_SECRET for deployment")
    for run in store.list("run"):
        if run["status"] in {"queued", "running"}:
            run.update(
                status="failed",
                error={
                    "code": "interrupted",
                    "message": "The server restarted. Rerun this investigation.",
                    "retryable": True,
                },
            )
            store.put(run["id"], "run", run["actor"], run)
    try:
        for job in store.list("job"):
            if job["status"] in {"queued", "running"}:
                source = repo.source(job["source_id"])
                if source and job.get("revision_id") == source.get("active_revision_id"):
                    job.update(status="complete", stage="Indexed")
                else:
                    candidates = (
                        [Candidate.model_validate(c) for c in job["claims"]] if "claims" in job else None
                    )
                    task = asyncio.create_task(
                        asyncio.to_thread(
                            ingestion.import_source,
                            SourceEnvelope.model_validate(job["envelope"]),
                            job["actor"],
                            candidates,
                            job.get("fixture", False),
                            job["id"],
                        )
                    )
                    workers.add(task)
                    task.add_done_callback(workers.discard)
                    continue
                store.put(job["id"], "job", job["actor"], job)
    except Exception:
        pass
    yield


app = FastAPI(title="Company Brain API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def policy(request: Request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin")
        expected = settings.allowed_origin.rstrip("/")
        # Trusted same-origin proxy supplies Origin too. Non-browser operators use the CSRF header.
        if origin != expected and not (
            settings.app_env == "development" and origin == "http://127.0.0.1:3000"
        ):
            return error(403, "origin_rejected", "A same-origin request is required")
        if request.headers.get("x-brain-csrf") != "1":
            return error(403, "csrf_required", "The application request header is required")
        key = (request.client.host if request.client else "local", request.url.path)
        bucket = rate_buckets[key]
        clock = time.monotonic()
        while bucket and bucket[0] < clock - 60:
            bucket.popleft()
        if len(bucket) >= 60:
            return error(429, "rate_limited", "Please wait before trying again", True)
        bucket.append(clock)
    try:
        response = await call_next(request)
    except Exception as exc:
        event(
            "request_error",
            level=40,
            error_type=type(exc).__name__,
            route=getattr(request.scope.get("route"), "path", "unmatched"),
        )
        return error(503, "dependency_unavailable", "A service is unavailable. Please retry.", True)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.middleware("http")
async def tracing(request: Request, call_next):
    correlation = uid("req", secrets.token_hex(16))
    token = request_id.set(correlation)
    started = time.monotonic()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = correlation
        event(
            "request_completed",
            method=request.method,
            status=response.status_code,
            level=30 if response.status_code >= 400 else 20,
            route=getattr(request.scope.get("route"), "path", "unmatched"),
            duration_ms=round((time.monotonic() - started) * 1000),
        )
        return response
    except Exception as exc:
        event("request_failed", level=40, method=request.method, error_type=type(exc).__name__)
        raise
    finally:
        request_id.reset(token)


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    codes = {
        401: "session_required",
        403: "forbidden",
        404: "unavailable",
        409: "conflict",
        413: "upload_limit",
        422: "invalid_input",
        503: "dependency_unavailable",
    }
    return error(
        exc.status_code,
        codes.get(exc.status_code, "invalid_request"),
        str(exc.detail),
        exc.status_code == 503,
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return error(422, "invalid_input", "Check the request fields and source format")


@app.get("/api/v1/health/live")
def live():
    return {"status": "live"}


@app.get("/api/v1/health/ready")
def ready():
    try:
        repo.db.connection.ping()
        store.db.execute("SELECT 1")
        return {
            "status": "ready",
            "graph": "falkordb",
            "execution_mode": "live_model_available"
            if settings.llm_api_key and settings.llm_model
            else "deterministic",
        }
    except Exception:
        raise HTTPException(503, "Graph or operational store is unavailable")


@app.post("/api/v1/demo/session", response_model=Me)
def demo_session(body: PersonaRequest, response: Response):
    if not settings.demo_mode:
        unavailable()
    response.set_cookie(
        "brain_session",
        serializer.dumps(body.persona),
        httponly=True,
        samesite="strict",
        secure=settings.app_env == "production",
        max_age=86400,
        path="/",
    )
    return PERSONAS[body.persona]


@app.get("/api/v1/me", response_model=Me)
def me(user: User):
    return user


@app.post("/api/v1/sessions")
def new_session(user: User):
    sid = uid("session", user.id, secrets.token_hex(16))
    data = {"id": sid, "actor": user.id, "last_entity_id": None, "created_at": now_iso()}
    store.put(sid, "conversation", user.id, data)
    return data


@app.get("/api/v1/sessions", response_model=list[ConversationDTO])
def list_sessions(user: User):
    return [{k: v for k, v in s.items() if k != "actor"} for s in store.list("conversation", user.id)]


@app.get("/api/v1/sessions/{id}")
def get_session(id: str, user: User):
    session = store.get(id, "conversation", user.id)
    if not session:
        unavailable()
    return session | {"runs": [r["id"] for r in store.list("run", user.id) if r["session_id"] == id]}


def visible(user):
    return repo.sources(user.groups)


def allowed(user):
    return [s["id"] for s in visible(user)]


@policy_snapshot
def checked_run(id, user):
    run = store.get(id, "run", user.id)
    if not run:
        unavailable()
    if run.get("answer"):
        # Current ACL governs saved answers; return no old body after permission loss.
        permitted = set(allowed(user))
        answer = run["answer"]
        if any(e["source_id"] not in permitted for e in answer["evidence"]):
            return run | {
                "answer": Answer(
                    run_id=id,
                    answer_state="needs_refresh",
                    intent=answer["intent"],
                    entity_id=answer.get("entity_id"),
                    graph_epoch=repo.epoch(),
                    generated_at=now_iso(),
                    scenario_time=settings.demo_clock_iso,
                ).model_dump()
            }
        current = {s["id"]: s["active_revision_id"] for s in visible(user)}
        answer = dict(
            answer,
            historical=any(current.get(e["source_id"]) != e["revision_id"] for e in answer["evidence"]),
        )
        return run | {"answer": answer}
    return run


def execute_run(id: str, user: Me):
    execution_started = time.monotonic()
    run = store.get(id, "run", user.id)

    def stage(text):
        run.update(status="running", stage=text)
        store.put(id, "run", user.id, run)

    try:
        session = store.get(run["session_id"], "conversation", user.id)
        answer = Investigator(repo).run(
            id, run["question"], user.groups, run.get("entity_id"), session.get("last_entity_id"), stage
        )
        previous_id = run.get("previous_run_id")
        if previous_id:
            previous = checked_run(previous_id, user)
            old = previous.get("answer")
            if (
                old
                and old["answer_state"] != "needs_refresh"
                and old["intent"] == answer.intent
                and old.get("entity_id") == answer.entity_id
            ):
                old_findings = {f["id"]: f for f in old["findings"]}
                new_findings = {f.id: f for f in answer.findings}
                # Re-read current source-authorized claims to explain actual status changes.
                current_claims, _ = repo.claims(allowed(user))
                for fid, f in old_findings.items():
                    if fid not in new_findings:
                        statuses = [
                            c
                            for c in current_claims
                            if c.subject_id in f["entity_ids"] and c.predicate == "STATUS"
                        ]
                        values = {c.scalar for c in statuses}
                        done = values and values <= {"done", "cancelled"}
                        supporting = statuses if done else []
                        for c in supporting:
                            if c.evidence.id not in {e.id for e in answer.evidence}:
                                answer.evidence.append(c.evidence)
                        text = f["title"] + (
                            " is no longer an active blocker: updated status is "
                            + ", ".join(sorted(values))
                            + "."
                            if done
                            else " was not found in the current evidence. This does not prove resolution."
                        )
                        answer.changes.removed.append(
                            Change(
                                finding_id=fid, text=text, evidence_ids=[c.evidence.id for c in supporting]
                            )
                        )
                for fid, f in new_findings.items():
                    if fid not in old_findings:
                        answer.changes.added.append(
                            Change(finding_id=fid, text=f.title, evidence_ids=f.evidence_ids)
                        )
                    elif set(f.evidence_ids) != set(old_findings[fid]["evidence_ids"]):
                        answer.changes.changed.append(
                            Change(
                                finding_id=fid,
                                text=f.title + " has updated evidence.",
                                evidence_ids=f.evidence_ids,
                            )
                        )
        if repo.epoch() != answer.graph_epoch:
            raise ValueError("knowledge_changed")
        answer.metrics.duration_ms = round((time.monotonic() - execution_started) * 1000)
        answer.metrics.graph_query_count = repo.local.count
        answer.metrics.graph_duration_ms = round(repo.local.duration_ms, 3)
        run.update(status="complete", stage="Complete", answer=answer.model_dump())
        if answer.entity_id:
            session["last_entity_id"] = answer.entity_id
            store.put(session["id"], "conversation", user.id, session)
    except Exception as exc:
        code = "knowledge_changed" if str(exc) == "knowledge_changed" else "dependency_unavailable"
        run.update(
            status="failed",
            error={
                "code": code,
                "message": "The investigation could not complete. Please retry.",
                "retryable": True,
            },
        )
    store.put(id, "run", user.id, run)


@app.post("/api/v1/investigations")
def investigate(body: InvestigateRequest, user: User, background: BackgroundTasks):
    if not store.get(body.session_id, "conversation", user.id):
        unavailable()
    if body.previous_run_id:
        checked_run(body.previous_run_id, user)
    id = uid("run", user.id, secrets.token_hex(16))
    run = body.model_dump() | {
        "id": id,
        "actor": user.id,
        "status": "queued",
        "stage": "Queued",
        "created_at": now_iso(),
    }
    store.put(id, "run", user.id, run)
    background.add_task(execute_run, id, user)
    return {"run_id": id, "status": "queued"}


@app.get("/api/v1/investigations/{id}", response_model=Answer | dict)
def get_run(id: str, user: User):
    run = checked_run(id, user)
    if run["status"] == "complete":
        return run["answer"]
    return {k: v for k, v in run.items() if k in {"id", "status", "stage", "error"}}


@app.get("/api/v1/history", response_model=list[HistoryDTO])
def history(user: User):
    return [
        {
            k: v
            for k, v in r.items()
            if k in {"id", "question", "status", "created_at", "entity_id", "session_id"}
        }
        for r in store.list("run", user.id)
    ]


@app.get("/api/v1/entities/search", response_model=list[Entity])
def entity_search(user: User, q: str = "", limit: int = 200):
    # Explicitly public directory labels only.
    return [
        e
        for e in registry()
        if q.lower() in e["label"].lower() or any(q.lower() in a.lower() for a in e["aliases"])
    ][: min(max(1, limit), 250)]


@app.get("/api/v1/sources", response_model=SourceList)
@policy_snapshot
def sources(user: User, offset: int = 0, limit: int = 20, q: str = "", kind: str = ""):
    rows = visible(user)
    rows = [
        s for s in rows if q.lower() in s["revision"]["title"].lower() and (not kind or s["kind"] == kind)
    ]

    def dto(s):
        r = s["revision"]
        threshold = {"ticket": 7, "chat": 7, "document": 30, "directory": 30, "decision": 90}[s["kind"]]
        return {
            "id": s["id"],
            "kind": s["kind"],
            "title": r["title"],
            "active_revision_id": s["active_revision_id"],
            "revision_number": r["revision_number"],
            "source_updated_at": iso(r["source_updated_at_ms"]),
            "indexed_at": iso(r["indexed_at_ms"]),
            "acl_groups": s["acl_groups"],
            "ingestion_mode": r["ingestion_mode"],
            "is_stale": ms(settings.demo_clock_iso) - r["source_updated_at_ms"] > threshold * 86400000,
            "state": s["state"],
        }

    return {
        "items": [dto(s) for s in rows[max(0, offset) : max(0, offset) + min(max(1, limit), 100)]],
        "total": len(rows),
        "graph_epoch": repo.epoch(),
    }


@app.get("/api/v1/sources/{id}/revisions", response_model=list[RevisionMetadata])
@policy_snapshot
def source_revisions(id: str, user: User):
    if id not in allowed(user):
        unavailable()
    return [
        {
            "id": r["id"],
            "revision_number": r["revision_number"],
            "title": r["title"],
            "source_updated_at": iso(r["source_updated_at_ms"]),
            "indexed_at": iso(r["indexed_at_ms"]),
            "is_current": r["id"] == repo.source(id)["active_revision_id"],
            "ingestion_mode": r["ingestion_mode"],
        }
        for r in repo.revisions(id)
        if r["state"] in {"active", "historical"}
    ]


@app.get("/api/v1/evidence/{id}", response_model=Evidence)
@policy_snapshot
def evidence(id: str, user: User):
    result = repo.evidence(id, allowed(user))
    if not result:
        unavailable()
    return result


@app.post("/api/v1/imports")
async def imports(
    user: User, background: BackgroundTasks, files: list[UploadFile] = File(...), metadata: str = Form("{}")
):
    require(user, "import")
    if not 1 <= len(files) <= 20:
        raise HTTPException(413, "Import between 1 and 20 files")
    try:
        meta = json.loads(metadata)
    except ValueError:
        raise HTTPException(422, "Metadata must be JSON")
    envelopes = []
    for file in files:
        raw = await file.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise HTTPException(413, "File exceeds the 2 MB limit")
        try:
            text = raw.decode("utf-8")
            if file.filename and file.filename.endswith(".json"):
                env = SourceEnvelope.model_validate_json(text)
            elif file.filename and file.filename.endswith((".md", ".txt")):
                env = SourceEnvelope.model_validate(meta | {"body": text})
            else:
                raise ValueError("Use JSON, Markdown, or UTF-8 text files")
            existing = repo.source(env.source_id)
            if existing and env.source_id not in allowed(user):
                unavailable()
            envelopes.append(env)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                422, "Invalid UTF-8 source envelope or metadata. Check required fields and file extension."
            )
    jobs = []
    for env in envelopes:
        id = uid("job", user.id, secrets.token_hex(16))
        store.put(
            id,
            "job",
            user.id,
            {
                "id": id,
                "actor": user.id,
                "status": "queued",
                "stage": "Queued",
                "source_id": env.source_id,
                "created_at": now_iso(),
                "envelope": env.model_dump(),
            },
        )
        background.add_task(ingestion.import_source, env, user.id, None, False, id)
        jobs.append(id)
    return {"job_ids": jobs}


@app.get("/api/v1/jobs/{id}", response_model=JobStatus)
@policy_snapshot
def job(id: str, user: User):
    require(user, "import")
    result = store.get(id, "job", user.id)
    if not result:
        unavailable()
    if repo.source(result["source_id"]) and result["source_id"] not in allowed(user):
        unavailable()
    return ingestion.public_job(result)


@app.patch("/api/v1/sources/{id}/access")
def access(id: str, body: AccessRequest, user: User):
    require(user, "import")
    with repo.lock:
        if id not in allowed(user):
            unavailable()
        result = repo.query(
            """MATCH (s:Source {id:$id}),(m:GraphMeta {id:'meta'}) WHERE s.active_revision_id=$expected
            SET s.acl_groups=$acl,s.checksum='',m.epoch=m.epoch+1 RETURN m.epoch""",
            {"id": id, "expected": body.expected_revision_id, "acl": body.acl_groups},
            True,
        )
        if not result:
            raise HTTPException(409, "Source changed. Refresh before updating access")
    return {"status": "updated", "graph_epoch": result[0][0]}


@app.get("/api/v1/sources/{id}/ticket", response_model=TicketDetails)
@policy_snapshot
def ticket_details(id: str, user: User):
    require(user, "import")
    if id not in allowed(user):
        unavailable()
    from app.ingestion.tickets import details

    return details(repo, id)


@app.post("/api/v1/sources/{id}/ticket-status", response_model=JobReceipt)
def update_ticket_status(id: str, body: TicketStatusRequest, user: User, background: BackgroundTasks):
    require(user, "import")
    from app.ingestion.tickets import prepare_update

    with repo.lock:
        if id not in allowed(user):
            unavailable()
        envelope, candidates = prepare_update(repo, id, body.expected_revision_id, body.status)
    job_id = uid("job", user.id, secrets.token_hex(16))
    store.put(
        job_id,
        "job",
        user.id,
        {
            "id": job_id,
            "actor": user.id,
            "status": "queued",
            "stage": "Queued",
            "source_id": id,
            "created_at": now_iso(),
            "envelope": envelope.model_dump(),
            "claims": [c.model_dump() for c in candidates],
            "fixture": False,
        },
    )
    background.add_task(ingestion.import_source, envelope, user.id, candidates, False, job_id)
    return {"job_ids": [job_id]}


@app.post("/api/v1/demo/apply-revision")
def apply_revision(body: RevisionRequest, user: User, background: BackgroundTasks):
    require(user, "import")
    if not settings.demo_mode:
        unavailable()
    if body.fixture_id == "restrict_runbook":
        sid = "doc:identity-runbook"
        source = repo.source(sid)
        return access(
            sid,
            AccessRequest(expected_revision_id=source["active_revision_id"], acl_groups=["leadership"]),
            user,
        )
    record = json.loads((FIXTURES / "ticket_T-101.json").read_text())
    env = SourceEnvelope.model_validate(record["envelope"])
    env.expected_revision_id = repo.source(env.source_id)["active_revision_id"]
    candidates = [Candidate.model_validate(c) for c in record["claims"]]
    if body.fixture_id == "t101_done":
        env.body = env.body.replace("status blocked", "status done")
        env.source_updated_at = "2026-10-17T04:25:00Z"
        candidates = []
        pos = 0
        for predicate, scalar, quote in [
            ("BLOCKS", None, "T-101 blocks Identity Gateway."),
            ("STATUS", "done", "T-101 has status done."),
        ]:
            start = env.body.index(quote, pos)
            pos = start + len(quote)
            candidates.append(
                Candidate(
                    subject_id="ticket:T-101",
                    predicate=predicate,
                    object_id="service:identity" if predicate == "BLOCKS" else None,
                    scalar=scalar,
                    quote=quote,
                    start=start,
                    end=pos,
                )
            )
    else:
        env.source_updated_at = "2026-10-17T04:26:00Z"
        candidates[0].start = 1
    id = uid("job", user.id, secrets.token_hex(16))
    store.put(
        id,
        "job",
        user.id,
        {
            "id": id,
            "actor": user.id,
            "status": "queued",
            "stage": "Queued",
            "source_id": env.source_id,
            "created_at": now_iso(),
            "envelope": env.model_dump(),
        },
    )
    background.add_task(ingestion.import_source, env, user.id, candidates, True, id)
    return {"job_ids": [id]}


@app.post("/api/v1/reviews/proposals", response_model=ReviewDTO)
@policy_snapshot
def proposal(body: ProposalRequest, user: User):
    require(user, "review")
    run = checked_run(body.run_id, user)
    answer = run.get("answer")
    if not answer or answer["answer_state"] == "needs_refresh":
        raise HTTPException(409, "Refresh the investigation before preparing a review")
    entities = {e["id"]: e for e in registry()}
    if body.assignee_id not in entities or entities[body.assignee_id]["kind"] != "Person":
        raise HTTPException(422, "Select a directory person")
    findings = [f for f in answer["findings"] if body.entity_id in f["entity_ids"]]
    ev_ids = list(dict.fromkeys(e for f in findings for e in f["evidence_ids"]))
    if not ev_ids:
        raise HTTPException(422, "Select an entity with supported findings")
    if repo.epoch() != answer["graph_epoch"]:
        raise HTTPException(409, "The evidence changed. Rerun before preparing a review")
    id = uid("proposal", user.id, secrets.token_hex(16))
    entity = entities[body.entity_id]
    result = {
        "id": id,
        "actor": user.id,
        "title": entity["label"] + " · evidence review",
        "reason": body.reason,
        "assignee_id": body.assignee_id,
        "assignee_name": entities[body.assignee_id]["label"],
        "entity_id": body.entity_id,
        "evidence_ids": ev_ids,
        "graph_epoch": repo.epoch(),
        "expires_at_ms": int(time.time() * 1000) + 600000,
        "destination": "Company Brain internal reviews",
        "state": "Draft",
    }
    store.put(id, "proposal", user.id, result)
    return {k: v for k, v in result.items() if k != "actor"}


@app.post("/api/v1/reviews/confirm", response_model=ReviewDTO)
def confirm(body: ConfirmRequest, user: User):
    require(user, "review")
    with repo.lock:
        draft = store.get(body.proposal_id, "proposal", user.id)
        if not draft:
            unavailable()
        permitted = allowed(user)
        if any(repo.evidence(e, permitted) is None for e in draft["evidence_ids"]):
            unavailable()
        existing = next(
            (t for t in repo.tasks() if t["created_by"] == user.id and t["proposal_id"] == draft["id"]), None
        )
        if existing:
            if existing["idempotency_key"] != body.idempotency_key:
                raise HTTPException(409, "This proposal was already confirmed with another key")
            return existing
        if draft["expires_at_ms"] < time.time() * 1000 or draft["graph_epoch"] != repo.epoch():
            raise HTTPException(
                409, "The evidence changed or the preview expired. Refresh it before creating the task"
            )
        if any(
            t["created_by"] == user.id and t["idempotency_key"] == body.idempotency_key for t in repo.tasks()
        ):
            raise HTTPException(409, "This idempotency key was already used")
        task = {
            k: v
            for k, v in draft.items()
            if k not in {"actor", "expires_at_ms", "graph_epoch", "destination"}
        }
        task.update(
            id=uid("review", user.id, draft["id"]),
            proposal_id=draft["id"],
            created_by=user.id,
            created_at=now_iso(),
            state="open",
            idempotency_key=body.idempotency_key,
        )
        repo.query(
            """MATCH (m:GraphMeta {id:'meta'}),(e:Entity {id:$entity}),(p:Entity {id:$person})
            MERGE (t:ReviewTask {id:$id}) SET t.title=$title,t.reason=$reason,t.assignee_id=$person,t.created_by=$actor,
            t.created_at_ms=$created,t.state='open',t.idempotency_key=$key,t.evidence_ids_json=$evidence,t.payload=$payload
            MERGE (t)-[:ABOUT]->(e) MERGE (t)-[:ASSIGNED_TO]->(p) SET m.epoch=m.epoch+1""",
            {
                "entity": draft["entity_id"],
                "person": draft["assignee_id"],
                "id": task["id"],
                "title": task["title"],
                "reason": task["reason"],
                "actor": user.id,
                "created": ms(task["created_at"]),
                "key": body.idempotency_key,
                "evidence": json.dumps(task["evidence_ids"]),
                "payload": json.dumps(task),
            },
            True,
        )
        return task


@app.get("/api/v1/reviews", response_model=list[ReviewDTO])
@policy_snapshot
def reviews(user: User):
    permitted = allowed(user)
    return [
        t for t in repo.tasks() if all(repo.evidence(e, permitted) is not None for e in t["evidence_ids"])
    ]


@app.post("/api/v1/demo/reset")
def reset(request: Request, user: User):
    require(user, "import")
    if not settings.demo_mode or settings.falkordb_graph != "company_brain_digiplus_services":
        unavailable()
    if not settings.operator_reset_token or not secrets.compare_digest(
        request.headers.get("x-operator-token", ""), settings.operator_reset_token
    ):
        raise HTTPException(403, "The private operator credential is required")
    with repo.lock:
        previous_epoch = repo.epoch()
        repo.graph.delete()
        repo.initialize(registry())
        repo.query("MATCH (m:GraphMeta {id:'meta'}) SET m.epoch=$epoch", {"epoch": previous_epoch + 1}, True)
        ingestion.seed()
    return {"status": "reset"}


app.include_router(work_router)
