import json
from hashlib import sha256
from pathlib import Path
from fastapi import HTTPException
from app.config import settings, ROOT
from app.domain.models import Candidate, PREDICATES, SourceEnvelope, uid, now_iso, ms
from app.agent.provider import Provider

FIXTURES = ROOT / "fixtures/digiplus"


def registry() -> list[dict]:
    return json.loads((FIXTURES / "registry.json").read_text())


def chunks(body: str) -> list[tuple[int, int, str]]:
    # Paragraph boundaries preserve short evidence; overlap only when a paragraph exceeds the hard limit.
    if not body:
        return [(0, 0, "")]
    out = []
    start = 0
    while start < len(body):
        end = min(start + 1500, len(body))
        if end < len(body):
            boundary = body.rfind("\n\n", start + 300, end)
            if boundary > start:
                end = boundary + 2
        out.append((start, end, body[start:end]))
        start = end if end == len(body) or body[end - 2 : end] == "\n\n" else end - 150
    return out


def validate_candidates(body: str, candidates: list[Candidate], entities: list[dict]):
    kinds = {e["id"]: e["kind"] for e in entities}
    for c in candidates:
        if body[c.start : c.end] != c.quote:
            raise ValueError("Evidence quote does not match its source span")
        if c.subject_id not in kinds or c.object_id is not None and c.object_id not in kinds:
            raise ValueError("Claim references an unregistered entity")
        subjects, objects = PREDICATES[c.predicate]
        if (
            kinds[c.subject_id] not in subjects
            or (objects and (c.object_id is None or kinds[c.object_id] not in objects))
            or (not objects and c.scalar is None)
        ):
            raise ValueError("Predicate is incompatible with entity types")


