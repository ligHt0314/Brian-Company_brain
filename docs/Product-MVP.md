# BrightMart workspace MVP

Updated 17 October 2026.

The website now uses a professional Company Brain workspace presentation. Demo/synthetic labels were removed from application chrome, onboarding, role controls and footers at the user's request. This does not change the underlying fictional data's provenance, which remains documented in the fixture manifest, verification records and source book.

## Working product workflows

- Investigate project risks, ownership, decisions and dependency impact through the configured Gemini agent and permission-filtered FalkorDB graph.
- Inspect exact citations and graph paths; see conflicts, missing evidence, current/historical source revisions, real execution details and explicit provider fallback.
- Search and filter all accessible source records, upload Markdown/text/structured JSON, and inspect import status.
- Update any accessible single-ticket source as Lead through **Sources → Update ticket status**. The editor loads current status and revision, accepts a new validated status, preserves non-status claims, contributor records, pending review scores and validity, and creates an immutable source revision. Stale edits are rejected. Overlapping evidence that cannot safely be changed requires a source-file update instead.
- Rerun saved investigations after an update and inspect evidence-backed changes. Review tasks retain their cited evidence and require preview/confirmation before creation.
- Browse a workspace handbook, project directory, searchable people directory and system glossary. Counts use the current public directory and access-filtered source data rather than fixed seed totals.

Status edits are reviewed records. They do not call an LLM or pretend that a human edit was extracted by a model. The previous fixed T-101 completion shortcut is no longer in the website; regression-only fixture endpoints remain internal compatibility tools.

## Scope

This is a functional local MVP on the current BrightMart corpus. Existing role-preview sessions, one-worker consistency, source permissions and private operational storage remain in place. Production authentication, customer onboarding, live connectors, hosting, multi-tenant isolation and broad human quality evaluation remain separate work. A visual polish pass does not establish production security or universal answer correctness.

The interface describes workspace access and source evidence; it does not claim SSO, enterprise certification, live SaaS connections or autonomous business decisions. Source citations are preserved exactly rather than rewritten to remove provenance language from underlying records.
