"use client";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  CheckCheck,
  Clock,
  FileText,
  GitBranch,
  Plus,
  RefreshCw,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import { api, post, type Entity, type Me } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";

type Meeting = components["schemas"]["Meeting"];
type Action = components["schemas"]["Action"];
type Detail = components["schemas"]["MeetingDetail"];
type Recap = components["schemas"]["Recap-Output"];
type Draft = components["schemas"]["RecapDraft"];
type Brief = components["schemas"]["Brief"];
const statuses = [
  "open",
  "in_progress",
  "blocked",
  "done",
  "cancelled",
] as const;
const done = (a: Action) => a.status === "done" || a.status === "cancelled";
const date = (s: string) =>
  new Date(s).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
const message = (e: unknown) =>
  e instanceof Error ? e.message : "The request could not complete.";

function historyText(
  event: { event: string; detail: string },
  labels: Record<string, string>,
  meetings: Meeting[],
) {
  if (event.event === "action_carried_forward")
    return `Continued in ${meetings.find((m) => m.id === event.detail)?.title || "a follow-up session"}.`;
  if (event.event === "action_added")
    return "An evidence-backed action was added to this session.";
  try {
    const change = JSON.parse(event.detail) as {
      owner_id?: string | null;
      due_date?: string | null;
      status?: string;
      outcome?: string;
    };
    if (event.event === "action_reassigned")
      return change.owner_id
        ? `Assigned to ${labels[change.owner_id] || "a colleague"}.`
        : "The action is now unassigned.";
    if (event.event === "action_closed")
      return `Closed as ${change.status || "complete"}. ${change.outcome || ""}`;
    const details = [];
    if (change.status)
      details.push(`Status: ${change.status.replaceAll("_", " ")}`);
    if ("due_date" in change)
      details.push(
        change.due_date ? `Due ${date(change.due_date)}` : "Due date cleared",
      );
    if (change.outcome) details.push(change.outcome);
    return details.join(". ") || "Action details updated.";
  } catch {
    return event.detail.replaceAll("_", " ");
  }
}

function Dialog({
  title,
  close,
  children,
}: {
  title: string;
  close: () => void;
  children: React.ReactNode;
}) {
  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [close]);
  return (
    <div className="work-overlay" onClick={close}>
      <section
        className="work-dialog"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <h2>{title}</h2>
          <button className="iconButton" aria-label="Close" onClick={close}>
            <X size={20} />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}

