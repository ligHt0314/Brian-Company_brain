# Graph Report - Company Brian  (2026-10-30)

## Corpus Check
- 288 files · ~120,908 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 558 nodes · 1367 edges · 48 communities (27 shown, 21 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 125 edges (avg confidence: 0.52)
- Token cost: 29,115 input · 1,764 output

## Community Hubs (Navigation)
- Investigation & Reasoning Loop
- Domain Entities & Validation
- Web UI & Workspaces
- FastAPI Routing & Auth Middleware
- Evaluation & FalkorDB Scripts
- Work Items & Action Models
- Frontend Package Dependencies
- TypeScript Configuration
- Work Operations & Mutations
- Fixtures Manifest & Entities
- DigiPlus Fixture Builder
- Demo Video Automation
- Next.js API Proxy Routes
- Next.js Root Layout
- Agent Reasoning Prompts
- Client Portals & Infrastructure
- Next.js Server Config
- Next.js Type Declarations
- BrightMart Showcase Docs
- Local Environment Initialization
- Source Packaging Automation
- API Container Startup
- Contributor Guidelines
- System Component Map
- Architecture Decisions
- Canonical Graph Schema
- Docker Compose Config
- DigiPlus Showcase Docs
- BrightMart Workspace MVP
- Monorepo Root Config
- Planning Prompt v1.1
- Brian README
- Entity Extraction Prompt
- SQLite Operational Store

## God Nodes (most connected - your core abstractions)
1. `Strict` - 64 edges
2. `Work` - 31 edges
3. `Provider` - 30 edges
4. `login()` - 29 edges
5. `registry()` - 26 edges
6. `Candidate` - 25 edges
7. `now_iso()` - 24 edges
8. `Investigator` - 24 edges
9. `uid()` - 22 edges
10. `require()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Event` --uses--> `Strict`  [INFERRED]
  services/api/app/work/models.py → services/api/app/domain/models.py
- `KnowledgeLink` --uses--> `Strict`  [INFERRED]
  services/api/app/work/models.py → services/api/app/domain/models.py
- `Query and Agent Execution` --calls--> `Tool Selector Prompt v1.2`  [INFERRED]
  Architecture.md → services/api/app/prompts/tools-v1.2.txt
- `Ingestion` --uses--> `Provider`  [INFERRED]
  services/api/app/ingestion/service.py → services/api/app/agent/provider.py
- `Work` --uses--> `Provider`  [INFERRED]
  services/api/app/work/service.py → services/api/app/agent/provider.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Agent Reasoning Pipeline** — services_api_prompts_tools, services_api_prompts_synthesis [EXTRACTED 1.00]
- **BrightMart Dataset Documentation** — docs_brightmart_demo, docs_brightmart_sourcebook, docs_product_mvp [EXTRACTED 1.00]

## Communities (48 total, 21 thin omitted)

### Community 0 - "Investigation & Reasoning Loop"
Cohesion: 0.06
Nodes (64): Answer, BaseModel, Exception, investigate_with_tools(), A bounded model/tool/result loop; all writes remain outside investigation tools., Provider, Small provider boundary. No model output is executable or authoritative by…, Synthesis (+56 more)

### Community 1 - "Domain Entities & Validation"
Cohesion: 0.07
Nodes (59): field_validator, fixture, parametrize, Candidate, model_validator, SourceEnvelope, chunks(), Ingestion (+51 more)

### Community 2 - "Web UI & Workspaces"
Cohesion: 0.06
Nodes (54): Action, ActionDialog(), AddActionDialog(), Brief, CreateDialog(), date(), Detail, done() (+46 more)

### Community 3 - "FastAPI Routing & Auth Middleware"
Cohesion: 0.10
Nodes (58): BackgroundTasks, exception_handler, Me, middleware, Response, current_user(), Request, require() (+50 more)

### Community 4 - "Evaluation & FalkorDB Scripts"
Cohesion: 0.07
Nodes (15): BaseSettings, FalkorDB, Deterministic regression evaluation against isolated real FalkorDB graphs.…, Reversible, one-time Orbit -> BrightMart replacement. Run with the API stopped.…, Explicit live-model gate. Uses synthetic data and an isolated FalkorDB graph.…, Controlled local synthetic-demo outage/restart rehearsal. Requires dev graph…, Opt-in paid-provider check on a random disposable graph, never the working…, Settings (+7 more)

### Community 5 - "Work Items & Action Models"
Cohesion: 0.13
Nodes (35): Action, ActionCreate, ActionDraft, ActionPatch, Brief, BriefRequest, DecisionDraft, Event (+27 more)

### Community 6 - "Frontend Package Dependencies"
Cohesion: 0.06
Nodes (35): dependencies, lucide-react, next, react, react-dom, @xyflow/react, devDependencies, openapi-typescript (+27 more)

### Community 7 - "TypeScript Configuration"
Cohesion: 0.07
Nodes (27): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+19 more)

### Community 8 - "Work Operations & Mutations"
Cohesion: 0.23
Nodes (4): event(), closed(), One atomic reviewed mutation, including immutable snapshots and graph epoch., Work

### Community 9 - "Fixtures Manifest & Entities"
Cohesion: 0.08
Nodes (25): action_count, claim_count, company, entity_counts, Commitment, Customer, Decision, Person (+17 more)

### Community 10 - "DigiPlus Fixture Builder"
Cohesion: 0.22
Nodes (4): Path, Build DigiPlus Services's reproducible, entirely fictional IT services company.…, build(), Reproducible service-delivery meetings and handovers, with exact note evidence.

### Community 14 - "Agent Reasoning Prompts"
Cohesion: 0.67
Nodes (3): Query and Agent Execution, Synthesis Prompt v1.1, Tool Selector Prompt v1.2

### Community 15 - "Client Portals & Infrastructure"
Cohesion: 0.67
Nodes (3): Atlas Client Portal, Identity Gateway, Platform Engineering

## Knowledge Gaps
- **106 isolated node(s):** `dynamic`, `metadata`, `Meeting`, `Action`, `Detail` (+101 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Strict` connect `Investigation & Reasoning Loop` to `Domain Entities & Validation`, `FastAPI Routing & Auth Middleware`, `Evaluation & FalkorDB Scripts`, `Work Items & Action Models`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `Work` connect `Work Operations & Mutations` to `Investigation & Reasoning Loop`, `Domain Entities & Validation`, `Work Items & Action Models`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `Provider` connect `Investigation & Reasoning Loop` to `Work Operations & Mutations`, `Domain Entities & Validation`, `Work Items & Action Models`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `Strict` (e.g. with `Synthesis` and `ToolArguments`) actually correct?**
  _`Strict` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Provider` (e.g. with `ToolDecision` and `Extraction`) actually correct?**
  _`Provider` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `dynamic`, `metadata`, `Meeting` to the rest of the system?**
  _106 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Investigation & Reasoning Loop` be split into smaller, more focused modules?**
  _Cohesion score 0.06470588235294118 - nodes in this community are weakly interconnected._