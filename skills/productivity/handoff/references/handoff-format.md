# The handoff format

A handoff is the document that lets work change hands without losing a thing. The author is about to vanish from the loop — a fresh session with no memory, a teammate picking up an unfinished branch, a future self three weeks from now — and the handoff is the only bridge across that gap. Everything the author knows and the reader will need has to cross the bridge in writing.

## The resumability principle

One test governs the whole document: **a fresh reader, with no access to the author, resumes the work without asking a single question.** Resumability is the bar. Every section earns its place by closing a question the reader would otherwise have to ask — and since the author is gone, an unanswered question is a hard stop, not a minor friction.

This principle decides what goes in. A detail the reader needs to continue belongs in the handoff. A detail that only explains how the author got here, with no bearing on the next step, stays out. The reader is trying to *move forward*, not to relive the session.

## Handoff versus status report

A status report and a handoff describe the same work and serve opposite purposes. The difference is direction.

| | Status report | Handoff |
|---|---|---|
| Faces | Backward — what happened | Forward — what to do next |
| Audience | An observer who wants to know | A successor who must continue |
| Success | The reader understands progress | The reader resumes the work |
| Next actions | Optional, often absent | Mandatory and concrete |
| Gotchas | Rarely included | Required — they save the reader |
| Lifespan | A snapshot, then discarded | Living, until the work is done |

A status report that says "authentication is 70% complete" informs the reader and strands them. A handoff says "the login route works; the token-refresh path in `auth/refresh.ts` is stubbed — implement it next, then run `npm test auth`." The first reports a percentage; the second hands over the work. When a document lists no next action and names no gotcha, the document is a status report wearing a handoff's title.

## What a complete handoff contains

A complete handoff carries nine parts. Each part closes a question the reader would otherwise ask the absent author.

1. **The goal.** One or two sentences naming what the work must ultimately deliver. Without the goal, the reader executes steps with no way to judge whether a step still serves the point. The goal is the yardstick every later section is measured against.

2. **Current state.** Where the work actually stands at handoff time: the branch, what builds and runs, what is broken, the last action taken. The reader's very first question is "where are we" — current state answers it. A handoff missing this section forces the reader to reconstruct the present by hand, which is exactly the loss the handoff was meant to prevent.

3. **What is done.** The work already finished, so the reader neither redoes it nor distrusts it. A crisp done-list is also the proof-of-progress that a status report stops at — necessary here, but never sufficient on its own.

4. **What remains, as concrete next actions.** The heart of the handoff. Each remaining item is rewritten as an action specific enough to begin cold — the file to open, the function to change, the command to run, the expected outcome. "Improve error handling" is a wish. "Wrap the `fetchUser` call in `api/user.ts` in a try/catch and return a 404 on miss" is a next action. The litmus: a remaining item that needs a follow-up question before the reader can start is not yet concrete.

5. **Files and artifacts touched.** The files changed, created, or deleted, plus any external artifacts — a migration, a deployed preview, a draft PR, a design doc. This list is the map of the blast radius, so the reader knows where the work lives without grepping the whole tree.

6. **Decisions made, with their reasons.** The choices taken and *why a choice beat the alternative considered.* A decision recorded without its reason is a decision the reader will reverse the moment it inconveniences them, re-litigating a question the author already settled. "Chose polling over websockets — the host caps concurrent sockets at 100, below our peak" survives; "chose polling" does not.

7. **Gotchas and landmines.** The traps a reader steps on without warning: the flaky test that fails one run in five, the service that must boot before the suite, the off-by-one that already cost an hour, the env var with no default. This section is pure transferred scar tissue — each entry is a wound the author took so the reader does not have to. An undocumented gotcha gets rediscovered the hard way, on the reader's time.

8. **How to verify.** The exact command or steps that prove the work correct, and the result to expect. Verification lets the reader confirm the inherited state is real before building on it, and confirm their own additions afterward. "Run `make test` — 142 pass, 0 fail" beats "tests should pass."

9. **Blockers.** Anything that stops forward progress — a missing credential, a pending review, an unanswered product question — paired with who or what clears it. A blocker named with its owner is a path forward; a blocker discovered cold is a dead end the reader hits at speed.

## Where the handoff lives, and keeping it current

A handoff lives in a **durable, committed file**, never in chat scrollback and never in memory. Chat history is gone the moment the session resets — which is the precise event the handoff prepares for. Put the document in a `HANDOFF.md` at the repo root, in a doc beside the work, or in the ticket the work belongs to. The location matters less than its survival across the author's disappearance.

