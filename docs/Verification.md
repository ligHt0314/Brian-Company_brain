# Local verification record — BrightMart

Updated 17 October 2026 (IST). All company data is synthetic. This record supersedes the small Orbit dataset counts.

## Corpus and backend

BrightMart seed 2.0 has 200 sources, 180 entities and 432 accepted claims. Tests validate every exact source span and supported predicate/type, all source pagination pages, all 180 public directory entries and per-persona access (196/200/23). New graph cases verify Delivery Tracking's own blocker chain, Quick Refunds sharing the payment blocker, and conditional Payment Gateway impact across checkout, refunds and subscriptions.

`pytest -q`: **41 passed**, using isolated randomly named real FalkorDB graphs. Existing checks cover revisions, failed updates, idempotency, private sessions, ACL revocation, agent budgets/tool validation and incomplete-plan fallback. One upstream Starlette/httpx TestClient deprecation warning remains.

`make check`: Ruff, Pydantic/OpenAPI synchronization and strict TypeScript pass. `make contract` regenerated API types after fixture IDs/entity lookup changed. Production `make build` passes.

`make evaluate`: **24/24** deterministic questions pass against seed 2.0. Thirty warm engine runs measured median 54 ms and p95 63 ms. Timings exclude HTTP/browser/LLM latency. These are local measurements, not enterprise-scale claims. Reports: evals/results/latest.json and latest.md. Human factual-support scoring remains unperformed.

## Live Gemini

The isolated live gate passed with `gemini-3.1-flash-lite`. It imported previously unseen text about Maya Rao, Customer Messages and Payment Gateway, accepted two exact-quote model claims, retrieved the new evidence and checked Viewer isolation. The release investigation used **five reads across two selection rounds**, four model calls, and completed in **16.2 seconds**, with no synthesis-failure warning in that run. New-document retrieval took 7.1 seconds. Full record: artifacts/gemini-live-verification.json. The test's temporary graph was removed; the working dataset was not modified.

This confirms the observed synthetic scenarios, not broad answer correctness or calibrated model confidence. Token costs and human semantic-support scores were not measured.

## Runtime and retirement

The old dataset is no longer active. Its graph is recoverable under `retired_company_brain_orbit_demo_20261017`, and operational history is preserved in SQLite table `retired_orbit_records_20261017`. Original uploads were preserved. Permanent removal was blocked by automatic approval review; reversible retirement completed instead. No other graph was reset.

The standard Docker build stalled at upstream registry metadata resolution. Cached application runtimes were repackaged with validated sources and the successful local Next.js standalone build, and the stack started with `make up BUILD_FLAG=--no-build`. Default `make up` and the normal Dockerfiles remain available for a fresh networked build. A clean-network/fresh-volume build of this expanded seed has not been repeated.

Desktop/mobile browser results are appended after the final pass. The in-app guide was visually inspected at desktop size. Old Orbit media was removed rather than presented as proof of BrightMart behavior. The earlier persistence rehearsal in artifacts/persistence.json refers to Orbit, not the expanded dataset; no new durability claim is made from it.

## Open gates

No production authentication, live Slack/Drive/Jira integration, public hosting, multi-company onboarding, general historical reconstruction, narrated competition video or submission was completed. Full accessibility conformance is not claimed. Every demo identity is synthetic; source permissions demonstrate behavior rather than production account security.

## Browser verification

All **10 Playwright cases passed** on desktop (1440 px) and mobile (390 px) against the running BrightMart stack. The new case checks the guide, glossary, tenth project, editable example question, complete entity picker and searching T-160 beyond the first source page. Existing cases inspect citations with keyboard/Escape, graph, confirmed reviews, stale proposals, source revisions, changed-answer evidence, permission changes, saved-run errors and overflow. T-101 was restored to blocked after update checks. The run took 1.3 minutes; live-provider availability can lead to labeled deterministic fallbacks.

The final backend rerun passed **38 tests**, including an additional three-hop boundary case and checks that displayed graph edges reference displayed nodes. A first attempt at that final rerun found the development DB port closed after normal Compose startup; restoring the loopback test port resolved the infrastructure error. The stack smoke check passed after browser mutation tests finished (a concurrent attempt correctly returned knowledge_changed during their source revision).


## Product MVP update — 17 October 2026

The polished interface and general ticket-status editor passed 41 backend tests, strict TypeScript, OpenAPI synchronization, Ruff and a production web build. Three new integration cases verify edits to non-canonical tickets, contributor/provenance preservation, pending review score/validity retention, stale revision rejection, access checks and risk/update/restore behavior through the normal endpoint. The 24-case corpus regression passed. The warm sample now uses its own random graph and measured 54 ms median / 63 ms p95 under the current local workload; it does not touch the configured working graph.

The active website no longer contains demo/synthetic labels in navigation, guide, role controls or footer. Browser checks assert their absence on the handbook and exercise the searchable people directory. The dataset and archived source provenance were preserved. Public production authentication and hosting were not added or claimed. Browser completion results and screenshots follow below.

Final product browser gate: **10/10 passed** (desktop and mobile, 1.1 minutes). The ticket update case used the ordinary status editor and verified the rerun/change summary; cleanup restored T-101 to its previous blocked state. The handbook case checks absence of demo/synthetic/fictional chrome, the searchable people directory and source pagination. Product screenshots are artifacts/workspace-home-desktop.png, workspace-home-mobile.png, workspace-guide-desktop.png and workspace-guide-mobile.png.
