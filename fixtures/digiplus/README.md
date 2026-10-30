# DigiPlus Services dataset

A fictional IT consulting and managed-services company, independent of any real DigiPlus organization.

- 40 people, 8 teams, 10 enterprise clients and 10 delivery projects.
- 16 shared systems, 60 tickets, 24 decisions and 12 commitments.
- 200 knowledge sources with 432 exact-span assertions.
- 40 connected meetings/handovers and 100 distinct action items, including repeated appearances of the same items in follow-ups.
- Missed meetings, leave coverage, overdue work, completed/cancelled outcomes and leadership-only context.

`registry.json` is the shared directory. `manifest.json` checksums the knowledge sources. `workflows.json` contains canonical seed meeting/action records and their exact note quotations. These are input records, not canned AI answers. New recaps and catch-up briefs use the configured provider and expose failures.

Regenerate with `python3 scripts/build_fixtures.py`. Startup only inserts missing records; it preserves your edits. See the root README for setup and the guided scenario. Keep this folder: it is needed at startup and runtime. Never add credentials or real client exports without review.
