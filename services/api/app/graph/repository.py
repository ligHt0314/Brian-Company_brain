import json
import threading
import time
from app.domain.models import uid

from falkordb import FalkorDB
from redis.exceptions import ResponseError
from app.config import settings
from app.domain.models import Claim, Evidence, iso, ms

from app.observability import event

# Every claim query joins its own source policy. Never filter only the first edge of a path.
CLAIMS_QUERY = """
MATCH (s:Source)-[:HAS_REVISION]->(r:SourceRevision)-[:HAS_CHUNK]->(ch:Chunk)
MATCH (c:Claim)-[support:SUPPORTED_BY]->(ch)
MATCH (c)-[:SUBJECT]->(subject:Entity)
WHERE s.id IN $allowed AND s.state = 'active' AND s.active_revision_id = r.id
 AND c.review_state = 'accepted'
 AND (c.valid_from_ms IS NULL OR c.valid_from_ms <= $clock)
 AND (c.valid_to_ms IS NULL OR c.valid_to_ms > $clock)
OPTIONAL MATCH (c)-[:OBJECT]->(object:Entity)
RETURN c, subject.id, object.id, ch, r, s, support.start, support.end
ORDER BY c.id LIMIT 2001
"""


class Repository:
    def __init__(self, graph_name: str | None = None):
        self._db = None
        self.graph_name = graph_name or settings.falkordb_graph
        self.lock = threading.RLock()
        self.local = threading.local()

    @property
    def db(self):
        if self._db is None:
            self._db = FalkorDB(
                host=settings.falkordb_host,
                port=settings.falkordb_port,
                password=settings.falkordb_password,
                socket_timeout=3,
                socket_connect_timeout=3,
            )
        return self._db

    @property
    def graph(self):
        return self.db.select_graph(self.graph_name)

    def query(self, text: str, params: dict | None = None, write: bool = False):
        self.local.count = getattr(self.local, "count", 0) + 1
        method = self.graph.query if write else self.graph.ro_query
        started = time.monotonic()
        try:
            return method(text, params=params or {}, timeout=settings.graph_query_timeout_ms).result_set
        finally:
            duration = (time.monotonic() - started) * 1000
            self.local.duration_ms = getattr(self.local, "duration_ms", 0) + duration
            event("graph_query", template=uid("query", text), duration_ms=round(duration, 3), write=write)

    def initialize(self, entities: list[dict]):
        with self.lock:
            self.query(
                "MERGE (m:GraphMeta {id:'meta'}) ON CREATE SET m.epoch=0, m.schema_version='1.0'", write=True
            )
            for label in ["Entity", "Source", "SourceRevision", "Chunk", "Claim", "ReviewTask"]:
                try:
                    self.query(f"CREATE INDEX FOR (n:{label}) ON (n.id)", write=True)
                except ResponseError as exc:
                    if "already indexed" not in str(exc):
                        raise
            for entity in entities:
                self.query(
                    "MERGE (e:Entity {id:$id}) SET e.kind=$kind,e.label=$label,e.canonical_key=$id,e.aliases=$aliases",
                    entity,
                    True,
                )

    def epoch(self) -> int:
        rows = self.query("MATCH (m:GraphMeta {id:'meta'}) RETURN m.epoch")
        return int(rows[0][0]) if rows else 0

    def sources(self, groups: list[str]) -> list[dict]:
        rows = self.query(
            """MATCH (s:Source)-[:HAS_REVISION]->(r:SourceRevision)
            WHERE s.state='active' AND s.active_revision_id=r.id
            AND any(g IN s.acl_groups WHERE g IN $groups)
            RETURN s,r ORDER BY r.title""",
            {"groups": groups},
        )
        return [dict(s.properties, revision=r.properties) for s, r in rows]

    def source(self, id: str) -> dict | None:
        rows = self.query("MATCH (s:Source {id:$id}) RETURN s", {"id": id})
        source = rows[0][0].properties if rows else None
        return source if source and source.get("active_revision_id") else None

    def claims(self, allowed: list[str]) -> tuple[list[Claim], bool]:
        rows = self.query(CLAIMS_QUERY, {"allowed": allowed, "clock": ms(settings.demo_clock_iso)})
        claims = []
        for c, subject, obj, ch, r, s, start, end in rows[:2000]:
            c, ch, r, s = [x.properties for x in [c, ch, r, s]]
            stale_days = {"ticket": 7, "chat": 7, "document": 30, "directory": 30, "decision": 90}[s["kind"]]
            ev = Evidence(
                id=c["evidence_id"],
                claim_id=c["id"],
                source_id=s["id"],
                revision_id=r["id"],
                chunk_id=ch["id"],
                quote=ch["text"][start:end],
                start=start,
                end=end,
                source_title=r["title"],
                source_kind=s["kind"],
                source_updated_at=iso(r["source_updated_at_ms"]),
                indexed_at=iso(r["indexed_at_ms"]),
                extraction_method=c["extraction_method"],
                ingestion_mode=r["ingestion_mode"],
                is_current=True,
                is_stale=ms(settings.demo_clock_iso) - r["source_updated_at_ms"] > stale_days * 86400000,
            )
            claims.append(
                Claim(
                    id=c["id"],
                    subject_id=subject,
                    object_id=obj,
                    predicate=c["predicate"],
                    scalar=json.loads(c["scalar_json"]),
                    scope=c["scope"],
                    evidence=ev,
                )
            )
        return claims, len(rows) > 2000

    def evidence(self, id: str, allowed: list[str]) -> dict | None:
        rows = self.query(
            """MATCH (s:Source)-[:HAS_REVISION]->(r:SourceRevision)-[:HAS_CHUNK]->(ch:Chunk)
            MATCH (c:Claim)-[p:SUPPORTED_BY]->(ch)
            WHERE c.evidence_id=$id AND s.id IN $allowed AND s.state='active'
            RETURN c,ch,r,s,p.start,p.end""",
            {"id": id, "allowed": allowed},
        )
        if not rows:
            return None
        c, ch, r, s, start, end = rows[0]
        c, ch, r, s = [n.properties for n in [c, ch, r, s]]
        return {
            "id": id,
            "claim_id": c["id"],
            "source_id": s["id"],
            "revision_id": r["id"],
            "chunk_id": ch["id"],
            "quote": ch["text"][start:end],
            "start": start,
            "end": end,
            "source_title": r["title"],
            "source_kind": s["kind"],
            "source_updated_at": iso(r["source_updated_at_ms"]),
            "indexed_at": iso(r["indexed_at_ms"]),
            "extraction_method": c["extraction_method"],
            "ingestion_mode": r["ingestion_mode"],
            "is_stale": ms(settings.demo_clock_iso) - r["source_updated_at_ms"]
            > {"ticket": 7, "chat": 7, "document": 30, "directory": 30, "decision": 90}[s["kind"]] * 86400000,
            "is_current": s["active_revision_id"] == r["id"],
        }

    def revisions(self, source_id: str) -> list[dict]:
        rows = self.query(
            "MATCH (s:Source {id:$id})-[:HAS_REVISION]->(r:SourceRevision) RETURN r ORDER BY r.revision_number DESC",
            {"id": source_id},
        )
        return [r[0].properties for r in rows]

    def tasks(self) -> list[dict]:
        return [
            json.loads(row[0])
            for row in self.query("MATCH (t:ReviewTask) RETURN t.payload ORDER BY t.created_at_ms DESC")
        ]