A handoff is a living document until the work is done. Stale instructions are worse than none, because they actively mislead a reader who trusts them. So the handoff is updated whenever the state moves: a finished next-action moves from "remaining" to "done," a cleared blocker comes off the list, a fresh gotcha goes on it. The discipline is simple — the handoff is rewritten at the moment work pauses, not reconstructed from memory hours later when the details have already blurred.

## Failure modes

Four failure modes account for most handoffs that fail their reader.

- **Missing current-state.** The handoff lists tasks but never says where things stand right now. The reader cannot tell what already runs versus what is half-built, and burns the first hour reconstructing the present the author could have stated in three lines.
- **Vague next-actions.** Remaining work is phrased as wishes — "finish the API," "tidy the tests," "improve performance." Each forces the reader back to the author for the specifics, and the author is gone. Vagueness is the single most common way a handoff fails the resumability test.
- **No gotchas.** The handoff records the happy path and omits the traps. The reader steps on every landmine the author already mapped, paying again in lost hours for knowledge that cost the author once and died unwritten.
- **Stale handoff.** The document describes a state two days and forty commits old. The reader follows instructions that no longer match the code, and trust in the whole document collapses on the first contradiction.

## Red flags

Signs a handoff will strand its reader:

- No next action is named — the reader is told the state but not the move.
- A next action cannot be started without a follow-up question to the author.
- A decision appears with no reason, inviting the reader to reverse it.
- The verification step is absent or vague ("it should work").
- The "current state" section is missing, so the present must be reconstructed.
- The document sits in chat or a scratch buffer rather than a committed file.
- The handoff's timestamp predates the latest commits — a stale map.
- The document only narrates what happened and hands over nothing to do.
- A known blocker is mentioned with no owner and no path to clearing it.

## A worked example

A half-finished feature: add CSV export to the reports page. The session ends mid-task. The handoff below would let a fresh agent resume cold.

```markdown
# Handoff: CSV export for reports page

## Goal
Let a user on /reports download the current filtered table as a CSV,
matching the columns and filters shown on screen.

## Current state
Branch: feature/csv-export (pushed, no PR yet).
The download button renders and the server route responds; the CSV body
is wrong — every row exports unfiltered. App builds and runs clean.
Last action: wired the button to GET /api/reports/export.

## Done
- Added the "Export CSV" button to ReportsToolbar.tsx.
- Added route GET /api/reports/export in api/reports/export.ts.
- CSV header row generates correctly from the column config.

## Remaining (next actions)
1. Pass the active filters into the export query. The filter state lives
   in useReportFilters(); the route in export.ts currently ignores the
   query string and calls findAll(). Read filters from req.query and
   pass them to findFiltered() — the same function the table already uses.
2. Escape commas and quotes in cell values. Each value goes through
   the formatCell() helper in csv-utils.ts, which is a stub returning
   String(value). Implement RFC-4180 quoting there.
3. Add a test in export.test.ts asserting a filtered export returns
   only matching rows. None exists yet.

## Files touched
- src/components/ReportsToolbar.tsx (new button)
- src/api/reports/export.ts (new route, filter wiring incomplete)
- src/lib/csv-utils.ts (formatCell stub — needs real quoting)

## Decisions
- Server-side export, not client-side. The table paginates and the
  client holds one page; only the server can stream the full result.
- Reused findFiltered() rather than a new query path, so export and
  on-screen table can never drift out of sync.

## Gotchas
- findAll() and findFiltered() take different argument shapes; copying
  the table's call into the route verbatim throws a type error. Adapt
  req.query to the filter object findFiltered() expects.
- The export.test.ts harness needs a seeded DB. Run `npm run seed:test`
  before the suite or the export returns empty and the test passes
  for the wrong reason.

## How to verify
1. `npm run dev`, open /reports, apply any column filter.
2. Click Export CSV; open the file.
3. Expected: only the filtered rows, commas inside values intact.
4. `npm run seed:test && npm test export` — the filtered-export
   test passes.

## Blockers
None. The product question about including a totals row was resolved:
no totals row in v1 (decided with Dana, 2026-06-21).
```

Read that document as the fresh reader. The goal sets the yardstick, current state pins the present, the next actions start cold, the gotchas pre-empt both traps, and verification closes the loop. No question for the absent author remains — which is the whole point.