export default function MeetingsWorkspace({
  me,
  entities,
  mode,
}: {
  me: Me;
  entities: Entity[];
  mode: "meetings" | "actions";
}) {
  const router = useRouter();
  const params = useSearchParams();
  const [meetings, setMeetings] = useState<Meeting[]>([]),
    [actions, setActions] = useState<Action[]>([]);
  const [detail, setDetail] = useState<Detail | null>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState("");
  const [query, setQuery] = useState(""),
    [project, setProject] = useState(""),
    [kind, setKind] = useState(""),
    [owner, setOwner] = useState(""),
    [state, setState] = useState(params.get("status") || "open");
  useEffect(() => setState(params.get("status") || "open"), [params]);
  const [create, setCreate] = useState(false),
    [follow, setFollow] = useState<Detail | null>(null);
  const [draft, setDraft] = useState<Recap | null>(null),
    [draftId, setDraftId] = useState<string | null>(null);
  const [brief, setBrief] = useState<Brief | null>(null),
    [recipient, setRecipient] = useState("");
  const [editing, setEditing] = useState<Action | null>(null),
    [adding, setAdding] = useState(false);
  const [notesOpen, setNotesOpen] = useState(false);
  const people = entities.filter((e) => e.kind === "Person"),
    projects = entities.filter((e) => e.kind === "Project");
  const labels = Object.fromEntries(entities.map((e) => [e.id, e.label]));
  const canWrite = me.capabilities.includes("review");
  const refresh = useCallback(async () => {
    const [ms, as] = await Promise.all([
      api<Meeting[]>("/meetings"),
      api<Action[]>("/actions"),
    ]);
    setMeetings(ms);
    setActions(as);
  }, []);
  useEffect(() => {
    setDetail(null);
    setError("");
    refresh().catch((e) => setError(message(e)));
  }, [me.id, mode, refresh]);
  async function open(id: string) {
    setError("");
    try {
      setDetail(await api<Detail>(`/meetings/${encodeURIComponent(id)}`));
    } catch (e) {
      setDetail(null);
      setError(message(e));
    }
  }
  async function run(name: string, f: () => Promise<void>) {
    setBusy(name);
    setError("");
    try {
      await f();
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy("");
    }
  }
  const overdue = actions.filter(
    (a) =>
      !done(a) &&
      a.due_date &&
      a.due_date < new Date().toISOString().slice(0, 10),
  );
  const visible = meetings.filter(
    (m) =>
      (!project || m.project_id === project) &&
      (!kind || m.kind === kind) &&
      `${m.title} ${m.summary} ${labels[m.project_id]}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const filteredActions = actions.filter(
    (a) =>
      (!owner || a.owner_id === owner) &&
      (state === "carried"
        ? a.meeting_ids.length > 1
        : state === "all" || state === "overdue"
          ? state !== "overdue" || overdue.some((o) => o.id === a.id)
          : state === "open"
            ? !done(a)
            : a.status === state) &&
      (!query ||
        `${a.title} ${a.outcome}`.toLowerCase().includes(query.toLowerCase())),
  );
  function actionRows(rows: Action[]) {
    return rows.length ? (
      <div className="work-action-list">
        {rows.map((a) => (
          <article
            key={a.id}
            className={`work-action ${done(a) ? "is-done" : ""}`}
          >
            <div className="work-action-icon">
              <CheckCheck size={18} />
            </div>
            <div className="work-action-content">
              <h3>{a.title}</h3>
              <p>
                {a.owner_id ? labels[a.owner_id] : "Unassigned"} <span>·</span>{" "}
                {a.due_date ? `Due ${date(a.due_date)}` : "No due date"}{" "}
                <span>·</span>{" "}
                <span className={`work-status ${a.status}`}>
                  {a.status.replaceAll("_", " ")}
                </span>
                {overdue.some((o) => o.id === a.id) && (
                  <strong className="work-overdue">Overdue</strong>
                )}
              </p>
              {a.outcome && (
                <p className="work-outcome">Outcome: {a.outcome}</p>
              )}
              <details>
                <summary>
                  Evidence &amp; history · {a.history.length} events
                  {a.meeting_ids.length > 1
                    ? ` · carried through ${a.meeting_ids.length} sessions`
                    : ""}
                </summary>
                <blockquote>{a.quote}</blockquote>
                <button
                  className="textButton"
                  onClick={() => open(a.origin_meeting_id)}
                >
                  Open original notes <ArrowRight size={14} />
                </button>
                <ol className="work-history">
                  {a.history.map((h, i) => (
                    <li key={i}>
                      <strong>{h.event.replaceAll("_", " ")}</strong>
                      <small>
                        {date(h.at)} ·{" "}
                        {(
                          {
                            demo_lead: "Lead",
                            demo_engineer: "Engineer",
                            demo_viewer: "Viewer",
                            seed: "Workspace record",
                            operator: "Operator",
                          } as Record<string, string>
                        )[h.actor] || "Workspace member"}
                      </small>
                      <p>{historyText(h, labels, meetings)}</p>
                    </li>
                  ))}
                </ol>
              </details>
            </div>
            {canWrite && (
              <button className="secondary" onClick={() => setEditing(a)}>
                Update
              </button>
            )}
          </article>
        ))}
      </div>
    ) : (
      <div className="work-empty">
        <CheckCheck size={28} />
        <h3>No actions in this view</h3>
        <p>Adjust the filters or add an action from a meeting.</p>
      </div>
    );
  }
  return (
    <div className="work-root">
      <div className="pageHeading">
        <div>
          <div className="eyebrow">DIGIPLUS SERVICES / TEAM CONTINUITY</div>
          <h1>
            {detail
              ? detail.meeting.title
              : mode === "actions"
                ? "Every commitment, followed through."
                : "Keep the context. Move work forward."}
          </h1>
          <p>
            {detail
              ? `${labels[detail.meeting.project_id]} · ${date(detail.meeting.scheduled_at)}`
              : "Meetings, handovers and the work between them, connected to your company knowledge."}
          </p>
        </div>
        <div className="work-toolbar">
          {detail && (
            <button className="secondary" onClick={() => setDetail(null)}>
              <ArrowLeft size={16} /> All sessions
            </button>
          )}
          {canWrite && (
            <button
              className="primary"
              onClick={() => {
                setFollow(null);
                setCreate(true);
              }}
            >
              <Plus size={16} /> New session
            </button>
          )}
        </div>
      </div>
      {error && (
        <div role="alert" className="work-alert">
          {error}
          <button onClick={() => setError("")} aria-label="Dismiss error">
            <X size={16} />
          </button>
        </div>
      )}
      {busy && (
        <div className="work-progress" role="status">
          <RefreshCw size={16} className="spin" /> {busy}…
        </div>
      )}
      {!detail ? (
        <>
          <div className="work-stats">
            <button onClick={() => router.push("/meetings")}>
              <CalendarDays />
              <strong>{meetings.length}</strong>
              <span>Meetings &amp; handovers</span>
            </button>
            <button onClick={() => router.push("/actions?status=open")}>
              <CheckCheck />
              <strong>{actions.filter((a) => !done(a)).length}</strong>
              <span>Open action items</span>
            </button>
            <button onClick={() => router.push("/actions?status=overdue")}>
              <Clock />
              <strong>{overdue.length}</strong>
              <span>Need follow-up</span>
            </button>
            <button onClick={() => router.push("/actions?status=carried")}>
              <GitBranch />
              <strong>
                {actions.filter((a) => a.meeting_ids.length > 1).length}
              </strong>
              <span>Actions carried forward</span>
            </button>
          </div>
          <div className="work-intro">
            <div>
              <span className="sectionEyebrow">EVIDENCE-BACKED HANDOVERS</span>
              <h2>Nothing gets lost between people.</h2>
              <p>
                Trace an action back to the original notes. Carry unfinished
                work forward with its owner, due date and full history.
              </p>
            </div>
            <Link href="/investigate" className="secondary">
              Explore company knowledge <ArrowRight size={16} />
            </Link>
          </div>
          <div className="work-filters">
            <input
              aria-label="Search work"
              placeholder="Search sessions or action items…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            {mode === "meetings" ? (
              <>
                <select
                  aria-label="Project filter"
                  value={project}
                  onChange={(e) => setProject(e.target.value)}
                >
                  <option value="">All client projects</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <select
                  aria-label="Session type"
                  value={kind}
                  onChange={(e) => setKind(e.target.value)}
                >
                  <option value="">Meetings &amp; handovers</option>
                  <option value="meeting">Meetings</option>
                  <option value="handover">Handovers</option>
                </select>
              </>
            ) : (
              <>
                <select
                  aria-label="Action owner filter"
                  value={owner}
                  onChange={(e) => setOwner(e.target.value)}
                >
                  <option value="">All owners</option>
                  {people.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <select
                  aria-label="Action status filter"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                >
                  <option value="open">All open work</option>
                  <option value="overdue">Overdue</option>
                  <option value="carried">Carried forward</option>
                  <option value="all">All statuses</option>
                  {statuses
                    .filter((s) => s !== "open")
                    .map((s) => (
                      <option key={s} value={s}>
                        {s.replaceAll("_", " ")}
                      </option>
                    ))}
                </select>
              </>
            )}
            <button
              className="secondary"
              onClick={() => run("Refreshing", refresh)}
            >
              <RefreshCw size={15} />
            </button>
          </div>
          {mode === "actions" ? (
            actionRows(filteredActions)
          ) : visible.length ? (
            <div className="work-grid">
              {visible.map((m) => {
                const pending = actions.filter(
                  (a) => m.action_ids.includes(a.id) && !done(a),
                );
                return (
                  <button
                    key={m.id}
                    className="work-session"
                    onClick={() => open(m.id)}
                  >
                    <div className="work-session-top">
                      <span className={`work-kind ${m.kind}`}>
                        {m.kind === "handover" ? "Handover" : "Meeting"}
                      </span>
                      <span className="work-date">{date(m.scheduled_at)}</span>
                    </div>
                    <h3>{m.title}</h3>
                    <p>{m.summary || m.agenda}</p>
                    <div className="work-session-meta">
                      <span>
                        <Users size={14} /> {m.participant_ids.length} invited
                        {m.absent_ids.length
                          ? ` · ${m.absent_ids.length} absent`
                          : ""}
                      </span>
                      <span>{pending.length} open actions</span>
                    </div>
                    <footer>
                      <span>
                        {m.status.replaceAll("_", " ")}
                        {!m.recap_confirmed && m.notes
                          ? " · recap to review"
                          : ""}
                      </span>
                      <ArrowRight size={16} />
                    </footer>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="work-empty">
              <h3>No sessions found</h3>
              <p>Create a meeting or change your filters.</p>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="work-detail-grid">
            <section className="work-panel">
              <div className="work-panel-heading">
                <h2>Session context</h2>
                <span className="work-kind">
                  {detail.meeting.status.replaceAll("_", " ")}
                </span>
              </div>
              <p className="work-lead">
                {detail.meeting.summary ||
                  "No confirmed recap yet. Generate one from the notes or enter a reviewed recap manually."}
              </p>
              <h3>Agenda</h3>
              <p className="work-pre">
                {detail.meeting.agenda || "No agenda recorded."}
              </p>
              <h3>People</h3>
              <div className="work-chips">
                {detail.meeting.participant_ids.map((p) => (
                  <span key={p}>
                    {labels[p]}
                    {detail.meeting.absent_ids.includes(p) ? " · absent" : ""}
                  </span>
                ))}
              </div>
              {detail.meeting.previous_meeting_id && (
                <button
                  className="textButton"
                  onClick={() => open(detail.meeting.previous_meeting_id!)}
                >
                  <ArrowLeft size={14} /> Previous session
                </button>
              )}
              <h3>Decisions</h3>
              {detail.meeting.decisions.length ? (
                detail.meeting.decisions.map((d, i) => (
                  <div className="work-decision" key={i}>
                    <p>{d.text}</p>
                    <details>
                      <summary>Source passage</summary>
                      <blockquote>{d.quote}</blockquote>
                    </details>
                  </div>
                ))
              ) : (
                <p className="work-muted">No reviewed decisions recorded.</p>
              )}
              <h3>Linked knowledge</h3>
              {detail.meeting.knowledge_links.map((l) => (
                <details className="work-knowledge" key={l.source_id}>
                  <summary>{l.title}</summary>
                  <blockquote>{l.quote}</blockquote>
                  <Link href="/sources">Browse sources →</Link>
                </details>
              ))}
              {!detail.meeting.knowledge_links.length && (
                <p className="work-muted">
                  Generate a recap to suggest relevant company documents.
                </p>
              )}
            </section>
            <aside className="work-panel work-next">
              <span className="sectionEyebrow">NEXT STEPS</span>
              <h2>Continue the conversation.</h2>
              {canWrite &&
                !detail.meeting.recap_confirmed &&
                detail.meeting.status !== "archived" && (
                  <>
                    <button
                      className="primary"
                      disabled={!!busy || !detail.meeting.notes.trim()}
                      onClick={() =>
                        run("Generating recap", async () => {
                          const d = await post<Draft>(
                            `/meetings/${encodeURIComponent(detail.meeting.id)}/recap`,
                            {},
                          );
                          setDraft(d.recap);
                          setDraftId(d.id);
                        })
                      }
                    >
                      <Sparkles size={16} /> Generate AI recap
                    </button>
                    <button
                      className="secondary"
                      onClick={() => {
                        setDraft({
                          summary: "",
                          decisions: [],
                          actions: [],
                          knowledge_source_ids: [],
                        });
                        setDraftId(null);
                      }}
                    >
                      Enter recap manually
                    </button>
                  </>
                )}
              <label>
                Catch-up recipient
                <select
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                >
                  <option value="">Choose a colleague</option>
                  {people.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </label>
              <button
                className="secondary"
                disabled={!recipient || !!busy}
                onClick={() =>
                  run("Preparing catch-up brief", async () =>
                    setBrief(
                      await post<Brief>(
                        `/meetings/${encodeURIComponent(detail.meeting.id)}/brief`,
                        { recipient_id: recipient },
                      ),
                    ),
                  )
                }
              >
                <FileText size={16} /> Prepare catch-up brief
              </button>
              <p className="work-muted">
                Preview context for a colleague. Nothing is sent automatically.
              </p>
              {canWrite && (
                <>
                  <button
                    className="secondary"
                    onClick={() => {
                      setFollow(detail);
                      setCreate(true);
                    }}
                  >
                    <GitBranch size={16} /> Create follow-up / handover
                  </button>
                  <label>
                    Session status
                    <select
                      aria-label="Session lifecycle"
                      value={detail.meeting.status}
                      disabled={!!busy}
                      onChange={(e) =>
                        run("Updating session", async () => {
                          const meeting = await api<Meeting>(
                            `/meetings/${encodeURIComponent(detail.meeting.id)}`,
                            {
                              method: "PATCH",
                              body: JSON.stringify({
                                expected_version: detail.meeting.version,
                                status: e.target.value,
                              }),
                            },
                          );
                          setDetail({ ...detail, meeting });
                          await refresh();
                        })
                      }
                    >
                      {["planned", "in_progress", "completed", "archived"].map(
                        (s) => (
                          <option key={s} value={s}>
                            {s.replaceAll("_", " ")}
                          </option>
                        ),
                      )}
                    </select>
                  </label>
                </>
              )}
            </aside>
          </div>
          <section className="work-panel">
            <div className="work-panel-heading">
              <div>
                <h2>Action items</h2>
                <p>
                  Original evidence and ownership history stay attached across
                  sessions.
                </p>
              </div>
              {canWrite && detail.meeting.status !== "archived" && (
                <button className="secondary" onClick={() => setAdding(true)}>
                  <Plus size={16} /> Add action
                </button>
              )}
            </div>
            {actionRows(detail.actions)}
          </section>
          <section className="work-panel">
            <div className="work-panel-heading">
              <h2>Original notes</h2>
              {canWrite &&
                !detail.meeting.recap_confirmed &&
                detail.meeting.status !== "archived" && (
                  <button
                    className="secondary"
                    onClick={() => setNotesOpen(true)}
                  >
                    Update notes
                  </button>
                )}
            </div>
            <pre className="work-notes">
              {detail.meeting.notes ||
                "No notes recorded. Create a new session with meeting notes to generate a recap."}
            </pre>
          </section>
          <details className="work-panel">
            <summary>
              Session activity · {detail.meeting.history.length} events
            </summary>
            <ol className="work-history">
              {detail.meeting.history.map((h, i) => (
                <li key={i}>
                  <strong>{h.event.replaceAll("_", " ")}</strong>
                  <small>
                    {date(h.at)} ·{" "}
                    {(
                      {
                        demo_lead: "Lead",
                        demo_engineer: "Engineer",
                        demo_viewer: "Viewer",
                        seed: "Workspace record",
                        operator: "Operator",
                      } as Record<string, string>
                    )[h.actor] || "Workspace member"}
                  </small>
                  <p>{historyText(h, labels, meetings)}</p>
                </li>
              ))}
            </ol>
          </details>
        </>
      )}
      {create && (
        <CreateDialog
          people={people}
          projects={projects}
          follow={follow}
          close={() => setCreate(false)}
          save={async (body) => {
            const m = await post<Meeting>("/meetings", body);
            setCreate(false);
            await refresh();
            await open(m.id);
          }}
        />
      )}
      {draft && detail && (
        <RecapDialog
          recap={draft}
          people={people}
          notes={detail.meeting.notes}
          close={() => setDraft(null)}
          save={async (recap) => {
            const d = await post<Detail>(
              `/meetings/${encodeURIComponent(detail.meeting.id)}/confirm-recap`,
              {
                expected_version: detail.meeting.version,
                draft_id: draftId,
                recap,
              },
            );
            setDetail(d);
            setDraft(null);
            await refresh();
          }}
        />
      )}
      {editing && (
        <ActionDialog
          action={editing}
          people={people}
          close={() => setEditing(null)}
          save={async (body) => {
            await api(`/actions/${encodeURIComponent(editing.id)}`, {
              method: "PATCH",
              body: JSON.stringify({
                ...body,
                expected_version: editing.version,
              }),
            });
            setEditing(null);
            await refresh();
            if (detail) await open(detail.meeting.id);
          }}
        />
      )}
      {adding && detail && (
        <AddActionDialog
          people={people}
          notes={detail.meeting.notes}
          close={() => setAdding(false)}
          save={async (body) => {
            await post(
              `/meetings/${encodeURIComponent(detail.meeting.id)}/actions`,
              { ...body, expected_version: detail.meeting.version },
            );
            setAdding(false);
            await refresh();
            await open(detail.meeting.id);
          }}
        />
      )}
      {notesOpen && detail && (
        <NotesDialog
          meeting={detail.meeting}
          close={() => setNotesOpen(false)}
          save={async (notes, agenda) => {
            const meeting = await api<Meeting>(
              `/meetings/${encodeURIComponent(detail.meeting.id)}/notes`,
              {
                method: "PATCH",
                body: JSON.stringify({
                  expected_version: detail.meeting.version,
                  notes,
                  agenda,
                }),
              },
            );
            setDetail({ ...detail, meeting });
            setNotesOpen(false);
            await refresh();
          }}
        />
      )}
      {brief && (
        <Dialog title="Catch-up brief" close={() => setBrief(null)}>
          <span className="work-kind">
            {brief.mode === "live_model"
              ? "AI-generated · review before sharing"
              : "Saved context"}
          </span>
          {brief.warning && <p className="work-alert">{brief.warning}</p>}
          {brief.blocks.map((b, i) => (
            <div className="work-brief-block" key={i}>
              <p>{b.text}</p>
              {b.reference_ids.map((id) => (
                <details key={id}>
                  <summary>
                    Supporting context ·{" "}
                    {id.startsWith("action:") || id.startsWith("action_")
                      ? "action item"
                      : "source"}
                  </summary>
                  <blockquote>{brief.references[id]}</blockquote>
                </details>
              ))}
            </div>
          ))}
          <h3>What changed across sessions</h3>
          {brief.changes.length ? (
            brief.changes.map((h, i) => (
              <p className="work-change" key={i}>
                {h.event.replaceAll("_", " ")} ·{" "}
                {historyText(h, labels, meetings)}
              </p>
            ))
          ) : (
            <p>No carry-forward or reassignment events recorded.</p>
          )}
          <p className="work-muted">
            This preview has not been sent to the recipient.
          </p>
        </Dialog>
      )}
    </div>
  );
}

function CreateDialog({
  people,
  projects,
  follow,
  close,
  save,
}: {
  people: Entity[];
  projects: Entity[];
  follow: Detail | null;
  close: () => void;
  save: (body: Record<string, unknown>) => Promise<void>;
}) {
  const [title, setTitle] = useState(
      follow ? `${follow.meeting.title.split(" · ")[0]} · Follow-up` : "",
    ),
    [kind, setKind] = useState("meeting"),
    [project, setProject] = useState(
      follow?.meeting.project_id || projects[0]?.id || "",
    ),
    [agenda, setAgenda] = useState(
      follow?.actions
        .filter((a) => !done(a))
        .map((a) => `Review: ${a.title}`)
        .join("\n") || "",
    ),
    [notes, setNotes] = useState(""),
    [at, setAt] = useState(
      new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16),
    ),
    [participants, setParticipants] = useState<string[]>(
      follow?.meeting.participant_ids || [],
    ),
    [absent, setAbsent] = useState<string[]>([]),
    [carry, setCarry] = useState<string[]>(
      follow?.actions.filter((a) => !done(a)).map((a) => a.id) || [],
    ),
    [group, setGroup] = useState("engineering"),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <Dialog
      title={
        follow
          ? "Continue work in a new session"
          : "Create a meeting or handover"
      }
      close={close}
    >
      <form
        className="work-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setError("");
          try {
            await save({
              title,
              kind,
              project_id: project,
              agenda,
              notes,
              scheduled_at: new Date(at).toISOString(),
              participant_ids: participants,
              absent_ids: absent,
              acl_groups: follow?.meeting.acl_groups || [group],
              previous_meeting_id: follow?.meeting.id || null,
              carry_action_ids: carry,
            });
          } catch (e) {
            setError(message(e));
          } finally {
            setBusy(false);
          }
        }}
      >
        {error && (
          <p role="alert" className="work-alert">
            {error}
          </p>
        )}
        <label>
          Session title
          <input
            required
            minLength={3}
            maxLength={200}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
        <div className="work-form-row">
          <label>
            Session kind
            <select value={kind} onChange={(e) => setKind(e.target.value)}>
              <option value="meeting">Meeting</option>
              <option value="handover">Work handover</option>
            </select>
          </label>
          <label>
            Scheduled time
            <input
              type="datetime-local"
              required
              value={at}
              onChange={(e) => setAt(e.target.value)}
            />
          </label>
        </div>
        <label>
          Client project
          <select
            disabled={!!follow}
            value={project}
            onChange={(e) => setProject(e.target.value)}
          >
            {projects.map((p) => (
              <option value={p.id} key={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Agenda
          <textarea
            rows={3}
            value={agenda}
            onChange={(e) => setAgenda(e.target.value)}
          />
        </label>
        <label>
          Meeting notes / handover context
          <textarea
            rows={7}
            maxLength={50000}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Paste the discussion, decisions and action commitments. Include names and dates when known."
          />
        </label>
        <fieldset>
          <legend>Participants and attendance</legend>
          <div className="work-people-pick">
            {people.map((p) => (
              <div key={p.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={participants.includes(p.id)}
                    onChange={(e) => {
                      setParticipants(
                        e.target.checked
                          ? [...participants, p.id]
                          : participants.filter((id) => id !== p.id),
                      );
                      if (!e.target.checked)
                        setAbsent(absent.filter((id) => id !== p.id));
                    }}
                  />
                  {p.label}
                </label>
                {participants.includes(p.id) && (
                  <label className="work-absent">
                    <input
                      type="checkbox"
                      checked={absent.includes(p.id)}
                      onChange={(e) =>
                        setAbsent(
                          e.target.checked
                            ? [...absent, p.id]
                            : absent.filter((id) => id !== p.id),
                        )
                      }
                    />
                    Absent
                  </label>
                )}
              </div>
            ))}
          </div>
        </fieldset>
        {follow ? (
          <fieldset>
            <legend>Carry unfinished work forward</legend>
            {follow.actions
              .filter((a) => !done(a))
              .map((a) => (
                <label className="work-check" key={a.id}>
                  <input
                    type="checkbox"
                    checked={carry.includes(a.id)}
                    onChange={(e) =>
                      setCarry(
                        e.target.checked
                          ? [...carry, a.id]
                          : carry.filter((id) => id !== a.id),
                      )
                    }
                  />
                  {a.title}
                </label>
              ))}
            <p className="work-muted">
              Existing action IDs, due dates and history are preserved. Access
              stays the same as the previous session.
            </p>
          </fieldset>
        ) : (
          <label>
            Source access
            <select value={group} onChange={(e) => setGroup(e.target.value)}>
              <option value="engineering">Delivery teams</option>
              <option value="all_employees">All employees</option>
              <option value="leadership">Leadership</option>
            </select>
          </label>
        )}
        <button className="primary" disabled={busy || !participants.length}>
          {busy ? "Saving…" : "Save session"}
        </button>
      </form>
    </Dialog>
  );
}

function RecapDialog({
  recap,
  people,
  notes,
  close,
  save,
}: {
  recap: Recap;
  people: Entity[];
  notes: string;
  close: () => void;
  save: (recap: Recap) => Promise<void>;
}) {
  const [value, setValue] = useState(recap),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <Dialog title="Review the recap before confirming" close={close}>
      <form
        className="work-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setError("");
          setBusy(true);
          try {
            await save(value);
          } catch (e) {
            setError(message(e));
          } finally {
            setBusy(false);
          }
        }}
      >
        <p>
          Check the summary, owners and due dates. Each decision and action must
          include its exact supporting passage from the notes.
        </p>
        {error && (
          <p role="alert" className="work-alert">
            {error}
          </p>
        )}
        <details>
          <summary>Original notes</summary>
          <pre className="work-notes">{notes}</pre>
        </details>
        <label>
          Summary
          <textarea
            required
            rows={4}
            value={value.summary}
            onChange={(e) => setValue({ ...value, summary: e.target.value })}
          />
        </label>
        <h3>Decisions</h3>
        {value.decisions.map((d, i) => (
          <fieldset key={i}>
            <label>
              Decision
              <input
                required
                value={d.text}
                onChange={(e) =>
                  setValue({
                    ...value,
                    decisions: value.decisions.map((x, j) =>
                      j === i ? { ...x, text: e.target.value } : x,
                    ),
                  })
                }
              />
            </label>
            <label>
              Exact passage
              <textarea
                required
                value={d.quote}
                onChange={(e) =>
                  setValue({
                    ...value,
                    decisions: value.decisions.map((x, j) =>
                      j === i ? { ...x, quote: e.target.value } : x,
                    ),
                  })
                }
              />
            </label>
            <button
              type="button"
              className="textButton"
              onClick={() =>
                setValue({
                  ...value,
                  decisions: value.decisions.filter((_, j) => i !== j),
                })
              }
            >
              Remove decision
            </button>
          </fieldset>
        ))}
        <button
          type="button"
          className="secondary"
          onClick={() =>
            setValue({
              ...value,
              decisions: [...value.decisions, { text: "", quote: "" }],
            })
          }
        >
          Add decision
        </button>
        <h3>Proposed actions</h3>
        {value.actions.map((a, i) => (
          <fieldset key={i}>
            <label>
              Action
              <input
                required
                value={a.text}
                onChange={(e) =>
                  setValue({
                    ...value,
                    actions: value.actions.map((x, j) =>
                      j === i ? { ...x, text: e.target.value } : x,
                    ),
                  })
                }
              />
            </label>
            <div className="work-form-row">
              <label>
                Owner
                <select
                  value={a.owner_id || ""}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      actions: value.actions.map((x, j) =>
                        j === i
                          ? { ...x, owner_id: e.target.value || null }
                          : x,
                      ),
                    })
                  }
                >
                  <option value="">Unassigned</option>
                  {people.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Due date
                <input
                  type="date"
                  value={a.due_date || ""}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      actions: value.actions.map((x, j) =>
                        j === i
                          ? { ...x, due_date: e.target.value || null }
                          : x,
                      ),
                    })
                  }
                />
              </label>
            </div>
            <label>
              Exact supporting passage
              <textarea
                required
                value={a.quote}
                onChange={(e) =>
                  setValue({
                    ...value,
                    actions: value.actions.map((x, j) =>
                      j === i ? { ...x, quote: e.target.value } : x,
                    ),
                  })
                }
              />
            </label>
            <button
              type="button"
              className="textButton"
              onClick={() =>
                setValue({
                  ...value,
                  actions: value.actions.filter((_, j) => i !== j),
                })
              }
            >
              Remove action
            </button>
          </fieldset>
        ))}
        <button
          type="button"
          className="secondary"
          onClick={() =>
            setValue({
              ...value,
              actions: [
                ...value.actions,
                { text: "", quote: "", owner_id: null, due_date: null },
              ],
            })
          }
        >
          Add action
        </button>
        {value.knowledge_source_ids.length > 0 && (
          <details>
            <summary>
              {value.knowledge_source_ids.length} suggested knowledge links
            </summary>
            {value.knowledge_source_ids.map((id) => (
              <label className="work-check" key={id}>
                <input
                  type="checkbox"
                  checked
                  onChange={() =>
                    setValue({
                      ...value,
                      knowledge_source_ids: value.knowledge_source_ids.filter(
                        (x) => x !== id,
                      ),
                    })
                  }
                />
                {id}
              </label>
            ))}
          </details>
        )}
        <button className="primary" disabled={busy}>
          {busy ? "Confirming…" : "Confirm recap & action items"}
        </button>
      </form>
    </Dialog>
  );
}

function ActionDialog({
  action,
  people,
  close,
  save,
}: {
  action: Action;
  people: Entity[];
  close: () => void;
  save: (body: Record<string, unknown>) => Promise<void>;
}) {
  const [owner, setOwner] = useState(action.owner_id || ""),
    [due, setDue] = useState(action.due_date || ""),
    [status, setStatus] = useState(action.status),
    [outcome, setOutcome] = useState(action.outcome),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  return (
    <Dialog title="Update action item" close={close}>
      <form
        className="work-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          try {
            await save({
              owner_id: owner || null,
              due_date: due || null,
              status,
              outcome,
            });
          } catch (e) {
            setError(message(e));
          } finally {
            setBusy(false);
          }
        }}
      >
        <h3>{action.title}</h3>
        {error && (
          <p role="alert" className="work-alert">
            {error}
          </p>
        )}
        <label>
          Owner
          <select value={owner} onChange={(e) => setOwner(e.target.value)}>
            <option value="">Unassigned</option>
            {people.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Due date
          <input
            type="date"
            value={due}
            onChange={(e) => setDue(e.target.value)}
          />
        </label>
        <label>
          Status
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as Action["status"])}
          >
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s.replaceAll("_", " ")}
              </option>
            ))}
          </select>
        </label>
        <label>
          Outcome / resolution notes
          <textarea
            required={status === "done" || status === "cancelled"}
            rows={4}
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            placeholder="What happened? Record the result or reason for cancellation."
          />
        </label>
        <blockquote>{action.quote}</blockquote>
        <button className="primary" disabled={busy}>
          {busy ? "Saving…" : "Save action update"}
        </button>
      </form>
    </Dialog>
  );
}

function AddActionDialog({
  people,
  notes,
  close,
  save,
}: {
  people: Entity[];
  notes: string;
  close: () => void;
  save: (body: Record<string, unknown>) => Promise<void>;
}) {
  const [text, setText] = useState(""),
    [quote, setQuote] = useState(""),
    [owner, setOwner] = useState(""),
    [due, setDue] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <Dialog title="Add an evidence-backed action" close={close}>
      <form
        className="work-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          try {
            await save({
              text,
              quote,
              owner_id: owner || null,
              due_date: due || null,
            });
          } catch (e) {
            setError(message(e));
          } finally {
            setBusy(false);
          }
        }}
      >
        {error && (
          <p className="work-alert" role="alert">
            {error}
          </p>
        )}
        <label>
          Action description
          <input
            required
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </label>
        <label>
          Owner
          <select value={owner} onChange={(e) => setOwner(e.target.value)}>
            <option value="">Unassigned</option>
            {people.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Due date
          <input
            type="date"
            value={due}
            onChange={(e) => setDue(e.target.value)}
          />
        </label>
        <details open>
          <summary>Original notes</summary>
          <pre className="work-notes">{notes}</pre>
        </details>
        <label>
          Exact supporting passage
          <textarea
            required
            value={quote}
            onChange={(e) => setQuote(e.target.value)}
            placeholder="Copy the exact passage from the notes above."
          />
        </label>
        <button className="primary" disabled={busy}>
          {busy ? "Saving…" : "Create action"}
        </button>
      </form>
    </Dialog>
  );
}

function NotesDialog({
  meeting,
  close,
  save,
}: {
  meeting: Meeting;
  close: () => void;
  save: (notes: string, agenda: string) => Promise<void>;
}) {
  const [notes, setNotes] = useState(meeting.notes),
    [agenda, setAgenda] = useState(meeting.agenda),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <Dialog title="Update session notes" close={close}>
      <form
        className="work-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          try {
            await save(notes, agenda);
          } catch (e) {
            setError(message(e));
          } finally {
            setBusy(false);
          }
        }}
      >
        {error && (
          <p className="work-alert" role="alert">
            {error}
          </p>
        )}
        <label>
          Agenda
          <textarea
            rows={3}
            value={agenda}
            onChange={(e) => setAgenda(e.target.value)}
          />
        </label>
        <label>
          Meeting notes
          <textarea
            required
            maxLength={50000}
            rows={12}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>
        <p className="work-muted">
          Previous revisions are preserved. Keep the passages supporting any
          existing actions. Confirmed recaps preserve their notes.
        </p>
        <button className="primary" disabled={busy}>
          {busy ? "Saving…" : "Save notes"}
        </button>
      </form>
    </Dialog>
  );
}
