# The ralph loop

The reference behind the loop steps. "Ralph" names a technique: pin one stable prompt,
point it at a persistent backlog file, and run it in a tight loop where each iteration
re-reads the state, advances the work, proves it with a gate, and writes the new state
back — with no human between iterations. The loop runs unattended until a fixed
done-condition is met or a guardrail halts it. This page is the judgment the steps assume:
how the technique works, how to write the done-condition, what each guardrail does, the
contract of the state file, when ralph is the right tool, how it fails, and a worked
example.

Ralph is the autonomous cousin of the checkpointed
[app-completion-loop](../../app-completion-loop/SKILL.md). The checkpointed loop stops at
every phase boundary for a human to approve the plan and the result; ralph removes that
human and replaces the andon cord with hard, mechanical guardrails. That trade buys
throughput on a large, well-specified backlog and pays for it in risk — so the guardrails
below are not optional decoration, they are the only thing standing between the loop and a
runaway.

## The technique — one prompt, one state file, one loop

Three pieces compose the technique, and each stays fixed for the whole run:

- **One stable prompt.** A single, unchanging instruction drives every iteration. The
  prompt does not grow or mutate between passes; the *state* changes, the prompt does not.
  A typical prompt reads: "Read `handoff/state.json`. Take the top open backlog item.
  Make the smallest change that closes it. Run the gate. Update the state file. Stop." The
  stability is the point — a prompt that drifts iteration to iteration is no longer one
  loop, it is many, and reproducibility dies with it.
- **One persistent backlog file.** The work to do and the work done both live in a durable
  file on disk, not in the agent's context. Context resets between iterations; the file
  does not. The file is the single source of truth for loop position, so any iteration can
  reconstruct exactly where the loop stands by reading it.
- **One loop that re-reads state and continues.** Each iteration opens by reading the file
  fresh, advances one unit of work, gates it, and writes the file back. The loop carries no
  memory across iterations beyond what the file holds — a deliberate constraint that makes
  the loop resumable after a crash and immune to context rot over a long run.

The loop is autonomous: nothing pauses for human approval between iterations. Removing the
human is exactly what makes ralph fast and exactly what makes it dangerous, which is why
the done-condition and the guardrails carry the whole safety burden.

## The done-condition — the stop the loop runs toward

The loop terminates against a fixed target written before the first iteration. That target
is the **done-condition**: every item in the backlog complete *and* the gate green. Both
halves are required — an empty open set with a red gate is not done, and a green gate with
open items left is not done. Only the conjunction stops the loop with success.

Write the backlog first, as a numbered list, before a single iteration runs. A backlog item
is well-formed when it is:

- **Binary** — the item passes or fails with no middle; a gate, a test, or a scripted check
  decides it, not an opinion. "Improve the parser" is not an item; "the parser test suite
  exits zero on the malformed-input fixtures" is.
- **Gate-decidable** — the named gate command, or a check the gate runs, can rule on the
  item without a human reading the diff. An item no gate can decide has no place in an
  autonomous loop, because nothing unattended can close it.
- **Independent** — items do not overlap, so closing one cannot silently reopen another and
  the open set shrinks monotonically.
- **Mechanical** — the item is specified well enough that closing it needs execution, not a
  design decision. A backlog full of judgment calls belongs in the checkpointed loop, where
  a human rules on each.

The done-condition is the contract: when the open set is empty and the gate is green, the
loop is finished and nothing else is in scope. The loop never adds work to the backlog on
its own — discovered work is recorded and surfaced at termination, never absorbed mid-run.

Red flags: a backlog written as prose goals rather than gate-decidable items; an item no
gate could rule on; a "done-condition" that is just the iteration cap with no real target;
backlog items that need a human to judge whether they are closed.

## The guardrails — what keeps the loop safe

The checkpointed loop is kept safe by a human at every boundary. Ralph has no such human,
so safety is mechanical. Six guardrails bound the run, and every one is set before the
first iteration:

- **Bounded iteration cap (N).** A hard ceiling on iterations. The loop halts at N
  regardless of backlog state. The cap is the last-resort brake against an infinite loop —
  even if every other detector fails, the loop cannot run past N. Set N from the backlog
  size with headroom for retries, not to an open-ended large number.
- **Cost/time budget.** A ceiling on spend — wall-clock minutes, token cost, or both. The
  loop checks the accumulated spend at the top of each iteration and halts the moment the
  budget is exhausted. The budget bounds the blast radius of a loop that makes slow,
  expensive progress without ever quite stalling.
