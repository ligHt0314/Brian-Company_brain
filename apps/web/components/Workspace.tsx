"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import WorkspaceGuide from "./WorkspaceGuide";
import MeetingsWorkspace from "./MeetingsWorkspace";
import TicketStatusEditor from "./TicketStatusEditor";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  CheckCheck,
  ClipboardCheck,
  ChevronDown,
  Clock,
  Database,
  FileText,
  GitBranch,
  History,
  Layers,
  LoaderCircle,
  MessageSquare,
  Network,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  AlertTriangle,
  RefreshCw,
  Users,
} from "lucide-react";
import {
  api,
  post,
  type Answer,
  type Evidence,
  type Entity,
  type Me,
  type Persona,
  type Source,
  type SourceList,
  type Revision,
  type Job,
  type Review,
  type HistoryItem,
  type PendingRun,
} from "@/lib/api/client";
const AnswerGraph = dynamic(() => import("./AnswerGraph"), {
  ssr: false,
  loading: () => <div className="graphCanvas empty">Loading graph…</div>,
});
const prompts = [
  {
    title: "Find launch risks",
    text: "What could block Atlas Client Portal, and which customer commitment is affected?",
    icon: GitBranch,
  },
  {
    title: "Untangle ownership",
    text: "Who owns Identity Gateway, and who has worked on it?",
    icon: Users,
  },
  {
    title: "Understand an impact",
    text: "What may be affected if Identity Gateway becomes unavailable?",
    icon: Network,
  },
  {
    title: "Trace a decision",
    text: "Why did we rule out unverified identities for Atlas Client Portal?",
    icon: BookOpen,
  },
];
function date(value: string | number) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
function time(value: string | number) {
  return new Date(value).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Kolkata",
  });
}
function errorText(e: unknown) {
  return e instanceof Error ? e.message : "Something went wrong. Please retry.";
}
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function allSources(): Promise<SourceList> {
  const first = await api<SourceList>("/sources?limit=100");
  const items = [...first.items];
  while (items.length < first.total && items.length < 10000) {
    const next = await api<SourceList>(
      `/sources?limit=100&offset=${items.length}`,
    );
    if (next.graph_epoch !== first.graph_epoch) {
      throw new Error(
        "Sources changed while loading. Refresh the page to try again.",
      );
    }
    if (!next.items.length) break;
    items.push(...next.items);
  }
  return { ...first, items };
}

