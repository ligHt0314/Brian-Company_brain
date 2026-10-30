# BrightMart: a demo anyone can follow

BrightMart is a completely fictional online grocery company. Local shops use its software to sell groceries, take payments, arrange deliveries, return money and help shoppers. No real employee or customer data is included.

Open **http://localhost:3000/guide** for the workspace handbook.

## How much data is here?

| Item | Seed count |
|---|---:|
| Employees | 40 |
| Teams | 8 |
| Projects | 10 |
| Software systems (services) | 16 |
| Grocery-store customers | 10 |
| Work tickets | 60 |
| Recorded decisions | 24 |
| Customer promise entities | 12 |
| All entity records | 180 |
| Source records | 200 |
| Independently supported claims | 432 |

A source is one readable document, chat export, ticket export, decision or directory. The 200 sources consist of 94 documents, 21 chat exports, 60 tickets, 24 decisions and one company directory. A claim is one supported statement, such as “Easy Checkout uses Checkout Service.” Some registered entities intentionally have missing facts, so the agent can demonstrate honest uncertainty.

The live counts depend on identity and subsequent imports. Initially Engineer can access 196 sources, Lead 200, and Viewer 23. Demo switching is a simulation, not real company authentication. Published seed counts in the guide are a description of the prepared synthetic corpus, not a private-source count from a user's investigation.

## The main story

**Easy Checkout** is a project to make placing a grocery order easier. It needs **Checkout Service**, which depends on **Payment Gateway**, the connection to the bank. **T-101** records a blocked payment check. **C-101** is a rollout promise to **Green Basket Stores**, due 18 October 2026.

The Payment Gateway working guide says **Payments** owns it. A handoff chat says **Integrations** owns it. **Maya Rao** and **Dev Shah** have documented relevant work. Their experience is useful, but it does not settle the ownership disagreement.

The source records contain each relationship separately. The agent must join them; it cannot get the full story by returning one matching document. This guide is a prepared narrative, not an ingested golden answer.

## A five-minute presentation

1. Open Investigate as **Engineer** and click **Find launch risks**. Ask: “What could block Easy Checkout, and which customer commitment is affected?” Show the blocked ticket, the complete path and the promise. Click a citation and read the exact source passage.
2. Open the Graph tab. Explain it in ordinary language: “The project needs this system; this system needs the bank connection; this ticket blocks that connection.” The numbered citations support those links.
3. Ask: “Who owns Payment Gateway, and who has worked on it?” Explain why conflicting sources stay visible. Prepare a review task, select an assignee, preview it and confirm it. It stays inside Company Brain.
4. Ask: “What may be affected if Payment Gateway becomes unavailable?” Explain why refunds and recurring grocery orders can also be at risk. This is a conditional impact, not a claim that an outage happened.
5. Ask: “Why did we rule out unconfirmed payments for Easy Checkout?” Read D-101: the order must not be confirmed until the bank has accepted payment.
6. Switch to **Lead**. Ask the launch question under that identity, then open Sources and choose **Update ticket status**, select T-101, select Done and save. Return to the saved Lead answer in History and rerun. Show “What changed” and the status citation. The ownership conflict remains; fixing one ticket does not prove the launch is ready.
7. Switch to **Viewer** and ask the same question. It cannot use engineering evidence. Explain that the same graph can produce a more limited answer because source access differs.

The status editor intentionally changes the source record. To repeat the blocked-state story, use the same editor to set T-101 back to Blocked. For a repeated blocked-state presentation, an operator can use `make demo-reset` with the private operator token. The endpoint requires the exact synthetic BrightMart graph. It rebuilds graph facts/reviews but retains private history, which is revalidated when read. Never share `.env` or use `docker compose down -v` as a casual reset.

## Other stories

| Project | Everyday purpose |
|---|---|
| Easy Checkout | Place and pay for an order |
| Sales Dashboard | Help shop managers understand sales |
| Delivery Tracking | See where a delivery is |
| Quick Refunds | Return money after an approved cancellation |
| Stock Alerts | Warn before products run out |
| Store Pickup | Reserve a collection slot |
| Customer Rewards | Earn reward points |
| Seller Dashboard | Help partner shops manage online sales |
| Help Center | Help shoppers with problems |
| Fresh Subscriptions | Receive a regular grocery box |

Try “What could block Delivery Tracking?” or “What could block Quick Refunds?” These are independent investigations over their own graph paths, not aliases for the checkout answer. Tickets have blocked, open, in-progress, done, cancelled and one unknown status; the agent must distinguish them.

## What the agent actually does

1. Gemini interprets the question and selects a known entity.
2. It selects approved, read-only tools, observes their real graph results, then chooses additional reads where needed.
3. FalkorDB supplies current accepted claims from permitted sources. The model cannot execute arbitrary queries or writes.
4. Graph reasoning builds the supported findings and paths. Gemini can add a cited inference. Model failures use a visible deterministic fallback.
5. The app shows citations, conflicts and missing evidence. Execution details show the actual model calls and tool trace.

Investigations keep six tool reads, two selection rounds and three dependency hops. The larger seed uses a bounded 2,000-claim permission-filtered snapshot, a maximum 150 claims per selected tool result, 32 answer excerpts, and a graph projection of 30 nodes/50 edges. Reaching a budget is disclosed as partial scope. This is a medium demonstration corpus, not a performance claim about enterprise-scale data.

## Inspect or regenerate the dataset

- `fixtures/brightmart/registry.json`: public entity IDs and aliases.
- `fixtures/brightmart/manifest.json`: source checksums and exact seed counts.
- `fixtures/brightmart/*.json`: readable original bodies and exact-span reviewed claims.
- [BrightMart-Sourcebook.md](BrightMart-Sourcebook.md): all 200 source bodies in one human-readable book, with access labels.
- `python3 scripts/build_fixtures.py`: regenerate the same dataset and guide metadata deterministically.

Fixtures use reviewed extraction artifacts; they do not pretend that 200 sources were extracted live by Gemini. New Markdown/text imports use the configured live model. The source book is local demo material and includes all synthetic access levels; it is not a public endpoint bypassing the app's permission checks.