- **No-progress detector (K stalled rounds).** A counter of consecutive iterations that
  closed no backlog item. One stalled round is noise; K in a row is a halt. The detector
  catches the loop that is busy but not converging — editing, gating, failing, and
  retrying the same item forever. Reset the counter to zero on any iteration that closes an
  item; halt when it reaches K.
- **Gate-green required each iteration.** No iteration reports an item done with a red or
  skipped gate. The gate runs every pass and its result is recorded verbatim. A red gate
  reverts the item to open; it never advances behind a narrowed or skipped check. Eroding
  the gate to make an item pass is the silent-gate-skipping failure mode, and it is banned.
- **No destructive operations.** The loop runs no irreversible command unattended — no
  history rewrite, no recursive delete, no force-push, no schema drop. Destruction routes
  through a guarded helper or is forbidden outright, because no human is watching to catch a
  mistaken `rm`. Determinism doctrine: the dangerous path is structurally impossible, not
  merely discouraged.
- **No external mutation without approval.** The loop does not mutate state outside the
  working tree — no deploy, no production write, no third-party API call that changes
  remote state, no published release — without recorded prior approval. The loop's reach
  ends at the repository unless a human has signed off in advance on a specific external
  action.

A loop that trips a guardrail halts and writes its termination reason to the state file. A
guardrail halt is the loop working as designed; a loop that runs past its guardrails is the
exact failure this skill exists to prevent.

## The state file — the resumable contract

The loop carries no memory across iterations beyond a durable, committed state file. The
file ties to [handoff](../../../productivity/handoff/SKILL.md): it is a handoff the loop writes
to itself every iteration, so the next iteration — or a fresh agent after a crash — resumes
cold with zero context loss. Read it first each loop, write it back each loop.

A `handoff/state.json` holds, at minimum:

- **`backlog_open`** — the remaining items, top-first, each a binary gate-decidable
  condition.
- **`backlog_done`** — the closed items, so the loop neither redoes them nor distrusts them.
- **`iteration`** — the current count, checked against the cap N.
- **`spend`** — accumulated cost and elapsed time, checked against the budget.
- **`stall_count`** — consecutive iterations that closed nothing, checked against K.
- **`gate`** — the named gate command and its last recorded result.
- **`termination`** — empty while running; on halt, the reason (done, cap, budget, stall,
  guardrail) and the final counts.

The discipline is strict: every iteration opens by reading this file and closes by writing
it back atomically, so a reader never sees a half-written state and a crash mid-iteration
loses at most one item's progress. Loop position lives in the file, never only in the
agent's head — that is what makes the autonomous loop resumable.

Red flags: loop counters tracked in context instead of the file; a state file written
non-atomically, so a crash corrupts it; a file that records done items but not the stall
count or spend, blinding the guardrails; reconstructing position from chat scrollback after
a reset.

## When ralph fits — and when the checkpointed loop is safer

Ralph and the [app-completion-loop](../../app-completion-loop/SKILL.md) solve the same
shape of problem — drive a backlog to a gated done — and differ on one axis: whether a
human rules between iterations. Choose by the backlog, not by taste.

**Ralph fits** a large, mechanical, well-specified backlog:

- The work is repetitive and the pattern is known — migrate every call site to a new API,
  fix a lint rule across hundreds of files, port a test suite, regenerate fixtures.
- Each item is gate-decidable, so correctness needs no human judgment per step.
- The backlog is large enough that stopping for approval each step wastes the autonomy.
- A mistake is cheap to catch and revert, because the gate is strong and the blast radius
  is contained to the working tree.

**The checkpointed loop is safer** for high-stakes, judgment-heavy work:

- Each step forces a design decision a gate cannot make — an architecture choice, an API
  contract, a product trade-off.
- A mistake is expensive or hard to reverse — irreversible migrations, security-sensitive
  code, anything touching production or money.
- The acceptance criteria are fuzzy enough that a human must judge whether a slice is
  really done.
- The diff per step needs a human review to stay trustworthy.

The deciding question: *could a gate, with no human reading the diff, decide every item in
this backlog correctly?* A confident yes points to ralph. Any real doubt points to the
checkpointed loop, where a human approves each step. When unsure, default to the
checkpointed loop — the cost of an unnecessary checkpoint is minutes; the cost of an
autonomous loop loose on judgment-heavy work is a runaway nobody caught.

## Failure modes

Five ways the ralph loop fails, each with the guardrail that counters it:

- **Infinite loop.** The loop runs forever because no fixed target bounds it. Countermeasure:
  the done-condition bounds termination and the iteration cap N is the hard last-resort
  brake — the loop cannot run past N regardless of state.