function Modal({
  title,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const d = ref.current;
    const previous = document.activeElement as HTMLElement;
    d?.showModal();
    return () => {
      d?.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={wide ? "modal wide" : "modal"}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modalHead">
        <h2>{title}</h2>
        <button
          className="iconButton"
          aria-label="Close dialog"
          onClick={onClose}
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}

export default function Workspace() {
  const pathname = usePathname();
  const params = useSearchParams();
  const page =
    pathname === "/" || pathname.startsWith("/meetings")
      ? "meetings"
      : pathname.startsWith("/actions")
        ? "actions"
        : pathname.startsWith("/guide")
          ? "guide"
          : pathname.startsWith("/sources")
            ? "sources"
            : pathname.startsWith("/reviews")
              ? "reviews"
              : pathname.startsWith("/history")
                ? "history"
                : "investigate";
  const [me, setMe] = useState<Me | null>(null);
  const [boot, setBoot] = useState(true);
  const [error, setError] = useState("");
  const [session, setSession] = useState<string | null>(null);
  const [question, setQuestion] = useState(params.get("question") || "");
  const [entity, setEntity] = useState("");
  const [entities, setEntities] = useState<Entity[]>([]);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [running, setRunning] = useState(false);
  const [stage, setStage] = useState("");
  const [sources, setSources] = useState<SourceList | null>(null);
  const [filter, setFilter] = useState("");
  const [sourceKind, setSourceKind] = useState("");
  const [reviews, setReviews] = useState<Review[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [evidence, setEvidence] = useState<Evidence | null>(null);
  const [evidenceError, setEvidenceError] = useState("");
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [graphTab, setGraphTab] = useState<"paths" | "graph">("paths");
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [importOpen, setImportOpen] = useState(false);
  const [ticketEditor, setTicketEditor] = useState<string | null>(null);
  const [sourceHistory, setSourceHistory] = useState<{
    source: Source;
    revisions: Revision[];
  } | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [draft, setDraft] = useState<Review | null>(null);
  const [reviewBusy, setReviewBusy] = useState(false);
  const [reviewError, setReviewError] = useState("");
  const [assignee, setAssignee] = useState("person:maya");
  const [reason, setReason] = useState(
    "Confirm the current primary owner and reconcile the competing source assertions.",
  );
  const [changed, setChanged] = useState(false);
  const generation = useRef(0);
  const scopeVersion = useRef(0);
  const canImport = me?.capabilities.includes("import");
  const canReview = me?.capabilities.includes("review");
  const refreshSources = useCallback(async () => {
    const v = scopeVersion.current;
    const result = await allSources();
    if (v === scopeVersion.current) setSources(result);
  }, []);
  const loadData = useCallback(async () => {
    const v = scopeVersion.current;
    const [ss, es, rs, hs] = await Promise.all([
      allSources(),
      api<Entity[]>("/entities/search"),
      api<Review[]>("/reviews"),
      api<HistoryItem[]>("/history"),
    ]);
    if (v !== scopeVersion.current) return;
    setSources(ss);
    setEntities(es);
    setReviews(rs);
    setHistory(hs);
  }, []);
  useEffect(() => {
    let active = true;
    api<Me>("/me")
      .catch(() => post<Me>("/demo/session", { persona: "Engineer" }))
      .then(async (user) => {
        if (!active) return;
        setMe(user);
        const sessions = await api<{ id: string }[]>("/sessions");
        const s = sessions[0] || (await post<{ id: string }>("/sessions", {}));
        if (active) setSession(s.id);
        await loadData();
      })
      .catch((e) => active && setError(errorText(e)))
      .finally(() => active && setBoot(false));
    return () => {
      active = false;
    };
  }, [loadData]);
  useEffect(() => {
    let active = true;
    const id = params.get("run");
    if (id && me) {
      setAnswer(null);
      const loadSaved = async () => {
        const items = await api<HistoryItem[]>("/history");
        if (!active) return;
        const saved = items.find((h) => h.id === id);
        if (saved) {
          setQuestion(saved.question);
          setSession(saved.session_id);
        }
        const started = Date.now();
        while (Date.now() - started < 30000) {
          const result = await api<Answer | PendingRun>(
            "/investigations/" + id,
          );
          if (!active) return;
          if (result.status === "complete") {
            setAnswer(result);
            setChanged(result.historical || false);
            setSelectedPath(result.graph.paths[0]?.id || null);
            setRunning(false);
            return;
          }
          if (result.status === "failed")
            throw new Error(
              result.error?.message ||
                "This saved investigation failed. Rerun its question to try again.",
            );
          setRunning(true);
          setStage(result.stage || "Investigating");
          await delay(650);
        }
        throw new Error(
          "This saved investigation is still processing. Check History again shortly.",
        );
      };
      loadSaved().catch((e) => {
        if (active) {
          setError(errorText(e));
          setRunning(false);
        }
      });
    }
    return () => {
      active = false;
    };
  }, [params, me]);
  const changePersona = async (persona: Persona) => {
    generation.current++;
    scopeVersion.current++;
    setAnswer(null);
    setEvidence(null);
    setEvidenceOpen(false);
    setEvidenceError("");
    setReviews([]);
    setHistory([]);
    setSources(null);
    setSession(null);
    setError("");
    setRunning(false);
    setJob(null);
    setDraft(null);
    setReviewOpen(false);
    setSourceHistory(null);
    setImportOpen(false);
    setTicketEditor(null);
    const v = scopeVersion.current;
    try {
      const user = await post<Me>("/demo/session", { persona });
      if (v !== scopeVersion.current) return;
      setMe(user);
      const sessions = await api<{ id: string }[]>("/sessions");
      const s = sessions[0] || (await post<{ id: string }>("/sessions", {}));
      if (v !== scopeVersion.current) return;
      setSession(s.id);
      await loadData();
    } catch (e) {
      if (v === scopeVersion.current) setError(errorText(e));
    }
  };
  const investigate = async (
    text = question,
    chosen = entity,
    previous = answer?.run_id,
  ) => {
    if (!text.trim() || !session) return;
    const gen = ++generation.current;
    setQuestion(text);
    setError("");
    setRunning(true);
    setStage("Queued");
    setEvidenceOpen(false);
    try {
      const r = await post<{ run_id: string }>("/investigations", {
        session_id: session,
        question: text,
        ...(chosen ? { entity_id: chosen } : {}),
        ...(previous ? { previous_run_id: previous } : {}),
      });
      const started = Date.now();
      while (Date.now() - started < 30000) {
        if (gen !== generation.current) return;
        const result = await api<Answer | PendingRun>(
          "/investigations/" + r.run_id,
        );
        if (gen !== generation.current) return;
        if (result.status === "complete") {
          setAnswer(result);
          setSelectedPath(result.graph.paths[0]?.id || null);
          setChanged(false);
          setRunning(false);
          setHistory(await api<HistoryItem[]>("/history"));
          return;
        }
        if (result.status === "failed")
          throw new Error(
            result.error?.message || "The investigation failed. Please retry.",
          );
        setStage(result.stage || "Investigating");
        await delay(650);
      }
      throw new Error(
        "The investigation is taking longer than expected. Open History to check it or retry.",
      );
    } catch (e) {
      if (gen === generation.current) setError(errorText(e));
    } finally {
      if (gen === generation.current) setRunning(false);
    }
  };
  const openEvidence = async (id: string) => {
    const v = scopeVersion.current;
    setEvidence(null);
    setEvidenceError("");
    setEvidenceOpen(true);
    try {
      const result = await api<Evidence>("/evidence/" + id);
      if (v === scopeVersion.current) setEvidence(result);
    } catch (e) {
      if (v === scopeVersion.current) setEvidenceError(errorText(e));
    }
  };
  const citations = (ids: string[]) => (
    <span className="citations">
      {ids.map((id) => (
        <button
          key={id}
          className="citation"
          aria-label={
            "Open evidence " +
            ((answer?.evidence.findIndex((e) => e.id === id) ?? -1) + 1)
          }
          onClick={() => openEvidence(id)}
        >
          {(answer?.evidence.findIndex((e) => e.id === id) ?? -1) + 1}
        </button>
      ))}
    </span>
  );
  const watchJob = async (id: string) => {
    const v = scopeVersion.current;
    for (let i = 0; i < 90; i++) {
      const j = await api<Job>("/jobs/" + id);
      if (v !== scopeVersion.current) return;
      setJob(j);
      if (j.status === "complete" || j.status === "failed") {
        await refreshSources();
        if (j.status === "complete") setChanged(true);
        return;
      }
      await delay(900);
    }
    throw new Error(
      "Import is still processing. Refresh the Sources page to check the new revision.",
    );
  };
  const prepareReview = async () => {
    if (!answer) return;
    setReviewBusy(true);
    setReviewError("");
    const finding = answer.conflicts[0] || answer.findings[0];
    try {
      setDraft(
        await post<Review>("/reviews/proposals", {
          run_id: answer.run_id,
          entity_id: finding.entity_ids[0],
          assignee_id: assignee,
          reason,
        }),
      );
    } catch (e) {
      setReviewError(errorText(e));
    } finally {
      setReviewBusy(false);
    }
  };
  const confirmReview = async () => {
    if (!draft) return;
    setReviewBusy(true);
    setReviewError("");
    try {
      const r = await post<Review>("/reviews/confirm", {
        proposal_id: draft.id,
        idempotency_key: "confirm-" + draft.id,
      });
      setDraft(r);
      setReviews(await api<Review[]>("/reviews"));
    } catch (e) {
      setReviewError(errorText(e));
    } finally {
      setReviewBusy(false);
    }
  };
  const labels = Object.fromEntries(
    (answer?.graph.nodes || []).map((e) => [e.id, e.label]),
  );
  const nav = [
    {
      id: "meetings",
      href: "/meetings",
      label: "Meetings & handovers",
      icon: MessageSquare,
    },
    {
      id: "actions",
      href: "/actions",
      label: "Action items",
      icon: CheckCheck,
    },
    {
      id: "investigate",
      href: "/investigate",
      label: "Investigate",
      icon: Sparkles,
    },
    { id: "sources", href: "/sources", label: "Sources", icon: Layers },
    { id: "reviews", href: "/reviews", label: "Reviews", icon: ClipboardCheck },
    { id: "history", href: "/history", label: "History", icon: History },
    { id: "guide", href: "/guide", label: "Workspace guide", icon: BookOpen },
  ];
  const blockerCount =
    answer?.findings.filter((f) => f.category === "blocker").length || 0;
  const sourceRows = (sources?.items || []).filter(
    (s) =>
      (!sourceKind || s.kind === sourceKind) &&
      s.title.toLowerCase().includes(filter.toLowerCase()),
  );
  return (
    <div className="workspace">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <span className="brandMark">
            <Network size={23} />
          </span>
          <span className="brandText">
            <strong>Brian</strong>
            <small>company brain</small>
          </span>
        </Link>
        <div className="workspacePicker">
          <span className="companyMark">B</span>
          <div>
            <strong>DigiPlus Services</strong>
            <small>Company workspace</small>
          </div>
          <ChevronDown size={15} />
        </div>
        <div className="navLabel">WORKSPACE</div>
        <nav>
          {nav.map((n) => (
            <Link
              key={n.id}
              className={page === n.id ? "navItem active" : "navItem"}
              href={n.href}
            >
              <n.icon size={18} />
              {n.label}
              {n.id === "reviews" && reviews.length > 0 && (
                <span className="navCount">{reviews.length}</span>
              )}
            </Link>
          ))}
        </nav>
        <div className="sidebarBottom">
          <div className="graphStatus">
            <span className="statusDot" />
            <strong>FalkorDB evidence graph</strong>
            <small>
              {sources
                ? `${sources.total} accessible sources`
                : "Checking sources…"}
            </small>
          </div>
          <div className="sidebarNote">
            <ShieldCheck size={16} />
            <span>
              Answers respect your
              <br />
              source permissions
            </span>
          </div>
          <div className="profile">
            <span className="avatar">{me?.persona[0] || "·"}</span>
            <div>
              <strong>{me?.persona || "Workspace"}</strong>
              <small>Workspace access</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="mainShell">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span>{" "}
            <strong>{nav.find((n) => n.id === page)?.label}</strong>
          </div>
          <div className="topRight">
            <span className="workspacePill">
              <span />
              Internal workspace
            </span>
            <label className="personaSelect">
              <Users size={15} />
              <select
                aria-label="Workspace role"
                value={me?.persona || "Engineer"}
                onChange={(e) => changePersona(e.target.value as Persona)}
              >
                {["Engineer", "Lead", "Viewer"].map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
          </div>
        </header>
        <main className="mainContent">
          {error && (
            <div className="errorBanner" role="alert">
              <AlertTriangle size={18} />
              <span>{error}</span>
              <button
                className="iconButton"
                onClick={() => setError("")}
                aria-label="Dismiss error"
              >
                <X size={17} />
              </button>
            </div>
          )}
          {boot ? (
            <div className="loadingPage">
              <LoaderCircle className="spin" />
              Opening your workspace…
            </div>
          ) : page === "meetings" || page === "actions" ? (
            <MeetingsWorkspace
              key={me!.id}
              me={me!}
              entities={entities}
              mode={page}
            />
          ) : page === "guide" ? (
            <WorkspaceGuide
              entities={entities}
              sourceCount={sources?.total || 0}
              onAsk={(text) => {
                window.location.assign(
                  `/investigate?question=${encodeURIComponent(text)}`,
                );
              }}
            />
          ) : page === "investigate" ? (
            <>
              <div className="pageHeading">
                <div>
                  <div className="eyebrow">
                    <span className="tinyLine" />
                    CONNECTED KNOWLEDGE, CLEARER DECISIONS
                  </div>
                  <h1>Your company, in context.</h1>
                  <p>
                    Understand what changed, who it affects, and the evidence
                    behind it.
                  </p>
                </div>
                <div className="clockNote">
                  <Clock size={15} />
                  <div>
                    Knowledge snapshot<small>17 Oct 2026</small>
                  </div>
                </div>
              </div>
              <div className="workspaceIntro">
                <span>
                  <strong>Your DigiPlus Services workspace.</strong> Connect
                  projects, people and decisions with the evidence behind them.
                </span>
                <Link href="/guide">
                  Workspace guide <ArrowRight size={15} />
                </Link>
              </div>
              <div className="workspaceMetrics" aria-label="Workspace overview">
                <Link href="/sources">
                  <Layers size={19} />
                  <div>
                    <strong>{sources?.total || 0}</strong>
                    <span>Accessible sources</span>
                  </div>
                  <ArrowUpRight size={15} />
                </Link>
                <Link href="/guide#projects">
                  <GitBranch size={19} />
                  <div>
                    <strong>
                      {entities.filter((e) => e.kind === "Project").length}
                    </strong>
                    <span>Projects in the directory</span>
                  </div>
                  <ArrowUpRight size={15} />
                </Link>
                <Link href="/guide#people">
                  <Users size={19} />
                  <div>
                    <strong>
                      {entities.filter((e) => e.kind === "Person").length}
                    </strong>
                    <span>People in the directory</span>
                  </div>
                  <ArrowUpRight size={15} />
                </Link>
                <Link href="/reviews">
                  <ClipboardCheck size={19} />
                  <div>
                    <strong>
                      {reviews.filter((r) => r.state === "open").length}
                    </strong>
                    <span>Open reviews</span>
                  </div>
                  <ArrowUpRight size={15} />
                </Link>
              </div>
              <section className="composer">
                <div className="composerTop">
                  <span>
                    <Sparkles size={17} /> Start an investigation
                  </span>
                  <label>
                    <span className="srOnly">Investigation entity</span>
                    <select
                      value={entity}
                      onChange={(e) => setEntity(e.target.value)}
                    >
                      <option value="">Detect from question</option>
                      {entities
                        .filter((e) => ["Project", "Service"].includes(e.kind))
                        .map((e) => (
                          <option value={e.id} key={e.id}>
                            {e.label}
                          </option>
                        ))}
                    </select>
                  </label>
                </div>
                <textarea
                  aria-label="Investigation question"
                  placeholder="What could block Atlas Client Portal, and which customer commitment is affected?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                      e.preventDefault();
                      investigate();
                    }
                  }}
                />
                <div className="composerBottom">
                  <span>
                    <ShieldCheck size={14} /> Based on the indexed sources you
                    can access
                  </span>
                  <button
                    className="primary"
                    disabled={running || !question.trim() || !session}
                    onClick={() => investigate()}
                  >
                    {running ? (
                      <LoaderCircle size={16} className="spin" />
                    ) : (
                      <Sparkles size={16} />
                    )}{" "}
                    {running ? "Investigating…" : "Investigate"}
                    {!running && <span className="shortcut">⌘ ↵</span>}
                  </button>
                </div>
              </section>
              {running && (
                <div className="progress" role="status">
                  <LoaderCircle size={17} className="spin" />
                  {stage}
                  <span>
                    Following supported relationships in your company graph
                  </span>
                </div>
              )}
              {!answer && !running ? (
                <>
                  <div className="sectionEyebrow">A GOOD PLACE TO START</div>
                  <div className="promptGrid">
                    {prompts.map((p) => (
                      <button
                        key={p.title}
                        className="promptCard"
                        onClick={() => {
                          setEntity("");
                          investigate(p.text, "", undefined);
                        }}
                      >
                        <span className="promptIcon">
                          <p.icon size={19} />
                        </span>
                        <strong>{p.title}</strong>
                        <p>{p.text}</p>
                        <ArrowUpRight size={17} className="promptArrow" />
                      </button>
                    ))}
                  </div>
                  <section className="howItWorks">
                    <div className="howIcon">
                      <GitBranch size={25} />
                    </div>
                    <div>
                      <h2>More than finding a document.</h2>
                      <p>
                        Follow the connections between projects, people,
                        decisions, and customer promises.
                        <br />
                        Every finding leads back to the source that supports it.
                      </p>
                    </div>
                    <span className="howTag">Evidence first</span>
                  </section>
                  <div className="workspaceSnapshot">
                    <span>
                      <Database size={16} />
                      {sources?.total || 0} accessible records
                    </span>
                    <span>
                      <Network size={16} />
                      FalkorDB powers every investigation
                    </span>
                    <span>
                      <ShieldCheck size={16} />
                      Permission-aware evidence
                    </span>
                  </div>
                </>
              ) : (
                answer && (
                  <>
                    <div className="resultToolbar">
                      <div>
                        <span className="sectionEyebrow">INVESTIGATION</span>
                        <span className="modePill">
                          {answer.execution_mode === "live_model"
                            ? "Live model + graph"
                            : "Deterministic graph findings"}
                        </span>
                      </div>
                      <button
                        className="textButton"
                        disabled={running}
                        onClick={() =>
                          investigate(
                            question || "What could block Atlas Client Portal?",
                            answer.entity_id || "",
                          )
                        }
                      >
                        <RefreshCw size={14} />
                        Rerun
                      </button>
                    </div>
                    {changed || answer.historical ? (
                      <div className="notice">
                        <RefreshCw size={16} />
                        Sources changed since this answer. Rerun to use current
                        evidence.
                      </div>
                    ) : null}
                    {answer.answer_state === "needs_refresh" ? (
                      <div className="emptyCard">
                        <ShieldCheck size={28} />
                        <h2>This investigation needs a refresh</h2>
                        <p>
                          Its evidence is no longer available to this session.
                          Rerun to retrieve current accessible evidence.
                        </p>
                      </div>
                    ) : answer.answer_state === "clarification" ? (
                      <div className="emptyCard">
                        <h2>Which entity do you mean?</h2>
                        <p>The name matches more than one directory entry.</p>
                        <div className="candidateList">
                          {answer.candidates.map((e) => (
                            <button
                              className="secondary"
                              key={e.id}
                              onClick={() => investigate(question, e.id)}
                            >
                              {e.label}
                              <small>{e.kind}</small>
                              <ArrowRight size={16} />
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="answerLayout">
                        <div className="answerColumn">
                          <section className="answerSummary">
                            <div className="resultKicker">
                              <span
                                className={
                                  blockerCount
                                    ? "resultIcon warning"
                                    : "resultIcon"
                                }
                              >
                                {blockerCount ? (
                                  <AlertTriangle size={20} />
                                ) : (
                                  <GitBranch size={20} />
                                )}
                              </span>
                              <span>
                                {answer.answer_state === "insufficient_evidence"
                                  ? "Evidence gap"
                                  : answer.conflicts.length
                                    ? "Needs attention"
                                    : "Evidence retrieved"}
                              </span>
                            </div>
                            <h2>
                              {answer.answer_state === "insufficient_evidence"
                                ? "More evidence is needed"
                                : answer.intent === "release_risk"
                                  ? `${blockerCount ? blockerCount + " known blocker" + (blockerCount > 1 ? "s" : "") : "No confirmed blockers"}${answer.conflicts.length ? " and an ownership conflict" : ""}`
                                  : answer.intent === "owner_lookup"
                                    ? answer.conflicts.length
                                      ? "Ownership needs confirmation"
                                      : "Ownership & relevant work"
                                    : answer.intent === "change_impact"
                                      ? "Follow the potential impact"
                                      : answer.intent === "decision_lookup"
                                        ? "The decision, with its context"
                                        : "Here’s what the evidence shows"}
                            </h2>
                            <p className="scopeLine">
                              {time(answer.generated_at)} IST ·{" "}
                              {answer.scope.visible_sources_considered}{" "}
                              accessible sources considered
                            </p>
                          </section>
                          {answer.changes.removed.length +
                            answer.changes.added.length +
                            answer.changes.changed.length >
                            0 && (
                            <section className="changesPanel">
                              <h3>
                                <RefreshCw size={16} />
                                What changed
                              </h3>
                              {[
                                ...answer.changes.removed,
                                ...answer.changes.added,
                                ...answer.changes.changed,
                              ].map((c) => (
                                <p key={c.finding_id}>
                                  {c.text}
                                  {citations(c.evidence_ids)}
                                </p>
                              ))}
                            </section>
                          )}
                          <div className="answerBlocks">
                            {answer.blocks.map((b, i) => (
                              <article
                                className={"answerBlock " + b.kind}
                                key={i}
                              >
                                <div className="blockIcon">
                                  {b.kind === "uncertainty" ? (
                                    <AlertTriangle size={16} />
                                  ) : b.kind === "inference" ? (
                                    <GitBranch size={16} />
                                  ) : (
                                    <Check size={16} />
                                  )}
                                </div>
                                <div>
                                  {b.kind === "inference" && (
                                    <small className="blockLabel">
                                      CONDITIONAL IMPACT
                                    </small>
                                  )}
                                  <p>
                                    {b.text}
                                    {citations(b.evidence_ids)}
                                  </p>
                                </div>
                              </article>
                            ))}
                          </div>
                          {answer.findings.some((f) => f.path_id) && (
                            <div className="findingPaths">
                              {answer.findings
                                .filter((f) => f.path_id)
                                .map((f) => (
                                  <button
                                    className="textButton"
                                    key={f.id}
                                    onClick={() => {
                                      setSelectedPath(f.path_id || null);
                                      setGraphTab("graph");
                                    }}
                                  >
                                    <GitBranch size={14} />
                                    Show path: {f.title}
                                    <ArrowRight size={13} />
                                  </button>
                                ))}
                            </div>
                          )}
                          {canReview && answer.findings.length > 0 && (
                            <div className="reviewCallout">
                              <div>
                                <h3>A question for the team?</h3>
                                <p>
                                  Turn evidence into a focused internal review.
                                </p>
                              </div>
                              <button
                                className="secondary"
                                onClick={() => {
                                  setDraft(null);
                                  setReviewError("");
                                  setReviewOpen(true);
                                }}
                              >
                                <Plus size={15} />
                                Prepare review task
                              </button>
                            </div>
                          )}
                          {answer.scope.warnings.length > 0 && (
                            <details className="warnings">
                              <summary>
                                <AlertTriangle size={14} />
                                {answer.scope.warnings.length} evidence{" "}
                                {answer.scope.warnings.length === 1
                                  ? "note"
                                  : "notes"}
                              </summary>
                              {answer.scope.warnings.map((w) => (
                                <p key={w}>{w}</p>
                              ))}
                            </details>
                          )}
                          <details className="execution">
                            <summary>
                              Execution details <ChevronDown size={13} />
                            </summary>
                            <div>
                              {answer.metrics.duration_ms} ms total ·{" "}
                              {answer.metrics.graph_query_count} graph queries (
                              {answer.metrics.graph_duration_ms} ms) ·{" "}
                              {answer.metrics.model_calls} model calls
                              <br />
                              Graph epoch {answer.graph_epoch} · Prompt{" "}
                              {answer.metrics.prompt_version}
                              <br />
                              {answer.metrics.model_id || "No live model used"}
                              {answer.metrics.agent_tool_calls > 0 && (
                                <>
                                  <p>
                                    {answer.metrics.agent_tool_calls} read tools
                                    · {answer.metrics.agent_rounds} selection
                                    rounds
                                  </p>
                                  <ol>
                                    {answer.agent_trace.map((step, index) => (
                                      <li key={index}>
                                        {step.tool.replaceAll("_", " ")} ·{" "}
                                        {step.claim_count} claims ·{" "}
                                        {step.duration_ms} ms
                                      </li>
                                    ))}
                                  </ol>
                                </>
                              )}
                              {answer.scope.truncated && (
                                <p>
                                  Partial scope: the retrieval budget was
                                  reached.
                                </p>
                              )}
                            </div>
                          </details>
                        </div>
                        <aside className="evidencePanel">
                          <div className="panelHeader">
                            <div>
                              <GitBranch size={17} />
                              <h3>Follow the evidence</h3>
                            </div>
                            <span>{answer.graph.nodes.length} entities</span>
                          </div>
                          <div className="tabs">
                            <button
                              className={graphTab === "paths" ? "selected" : ""}
                              onClick={() => setGraphTab("paths")}
                            >
                              <Layers size={14} />
                              Path list
                            </button>
                            <button
                              className={graphTab === "graph" ? "selected" : ""}
                              onClick={() => setGraphTab("graph")}
                            >
                              <Network size={14} />
                              Graph
                            </button>
                          </div>
                          {graphTab === "graph" ? (
                            <AnswerGraph
                              answer={answer}
                              selectedPath={selectedPath}
                              onEvidence={openEvidence}
                            />
                          ) : (
                            <div className="pathList">
                              {answer.graph.paths.length > 0 ? (
                                answer.graph.paths.map((path, i) => (
                                  <div className="pathGroup" key={path.id}>
                                    <small>PATH {i + 1}</small>
                                    {path.edge_ids.map((id) => {
                                      const e = answer.graph.edges.find(
                                        (e) => e.id === id,
                                      );
                                      return e ? (
                                        <button
                                          className={
                                            "pathStep " +
                                            (e.conflict ? "conflict" : "")
                                          }
                                          key={id}
                                          onClick={() =>
                                            openEvidence(e.evidence_ids[0])
                                          }
                                        >
                                          <span className="pathNodeDot" />
                                          <strong>
                                            {labels[e.source_entity_id]}
                                          </strong>
                                          <span className="pathVerb">
                                            {e.predicate
                                              .toLowerCase()
                                              .replaceAll("_", " ")}
                                            <ArrowRight size={13} />
                                          </span>
                                          <strong>
                                            {labels[e.target_entity_id]}
                                          </strong>
                                          <ArrowUpRight size={13} />
                                        </button>
                                      ) : null;
                                    })}
                                  </div>
                                ))
                              ) : answer.graph.edges.length > 0 ? (
                                answer.graph.edges.map((e) => (
                                  <button
                                    className={
                                      "pathStep " +
                                      (e.conflict ? "conflict" : "")
                                    }
                                    key={e.id}
                                    onClick={() =>
                                      openEvidence(e.evidence_ids[0])
                                    }
                                  >
                                    <span className="pathNodeDot" />
                                    <strong>
                                      {labels[e.source_entity_id]}
                                    </strong>
                                    <span className="pathVerb">
                                      {e.predicate
                                        .toLowerCase()
                                        .replaceAll("_", " ")}
                                      <ArrowRight size={13} />
                                    </span>
                                    <strong>
                                      {labels[e.target_entity_id]}
                                    </strong>
                                  </button>
                                ))
                              ) : (
                                <p className="empty">
                                  No supported relationship paths in this
                                  result.
                                </p>
                              )}
                            </div>
                          )}
                          <div className="panelFoot">
                            <ShieldCheck size={14} />
                            Select a relationship to inspect its source.
                          </div>
                          <div className="sourceMiniList">
                            <h4>
                              SOURCES IN THIS ANSWER{" "}
                              <span>
                                {
                                  new Set(
                                    answer.evidence.map((e) => e.source_id),
                                  ).size
                                }
                              </span>
                            </h4>
                            {Array.from(
                              new Map(
                                answer.evidence.map((e) => [e.source_id, e]),
                              ).values(),
                            ).map((e) => (
                              <button
                                key={e.source_id}
                                onClick={() => openEvidence(e.id)}
                              >
                                <span
                                  className={"sourceTypeIcon " + e.source_kind}
                                >
                                  {e.source_kind === "chat" ? (
                                    <MessageSquare size={15} />
                                  ) : (
                                    <FileText size={15} />
                                  )}
                                </span>
                                <span>
                                  <strong>{e.source_title}</strong>
                                  <small>
                                    {e.source_kind} export ·{" "}
                                    {date(e.source_updated_at)}
                                    {e.is_stale ? " · Stale" : ""}
                                  </small>
                                </span>
                                <ArrowUpRight size={14} />
                              </button>
                            ))}
                          </div>
                        </aside>
                      </div>
                    )}
                  </>
                )
              )}
            </>
          ) : page === "sources" ? (
            <>
              <div className="pageHeading">
                <div>
                  <div className="eyebrow">YOUR EVIDENCE LIBRARY</div>
                  <h1>Sources</h1>
                  <p>
                    Know what’s indexed, how current it is, and where it came
                    from.
                  </p>
                </div>
                {canImport && (
                  <div className="headingActions">
                    <button
                      className="secondary"
                      onClick={() => setTicketEditor("")}
                    >
                      <RefreshCw size={16} />
                      Update ticket status
                    </button>
                    <button
                      className="primary"
                      onClick={() => setImportOpen(true)}
                    >
                      <Upload size={16} />
                      Import source
                    </button>
                  </div>
                )}
              </div>
              {job && (
                <div
                  className={job.status === "failed" ? "errorBanner" : "notice"}
                  role="status"
                >
                  <Activity size={17} />
                  <span>
                    <strong>{job.stage}</strong> · {job.source_id}
                    {job.error && " · " + job.error}
                    {job.status === "complete" &&
                      ` · ${job.accepted || 0} accepted, ${job.pending || 0} pending${job.unchanged ? " · Already indexed" : ""}`}
                    {job.unresolved_mentions?.length
                      ? " · Unrecognized entities: " +
                        job.unresolved_mentions.join(", ")
                      : ""}
                  </span>
                </div>
              )}
              <div className="sourceStats">
                <div>
                  <span className="statIcon">
                    <Layers size={21} />
                  </span>
                  <div>
                    <strong>{sources?.total || 0}</strong>
                    <small>Accessible sources</small>
                  </div>
                </div>
                <div>
                  <span className="statIcon amber">
                    <Clock size={21} />
                  </span>
                  <div>
                    <strong>
                      {sources?.items.filter((s) => s.is_stale).length || 0}
                    </strong>
                    <small>Need a freshness check</small>
                  </div>
                </div>
                <div>
                  <span className="statIcon purple">
                    <Database size={21} />
                  </span>
                  <div>
                    <strong>FalkorDB</strong>
                    <small>Canonical evidence graph</small>
                  </div>
                </div>
              </div>
              <section className="sourceTableCard">
                <div className="tableToolbar">
                  <div className="searchInput">
                    <Search size={16} />
                    <input
                      aria-label="Search sources"
                      placeholder="Search sources…"
                      value={filter}
                      onChange={(e) => setFilter(e.target.value)}
                    />
                  </div>
                  <select
                    aria-label="Source type"
                    value={sourceKind}
                    onChange={(e) => setSourceKind(e.target.value)}
                  >
                    <option value="">All source types</option>
                    {[
                      "document",
                      "chat",
                      "ticket",
                      "decision",
                      "directory",
                    ].map((k) => (
                      <option key={k}>{k}</option>
                    ))}
                  </select>
                  <span>{sourceRows.length} records</span>
                </div>
                <div className="tableScroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Source</th>
                        <th>Type</th>
                        <th>Source updated</th>
                        <th>Freshness</th>
                        <th>Revision</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sourceRows.map((s) => (
                        <tr key={s.id}>
                          <td>
                            <button
                              className="sourceName"
                              onClick={async () => {
                                const v = scopeVersion.current;
                                try {
                                  const revisions = await api<Revision[]>(
                                    "/sources/" +
                                      encodeURIComponent(s.id) +
                                      "/revisions",
                                  );
                                  if (v === scopeVersion.current)
                                    setSourceHistory({ source: s, revisions });
                                } catch (e) {
                                  if (v === scopeVersion.current)
                                    setError(errorText(e));
                                }
                              }}
                            >
                              <span className={"sourceTypeIcon " + s.kind}>
                                {s.kind === "chat" ? (
                                  <MessageSquare size={17} />
                                ) : (
                                  <FileText size={17} />
                                )}
                              </span>
                              <span>
                                <strong>{s.title}</strong>
                                <small>{s.id}</small>
                              </span>
                            </button>
                          </td>
                          <td>
                            <span className="typeLabel">{s.kind}</span>
                          </td>
                          <td>
                            {date(s.source_updated_at)}
                            <small className="cellSmall">
                              Indexed {time(s.indexed_at)}
                            </small>
                          </td>
                          <td>
                            <span
                              className={
                                s.is_stale ? "freshness stale" : "freshness"
                              }
                            >
                              <span />
                              {s.is_stale ? "Stale source" : "Current"}
                            </span>
                          </td>
                          <td>
                            <span className="revisionTag">
                              v{s.revision_number}
                            </span>
                            <ArrowUpRight size={14} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {sourceRows.length === 0 && (
                  <div className="empty">
                    No accessible sources match this filter.
                  </div>
                )}
              </section>
            </>
          ) : page === "reviews" ? (
            <>
              <div className="pageHeading">
                <div>
                  <div className="eyebrow">FOLLOW THROUGH, WITH CONTEXT</div>
                  <h1>Internal reviews</h1>
                  <p>
                    Questions for the team, connected to the evidence that
                    raised them.
                  </p>
                </div>
                <span className="countPill">{reviews.length} open</span>
              </div>
              {reviews.length ? (
                reviews.map((r) => (
                  <article className="reviewCard" key={r.id}>
                    <div className="reviewCardIcon">
                      <ClipboardCheck size={23} />
                    </div>
                    <div>
                      <span className="freshness">Open review</span>
                      <h2>{r.title}</h2>
                      <p>{r.reason}</p>
                      <div className="reviewMeta">
                        <span>
                          <Users size={14} />
                          {r.assignee_name}
                        </span>
                        <span>
                          <Clock size={14} />
                          {r.created_at ? date(r.created_at) : ""}
                        </span>
                        <code>{r.id}</code>
                      </div>
                      <div className="reviewEvidence">
                        {r.evidence_ids.map((id, i) => (
                          <button
                            className="textButton"
                            key={id}
                            onClick={() => openEvidence(id)}
                          >
                            Evidence {i + 1}
                            <ArrowUpRight size={13} />
                          </button>
                        ))}
                      </div>
                    </div>
                  </article>
                ))
              ) : (
                <div className="emptyCard">
                  <ClipboardCheck size={32} />
                  <h2>No reviews in your visible scope</h2>
                  <p>
                    Investigate a project, then prepare a review from a
                    supported finding.
                  </p>
                  <Link className="secondary" href="/investigate">
                    Start an investigation
                    <ArrowRight size={16} />
                  </Link>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="pageHeading">
                <div>
                  <div className="eyebrow">YOUR INVESTIGATION TRAIL</div>
                  <h1>History</h1>
                  <p>
                    Reopen a past investigation or retrieve fresh evidence for
                    the same question.
                  </p>
                </div>
                <span className="privateLabel">
                  <ShieldCheck size={15} />
                  Private to your identity
                </span>
              </div>
              {history.length ? (
                <div className="historyList">
                  {history.map((h) => (
                    <article key={h.id}>
                      <span className="historyIcon">
                        <History size={20} />
                      </span>
                      <div>
                        <Link href={"/investigate?run=" + h.id}>
                          {h.question}
                        </Link>
                        <small>
                          {time(h.created_at)} IST · {h.status}
                        </small>
                      </div>
                      <Link
                        className="iconButton"
                        aria-label="Open saved investigation"
                        href={"/investigate?run=" + h.id}
                      >
                        <ArrowUpRight size={18} />
                      </Link>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="emptyCard">
                  <History size={32} />
                  <h2>Your next question starts the trail</h2>
                  <p>
                    Investigations are saved privately and rechecked against
                    current source permissions.
                  </p>
                </div>
              )}
            </>
          )}
          <footer className="pageFooter">
            <span>
              Brian <span className="footerDot">·</span> DigiPlus Services
            </span>
            <span>Evidence connects your work.</span>
          </footer>
        </main>
      </div>
      {evidenceOpen && (
        <Modal
          title="Source evidence"
          onClose={() => {
            setEvidenceOpen(false);
            setEvidence(null);
          }}
        >
          {evidenceError ? (
            <div className="errorBanner">
              {evidenceError}. Rerun the investigation to refresh its evidence.
            </div>
          ) : evidence ? (
            <div className="evidenceDetail">
              <span className="typeLabel">{evidence.source_kind} export</span>
              <h2>{evidence.source_title}</h2>
              <div className="evidenceBadges">
                <span
                  className={
                    evidence.is_current ? "freshness" : "freshness stale"
                  }
                >
                  {evidence.is_current
                    ? "Current revision"
                    : "Historical revision"}
                </span>
                {evidence.is_stale && (
                  <span className="freshness stale">Stale source</span>
                )}
              </div>
              <blockquote>
                <mark>{evidence.quote}</mark>
              </blockquote>
              <dl>
                <dt>Source updated</dt>
                <dd>{time(evidence.source_updated_at)} IST</dd>
                <dt>Indexed</dt>
                <dd>{time(evidence.indexed_at)} IST</dd>
                <dt>Evidence method</dt>
                <dd>
                  {evidence.extraction_method === "fixture"
                    ? "Reviewed extraction"
                    : evidence.extraction_method === "model"
                      ? "Model extraction"
                      : evidence.extraction_method === "structured"
                        ? "Validated record"
                        : "Reviewed record"}
                </dd>
                <dt>Import mode</dt>
                <dd>
                  {evidence.ingestion_mode === "fixture"
                    ? "Reviewed import"
                    : "Source import"}
                </dd>
                <dt>Revision</dt>
                <dd>
                  <code>{evidence.revision_id}</code>
                </dd>
                <dt>Evidence span</dt>
                <dd>
                  {evidence.start}–{evidence.end} · Unicode code points
                </dd>
              </dl>
              <p className="muted">
                This exact passage supports the selected assertion. A citation
                identifies evidence; it does not remove uncertainty in
                conflicting sources.
              </p>
            </div>
          ) : (
            <div className="empty">
              <LoaderCircle className="spin" />
              Loading authorized evidence…
            </div>
          )}
        </Modal>
      )}
      {sourceHistory && (
        <Modal title="Source history" onClose={() => setSourceHistory(null)}>
          <div className="evidenceDetail">
            <span className="typeLabel">
              {sourceHistory.source.kind} export
            </span>
            <h2>{sourceHistory.source.title}</h2>
            <p className="muted">
              Current source permissions apply to every revision.
            </p>
            {sourceHistory.revisions.map((r) => (
              <div className="revisionRow" key={r.id}>
                <span className="revisionTag">v{r.revision_number}</span>
                <div>
                  <strong>
                    {r.is_current ? "Current revision" : "Historical revision"}
                  </strong>
                  <small>
                    Updated {time(r.source_updated_at)} IST
                    <br />
                    Indexed {time(r.indexed_at)} IST ·{" "}
                    {r.ingestion_mode === "fixture"
                      ? "Reviewed import"
                      : "Source import"}
                    <br />
                    <code>{r.id}</code>
                  </small>
                </div>
                {r.is_current && <Check size={17} />}
              </div>
            ))}
          </div>
        </Modal>
      )}
      {ticketEditor !== null && (
        <Modal
          title="Update ticket status"
          onClose={() => setTicketEditor(null)}
        >
          <TicketStatusEditor
            sources={sources?.items || []}
            initialSource={ticketEditor || undefined}
            onSave={async (id) => {
              const version = scopeVersion.current;
              await watchJob(id);
              if (version !== scopeVersion.current) return;
              const saved = await api<Job>("/jobs/" + id);
              if (saved.status === "failed")
                throw new Error(saved.error || "The source update failed.");
              setTicketEditor(null);
            }}
          />
        </Modal>
      )}
      {importOpen && (
        <ImportModal
          onClose={() => setImportOpen(false)}
          onImport={async (form) => {
            const r = await api<{ job_ids: string[] }>("/imports", {
              method: "POST",
              body: form,
            });
            setImportOpen(false);
            setTicketEditor(null);
            for (const id of r.job_ids) await watchJob(id);
          }}
        />
      )}
      {reviewOpen && (
        <Modal
          title={
            draft?.state === "open"
              ? "Review created"
              : "Prepare an internal review"
          }
          onClose={() => setReviewOpen(false)}
        >
          <div className="reviewForm">
            {reviewError && (
              <div className="errorBanner" role="alert">
                {reviewError}
              </div>
            )}
            {reviewError && draft && draft.state !== "open" && (
              <button
                className="textButton"
                onClick={() => {
                  setDraft(null);
                  setReviewError("");
                }}
              >
                Refresh preview
              </button>
            )}
            {draft ? (
              <>
                <span
                  className={draft.state === "open" ? "freshness" : "modePill"}
                >
                  {draft.state === "open"
                    ? "Created"
                    : "Draft · awaiting confirmation"}
                </span>
                <h2>{draft.title}</h2>
                <p>{draft.reason}</p>
                <dl>
                  <dt>Assignee</dt>
                  <dd>{draft.assignee_name}</dd>
                  <dt>Destination</dt>
                  <dd>Company Brain internal reviews</dd>
                  <dt>Supporting evidence</dt>
                  <dd>{draft.evidence_ids.length} passages</dd>
                </dl>
                {draft.state === "open" ? (
                  <>
                    <code>{draft.id}</code>
                    <Link
                      className="primary"
                      href="/reviews"
                      onClick={() => setReviewOpen(false)}
                    >
                      View reviews
                      <ArrowRight size={16} />
                    </Link>
                  </>
                ) : (
                  <button
                    className="primary"
                    disabled={reviewBusy}
                    onClick={confirmReview}
                  >
                    {reviewBusy ? (
                      <LoaderCircle size={16} className="spin" />
                    ) : (
                      <Plus size={16} />
                    )}
                    Create review task
                  </button>
                )}
              </>
            ) : (
              <>
                <p className="muted">
                  Review the finding with a named person. The task will retain
                  its source evidence.
                </p>
                <label>
                  Assignee
                  <select
                    value={assignee}
                    onChange={(e) => setAssignee(e.target.value)}
                  >
                    <option value="person:maya">Maya Rao</option>
                    <option value="person:dev">Dev Shah</option>
                    <option value="person:leah">Leah Chen</option>
                  </select>
                </label>
                <label>
                  Reason
                  <textarea
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    maxLength={500}
                  />
                </label>
                <button
                  className="primary"
                  disabled={reviewBusy || !reason.trim()}
                  onClick={prepareReview}
                >
                  {reviewBusy ? (
                    <LoaderCircle size={16} className="spin" />
                  ) : (
                    <ArrowRight size={16} />
                  )}
                  Preview review
                </button>
              </>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}

function ImportModal({
  onClose,
  onImport,
}: {
  onClose: () => void;
  onImport: (form: FormData) => Promise<void>;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [sourceId, setSourceId] = useState("doc:new-document");
  const [title, setTitle] = useState("New evidence");
  const [kind, setKind] = useState("document");
  const [groups, setGroups] = useState("engineering");
  const [updated, setUpdated] = useState("2026-10-17T04:30");
  const [expected, setExpected] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit() {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const form = new FormData();
      form.append("files", file);
      form.append(
        "metadata",
        JSON.stringify({
          schema_version: "1.0",
          source_id: sourceId,
          title,
          kind,
          source_updated_at: new Date(updated + "Z").toISOString(),
          acl_groups: [groups],
          ...(expected ? { expected_revision_id: expected } : {}),
        }),
      );
      await onImport(form);
    } catch (e) {
      setError(errorText(e));
      setBusy(false);
    }
  }
  return (
    <Modal title="Import a source" onClose={onClose}>
      <div className="importForm">
        <p className="muted">
          JSON exports use structured fields. Markdown and text use live model
          extraction and require a configured server key.
        </p>
        <label className="fileDrop">
          <Upload size={26} />
          <strong>{file ? file.name : "Choose a source file"}</strong>
          <span>JSON, Markdown, or UTF-8 text · up to 2 MB</span>
          <input
            aria-label="Source file"
            type="file"
            accept=".json,.md,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>
        {file && !file.name.endsWith(".json") && (
          <>
            <div className="formGrid">
              <label>
                Source ID
                <input
                  value={sourceId}
                  onChange={(e) => setSourceId(e.target.value)}
                />
              </label>
              <label>
                Source type
                <select value={kind} onChange={(e) => setKind(e.target.value)}>
                  {["document", "chat", "decision", "ticket"].map((k) => (
                    <option key={k}>{k}</option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              Title
              <input value={title} onChange={(e) => setTitle(e.target.value)} />
            </label>
            <div className="formGrid">
              <label>
                Source updated (UTC)
                <input
                  type="datetime-local"
                  value={updated}
                  onChange={(e) => setUpdated(e.target.value)}
                />
              </label>
              <label>
                Visible to
                <select
                  value={groups}
                  onChange={(e) => setGroups(e.target.value)}
                >
                  {["engineering", "all_employees", "leadership"].map((g) => (
                    <option key={g}>{g}</option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              Expected revision ID (for an update)
              <input
                value={expected}
                onChange={(e) => setExpected(e.target.value)}
                placeholder="Leave empty for a new source"
              />
            </label>
          </>
        )}
        {error && (
          <div className="errorBanner" role="alert">
            {error}
          </div>
        )}
        <button className="primary" disabled={busy || !file} onClick={submit}>
          {busy ? (
            <LoaderCircle size={16} className="spin" />
          ) : (
            <Upload size={16} />
          )}
          Import & index
        </button>
      </div>
    </Modal>
  );
}
