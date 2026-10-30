"use client";
import { useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  GitBranch,
  Search,
  ShieldCheck,
  Users,
} from "lucide-react";
import catalog from "@/lib/workspace-catalog.json";
import type { Entity } from "@/lib/api/client";

const workflows = [
  {
    title: "Understand launch risks",
    question:
      "What could block Atlas Client Portal, and which customer commitment is affected?",
    detail:
      "Connect open tickets to the systems, projects and customer commitments they affect.",
  },
  {
    title: "Find ownership and experience",
    question: "Who owns Identity Gateway, and who has worked on it?",
    detail:
      "Compare ownership records and find people with relevant contributions. Conflicting records stay visible.",
  },
  {
    title: "Assess a proposed change",
    question: "What may be affected if Identity Gateway becomes unavailable?",
    detail:
      "Trace dependencies across projects and see which commitments may be affected.",
  },
  {
    title: "Understand a decision",
    question:
      "Why did we rule out unverified identities for Atlas Client Portal?",
    detail:
      "Read the recorded rationale, with a direct reference to the passage that supports it.",
  },
];
export default function WorkspaceGuide({
  onAsk,
  entities,
  sourceCount,
}: {
  onAsk: (text: string) => void;
  entities: Entity[];
  sourceCount: number;
}) {
  const [peopleQuery, setPeopleQuery] = useState("");
  const people = entities.filter(
    (e) =>
      e.kind === "Person" &&
      e.label.toLowerCase().includes(peopleQuery.toLowerCase()),
  );
  return (
    <div className="workspaceGuide">
      <div className="pageHeading">
        <div>
          <div className="eyebrow">WORKSPACE HANDBOOK</div>
          <h1>Work with a clearer picture.</h1>
          <p>
            Your guide to DigiPlus Services’s projects, people and connected
            knowledge.
          </p>
        </div>
        <span className="guideHeadingIcon">
          <BookOpen size={25} />
        </span>
      </div>
      <section className="guidePanel companyOverview">
        <div>
          <span className="sectionEyebrow">DIGIPLUS</span>
          <h2>One workspace. Connected work.</h2>
          <p>
            DigiPlus Services delivers software projects and managed IT support
            to enterprise clients. Teams work together on portals, identity,
            project delivery, claims, infrastructure and customer care. Company
            Brain connects their records so you can understand what needs
            attention and why.
          </p>
        </div>
        <div className="guideNumbers">
          <span>
            <strong>
              {entities.filter((e) => e.kind === "Person").length}
            </strong>{" "}
            people
          </span>
          <span>
            <strong>{entities.filter((e) => e.kind === "Team").length}</strong>{" "}
            teams
          </span>
          <span>
            <strong>
              {entities.filter((e) => e.kind === "Project").length}
            </strong>{" "}
            projects
          </span>
          <span>
            <strong>{sourceCount}</strong> accessible sources
          </span>
        </div>
        <p className="guideMuted">
          Directory totals describe the workspace. Sources and investigation
          results follow the access of your selected workspace role.
        </p>
      </section>
      <section aria-labelledby="workflows">
        <div className="guideSectionHeading">
          <div>
            <span className="sectionEyebrow">
              GET ANSWERS THAT MOVE WORK FORWARD
            </span>
            <h2 id="workflows">Start with a question</h2>
          </div>
        </div>
        <div className="guideGrid">
          {workflows.map((w) => (
            <article className="guidePanel workflowCard" key={w.title}>
              <h3>{w.title}</h3>
              <p>{w.detail}</p>
              <p className="guideQuestion">{w.question}</p>
              <button className="secondary" onClick={() => onAsk(w.question)}>
                Try this question <ArrowRight size={15} />
              </button>
            </article>
          ))}
        </div>
      </section>
      <section className="guidePanel">
        <h2>From question to action</h2>
        <div className="guideFlow">
          <span>
            <Search size={18} /> Ask a question
          </span>
          <ArrowRight size={18} />
          <span>
            <GitBranch size={18} /> Follow the connections
          </span>
          <ArrowRight size={18} />
          <span>
            <BookOpen size={18} /> Inspect the evidence
          </span>
          <ArrowRight size={18} />
          <span>
            <ShieldCheck size={18} /> Take the next step
          </span>
        </div>
        <p>
          Open any numbered citation to read the exact supporting passage. Use
          the relationship graph to follow the path between a ticket, a system,
          a project and a customer promise. Where records disagree, compare both
          sources before deciding what to do.
        </p>
        <ol className="guideActionList">
          <li>
            <strong>Assign an ownership review.</strong> Choose Prepare review
            task from an investigation, select a colleague, preview the evidence
            and confirm the internal task.
          </li>
          <li>
            <strong>Keep ticket status current.</strong> Leads can open{" "}
            <Link href="/sources">Sources</Link>, choose Update ticket status,
            select a ticket and save its new status. This creates a source
            revision and preserves other evidence.
          </li>
          <li>
            <strong>See what changed.</strong> Open a previous investigation in
            History and rerun it after a source update. The change summary
            explains which findings were added or removed.
          </li>
        </ol>
      </section>
      <section id="projects">
        <div className="guideSectionHeading">
          <div>
            <span className="sectionEyebrow">PROJECT DIRECTORY</span>
            <h2>Explore the work</h2>
          </div>
          <span className="countPill">{catalog.projects.length} projects</span>
        </div>
        <div className="guideGrid">
          {catalog.projects.map((p) => (
            <article className="guidePanel projectCard" key={p.id}>
              <span className="projectCardIcon">
                <GitBranch size={19} />
              </span>
              <h3>{p.name}</h3>
              <p>{p.purpose}</p>
              <button className="textButton" onClick={() => onAsk(p.question)}>
                Investigate this project <ArrowRight size={15} />
              </button>
            </article>
          ))}
        </div>
      </section>
      <section id="people" className="guidePanel">
        <div className="guideSectionHeading">
          <div>
            <span className="sectionEyebrow">PEOPLE DIRECTORY</span>
            <h2>Find your colleagues</h2>
          </div>
          <Users size={22} />
        </div>
        <label className="searchInput">
          <Search size={17} />
          <input
            aria-label="Search people"
            placeholder="Search by name…"
            value={peopleQuery}
            onChange={(e) => setPeopleQuery(e.target.value)}
          />
        </label>
        <div className="peopleDirectory">
          {people.map((p) => (
            <div className="directoryPerson" key={p.id}>
              <span className="personInitials">
                {p.label
                  .split(" ")
                  .map((w) => w[0])
                  .slice(0, 2)
                  .join("")}
              </span>
              <span>{p.label}</span>
            </div>
          ))}
        </div>
        {!people.length && (
          <p className="guideMuted">No people match this search.</p>
        )}
      </section>
      <section className="guidePanel">
        <span className="sectionEyebrow">SYSTEMS & TERMINOLOGY</span>
        <h2>Know what each system does</h2>
        <p>
          A service is one part of the company’s software with a specific job.
        </p>
        <dl className="guideGlossary">
          {catalog.glossary.map((g) => (
            <div key={g.name}>
              <dt>{g.name}</dt>
              <dd>{g.meaning}.</dd>
            </div>
          ))}
        </dl>
      </section>
      <section className="guidePanel guideTrust">
        <ShieldCheck size={23} />
        <div>
          <h3>Evidence stays in context.</h3>
          <p>
            Answers use the current records your role can access. An unanswered
            question is an evidence gap; a dependency is a potential impact, not
            proof of an outage. Check the source before acting on a finding.
          </p>
        </div>
      </section>
    </div>
  );
}