- **Drift.** The stable prompt is edited mid-run, or the loop wanders off the backlog into
  unrelated work. Countermeasure: one unchanging prompt and a fixed backlog as the only
  scope; discovered work is recorded for after the run, never absorbed mid-loop.
- **Thrash.** The same item is edited across iteration after iteration without its status
  converging — the loop is busy but closes nothing. Countermeasure: the no-progress
  detector halts on K consecutive stalled rounds and surfaces the stuck item.
- **Runaway cost.** The loop makes slow, expensive progress that never quite stalls and
  never quite finishes, burning budget the whole way. Countermeasure: the cost/time budget,
  checked at the top of every iteration, halts the loop the moment spend is exhausted.
- **Silent gate-skipping.** The gate is skipped, narrowed, or reported green when it is not,
  so a broken item advances to done. Countermeasure: gate-green is required every iteration
  and the result is recorded verbatim; a red or skipped gate reverts the item to open and
  is never reported as done.

## Red flags

Signs a ralph loop is unsafe or mis-scoped:

- No iteration cap, no budget, or no stall limit set before the loop runs — a loop with no
  brakes.
- The done-condition is the iteration cap rather than a real backlog target.
- The prompt is rewritten between iterations, so the run is no longer reproducible.
- Loop position lives in the agent's context instead of a committed state file.
- A destructive or external-mutation command sits inline in the loop body.
- The gate is rerun many times against one item, or narrowed to make the item pass.
- The backlog contains items no gate could decide — judgment work smuggled into an
  autonomous loop.
- The loop absorbs newly discovered work into the current run instead of recording it for
  after termination.

## Worked example — two iterations

Task: migrate every call site of a deprecated `getUser(id)` helper to the new
`fetchUser({ id })` signature across a codebase. The backlog and bounds, written first:

Done-condition — backlog (each item gate-decidable), plus the gate green:

1. `src/profile.ts` calls `fetchUser` and the type-check passes.
2. `src/admin.ts` calls `fetchUser` and the type-check passes.
3. `src/report.ts` calls `fetchUser` and the type-check passes.
4. No reference to `getUser` remains anywhere in `src/` (grep returns nothing).

Guardrails: iteration cap N = 8; budget = 15 minutes; stall limit K = 2; gate =
`skill-gate --strict`. The state seeds with these four open items, `iteration: 0`,
`spend: 0`, `stall_count: 0`, and an empty `termination`.

### Iteration 1 — an item closes

**Open by re-reading state.** Read `handoff/state.json`: four items open, iteration 0 of 8,
spend under budget, stall count 0, gate green precondition holds. Another iteration is
permitted.

**Advance one item.** Take item 1. Rewrite the single `getUser(profileId)` call in
`src/profile.ts` to `fetchUser({ id: profileId })`. No destructive command runs; no external
state is touched.

**Gate and write back.** Run `skill-gate --strict`. The type-check passes and the gate exits
zero. Move item 1 to `backlog_done`, reset `stall_count` to 0, set `iteration: 1`, add the
spend. Three items remain open.

### Iteration 2 — a stalled round, detected

**Open by re-reading state.** Read the file: three items open, iteration 1 of 8, spend under
budget, stall count 0. Another iteration is permitted.

**Advance one item.** Take item 2. Rewrite the `getUser(adminId)` call in `src/admin.ts` to
`fetchUser({ id: adminId })`.

**Gate and write back.** Run `skill-gate --strict`. The gate fails: `src/admin.ts` passed a
second positional argument the old helper accepted and the new one rejects. Per the
gate-green guardrail, item 2 stays open, `stall_count` increments to 1, `iteration: 2`, spend
added. No item closed this round.

The next iteration re-reads state, sees `stall_count: 1` (below K = 2), and retries item 2 —
this time dropping the stray argument the gate flagged. That pass closes item 2 and resets the
stall count. Had a second consecutive iteration also closed nothing, `stall_count` would have
reached K = 2 and the no-progress detector would have halted the loop, writing
`termination: { reason: "stall", item: 2 }` for a human to inspect.

The loop continues — re-read, advance, gate, write back — until items 3 and 4 close with the
gate green. At that point the open set is empty and `skill-gate --strict` exits zero: the
done-condition holds, the loop writes `termination: { reason: "done" }`, and it stops. Every
iteration was bounded by the cap, the budget, and the stall detector; no destructive or
external operation ran; and the state file alone could have resumed the run after any crash —
which is the whole point of ralph.