class Ingestion:
    def __init__(self, repo, store):
        self.repo, self.store = repo, store

    def import_source(
        self,
        envelope: SourceEnvelope,
        actor: str,
        curated: list[Candidate] | None = None,
        fixture: bool = False,
        job_id: str | None = None,
    ) -> dict:
        job_id = job_id or uid("job", actor, now_iso(), envelope.source_id)
        job = {
            "id": job_id,
            "actor": actor,
            "status": "running",
            "stage": "Validating source",
            "source_id": envelope.source_id,
            "envelope": envelope.model_dump(),
            "fixture": fixture,
            "created_at": now_iso(),
        }
        self.store.put(job_id, "job", actor, job)
        try:
            result = self._import(envelope, curated, fixture, job)
            job.update(status="complete", stage="Indexed", **result)
        except HTTPException as exc:
            job.update(status="failed", stage="Failed", error=str(exc.detail), code=exc.status_code)
        except Exception as exc:
            # Validation errors are curated messages; provider/network exceptions may carry private URLs.
            message = (
                str(exc)
                if isinstance(exc, ValueError)
                else "Source processing failed; prior active evidence remains available"
            )
            job.update(
                status="failed",
                stage="Failed",
                error=message,
                code=422 if isinstance(exc, ValueError) else 503,
            )
        self.store.put(job_id, "job", actor, job)
        return self.public_job(job)

    @staticmethod
    def public_job(job: dict) -> dict:
        return {k: v for k, v in job.items() if k not in {"envelope", "claims", "actor"}}

    @staticmethod
    def check_update_access(source, actor):
        if actor == "operator" or not source:
            return
        from app.auth.policy import PERSONAS

        identity = next((p for p in PERSONAS.values() if p.id == actor), None)
        if (
            not identity
            or "import" not in identity.capabilities
            or not set(source.get("acl_groups", [])).intersection(identity.groups)
        ):
            raise HTTPException(404, "This record is unavailable")

    def _import(self, env: SourceEnvelope, curated, fixture, job):
        entities = registry()
        labels = {e["id"]: e["label"] for e in entities}
        original = env.body
        body = original.replace("\r\n", "\n").replace("\r", "\n")
        method = (
            "structured"
            if env.records
            else "fixture"
            if fixture
            else "reviewed"
            if curated is not None
            else "model"
        )
        if env.records:
            if env.kind != "ticket" or env.records.entity_id not in labels:
                raise ValueError("Structured records require a registered ticket")
            facts = []
            for target in env.records.blocks:
                if target not in labels:
                    raise ValueError("Unknown blocked entity")
                facts.append(
                    (
                        env.records.entity_id,
                        "BLOCKS",
                        target,
                        None,
                        f"{labels[env.records.entity_id]} blocks {labels[target]}.",
                    )
                )
            if env.records.status:
                facts.append(
                    (
                        env.records.entity_id,
                        "STATUS",
                        None,
                        env.records.status,
                        f"{labels[env.records.entity_id]} has status {env.records.status}.",
                    )
                )
            body = "\n\n".join(f[-1] for f in facts)
            curated = []
            pos = 0
            for subject, predicate, obj, scalar, quote in facts:
                start = body.index(quote, pos)
                pos = start + len(quote)
                curated.append(
                    Candidate(
                        subject_id=subject,
                        predicate=predicate,
                        object_id=obj,
                        scalar=scalar,
                        quote=quote,
                        start=start,
                        end=pos,
                    )
                )
        canonical = env.model_dump(exclude={"expected_revision_id", "body"}) | {"body": body}
        checksum = sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
        with self.repo.lock:
            source = self.repo.source(env.source_id)
            self.check_update_access(source, job["actor"])
            if source and source.get("checksum") == checksum:
                return {
                    "revision_id": source["active_revision_id"],
                    "unchanged": True,
                    "accepted": 0,
                    "pending": 0,
                    "unresolved_mentions": [],
                }
            if source and source.get("active_revision_id") != env.expected_revision_id:
                raise HTTPException(409, "Source changed. Refresh its current revision before updating")
            if not source and env.expected_revision_id:
                raise HTTPException(409, "Expected revision does not match")
        unresolved = []
        if curated is None:
            job["stage"] = "Extracting evidence"
            self.store.put(job["id"], "job", job["actor"], job)
            candidates = []
            for start, end, part in chunks(body):
                extraction = Provider().extract(part, entities)
                unresolved.extend(extraction.unresolved_mentions)
                for c in extraction.claims:
                    c.start += start
                    c.end += start
                    candidates.append(c)
            curated = candidates
        validate_candidates(body, curated, entities)
        # Validate before persisting graph staging. Repeated overlap passages collapse to one claim.
        curated = list(
            {(c.subject_id, c.predicate, c.object_id, c.scalar, c.start, c.end): c for c in curated}.values()
        )
        job["claims"] = [c.model_dump() for c in curated]
        job["stage"] = "Staging validated evidence"
        self.store.put(job["id"], "job", job["actor"], job)
        source_chunks = chunks(body)
        for c in curated:
            if not any(start <= c.start and c.end <= end for start, end, _ in source_chunks):
                source_chunks.append((c.start, c.end, body[c.start : c.end]))
        upload = Path(settings.upload_dir)
        upload.mkdir(parents=True, exist_ok=True)
        (upload / (checksum + ".original.txt")).write_text(original)
        (upload / (checksum + ".normalized.txt")).write_text(body)
        with self.repo.lock:
            source = self.repo.source(env.source_id)
            self.check_update_access(source, job["actor"])
            if source and source.get("active_revision_id") != env.expected_revision_id:
                raise HTTPException(409, "Source changed during extraction. Refresh and retry")
            number = int(source.get("revision_number", 0)) + 1 if source else 1
            rid = uid("rev", env.source_id, checksum, number)
            job["revision_id"] = rid
            self.store.put(job["id"], "job", job["actor"], job)
            indexed = ms(now_iso())
            old = source["active_revision_id"] if source else ""
            self.repo.query(
                """MERGE (s:Source {id:$sid}) ON CREATE SET s.kind=$kind,s.state='staging',s.active_revision_id='',s.acl_groups=[]
                MERGE (r:SourceRevision {id:$rid}) SET r.source_id=$sid,r.revision_number=$number,r.checksum=$checksum,
                r.source_updated_at_ms=$updated,r.indexed_at_ms=$indexed,r.state='staging',r.title=$title,
                r.content_path=$content,r.ingestion_mode=$mode
                MERGE (s)-[:HAS_REVISION]->(r)""",
                {
                    "sid": env.source_id,
                    "kind": env.kind,
                    "rid": rid,
                    "number": number,
                    "checksum": checksum,
                    "updated": ms(env.source_updated_at),
                    "indexed": indexed,
                    "title": env.title,
                    "content": checksum + ".normalized.txt",
                    "mode": "fixture" if fixture else "live_import",
                },
                True,
            )
            chunk_ids = []
            for ordinal, (start, end, text) in enumerate(source_chunks):
                cid = uid("chunk", rid, start, end)
                chunk_ids.append(cid)
                self.repo.query(
                    """MATCH (r:SourceRevision {id:$rid}) MERGE (ch:Chunk {id:$id})
                    SET ch.revision_id=$rid,ch.ordinal=$ordinal,ch.text=$text,ch.char_start=$start,ch.char_end=$end
                    MERGE (r)-[:HAS_CHUNK]->(ch)""",
                    {"rid": rid, "id": cid, "ordinal": ordinal, "text": text, "start": start, "end": end},
                    True,
                )
            accepted = 0
            for c in curated:
                idx = next(
                    i for i, (start, end, _) in enumerate(source_chunks) if start <= c.start and c.end <= end
                )
                relative_start = c.start - source_chunks[idx][0]
                relative_end = c.end - source_chunks[idx][0]
                cid = uid(
                    "claim", rid, c.subject_id, c.predicate, c.object_id, c.scalar, c.scope, c.start, c.end
                )
                evid = uid("ev", cid, chunk_ids[idx], relative_start, relative_end)
                accepted += c.extraction_score >= 0.85
                params = {
                    "cid": cid,
                    "subject": c.subject_id,
                    "chunk": chunk_ids[idx],
                    "predicate": c.predicate,
                    "scope": c.scope,
                    "scalar": json.dumps(c.scalar),
                    "from": c.valid_from_ms,
                    "to": c.valid_to_ms,
                    "method": method,
                    "score": c.extraction_score,
                    "state": "accepted" if c.extraction_score >= 0.85 else "pending",
                    "evidence": evid,
                    "start": relative_start,
                    "end": relative_end,
                }
                self.repo.query(
                    """MATCH (e:Entity {id:$subject}),(ch:Chunk {id:$chunk}) MERGE (c:Claim {id:$cid})
                    SET c.predicate=$predicate,c.scope=$scope,c.scalar_json=$scalar,c.valid_from_ms=$from,c.valid_to_ms=$to,
                    c.extraction_method=$method,c.extraction_score=$score,c.review_state=$state,c.evidence_id=$evidence
                    MERGE (c)-[:SUBJECT]->(e) MERGE (c)-[p:SUPPORTED_BY]->(ch) SET p.start=$start,p.end=$end""",
                    params,
                    True,
                )
                if c.object_id:
                    self.repo.query(
                        "MATCH (c:Claim {id:$cid}),(o:Entity {id:$object}) MERGE (c)-[:OBJECT]->(o)",
                        {"cid": cid, "object": c.object_id},
                        True,
                    )
            count = self.repo.query(
                "MATCH (r:SourceRevision {id:$rid})-[:HAS_CHUNK]->(ch)<-[:SUPPORTED_BY]-(c:Claim) RETURN count(c)",
                {"rid": rid},
            )[0][0]
            if count != len(curated):
                raise ValueError("Staged evidence count mismatch")
            # The source pointer, ACL, state and application epoch change in ONE atomic query.
            result = self.repo.query(
                """MATCH (s:Source {id:$sid}),(r:SourceRevision {id:$rid}),(m:GraphMeta {id:'meta'})
                WHERE s.active_revision_id=$old
                SET s.active_revision_id=$rid,s.state='active',s.kind=$kind,s.acl_groups=$acl,s.checksum=$checksum,s.revision_number=$number,
                    r.state='active',m.epoch=m.epoch+1
                RETURN m.epoch""",
                {
                    "sid": env.source_id,
                    "rid": rid,
                    "old": old,
                    "kind": env.kind,
                    "acl": env.acl_groups,
                    "checksum": checksum,
                    "number": number,
                },
                True,
            )
            if not result:
                raise HTTPException(409, "Source changed before activation")
            if old:
                self.repo.query(
                    "MATCH (r:SourceRevision {id:$old}) SET r.state='historical'", {"old": old}, True
                )
            return {
                "revision_id": rid,
                "unchanged": False,
                "accepted": accepted,
                "pending": len(curated) - accepted,
                "unresolved_mentions": unresolved,
                "graph_epoch": result[0][0],
            }

    def seed(self):
        self.repo.initialize(registry())
        manifest = json.loads((FIXTURES / "manifest.json").read_text())
        results = []
        for item in manifest["sources"]:
            raw = (FIXTURES / item["path"]).read_bytes()
            if sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("Fixture checksum mismatch")
            record = json.loads(raw)
            env = SourceEnvelope.model_validate(record["envelope"])
            # Seed never rolls back a user revision.
            if self.repo.source(env.source_id):
                continue
            results.append(
                self.import_source(
                    env, "operator", [Candidate.model_validate(c) for c in record["claims"]], True
                )
            )
        from app.work.service import Work
        Work(self.repo, self.store).seed()
        return results
