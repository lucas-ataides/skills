# The loop protocol

The reference behind the loop steps. The loop drives a codebase to **done** in bounded
iterations: define done as criteria, plan a slice, build it test-first, gate it, record
state, repeat. This page is the judgment the steps assume — how to choose a mode, how to
write *done*, how to cut a *slice*, what a *checkpoint* reports, what *guardrails* bound an
autonomous run, how to reset the working tree on a red gate, how to recognize a loop that
has stopped converging, and how the loop fails. The deterministic gate
(`skill-gate --strict`) owns the mechanical checks — formatting, lint, types, SAST, SCA,
secrets, tests — and the loop owns the discipline that keeps each pass small, reviewable,
reversible, and bounded.

## The two modes — checkpointed and autonomous

The loop runs in one of two modes, chosen once before the first iteration. Both share the
same skeleton: a definition of done as acceptance criteria, a persistent resumable state
file, slice planning, build test-first, a gate every iteration, a working-tree reset on a
red gate, and the stop condition *backlog empty AND gate green*. The modes differ on a
single axis — whether a human rules between iterations.

**Checkpointed** keeps a human at every phase boundary. The agent pauses after planning a
slice (before code) and after gating it (before the next slice), reports at altitude, and
waits for approval. The checkpoint is the andon cord: a human sees real output and steers,
so progress stays reviewable and reversible. Checkpointed is the default and the safe
mode.

**Autonomous** (the "ralph" technique) removes the human between iterations and replaces
the andon cord with hard, mechanical guardrails. One stable prompt re-reads the state
file, advances one item, gates it, writes state back, and repeats — unattended — until the
done-condition is met or a guardrail halts the run. Autonomous buys throughput on a large,
well-specified backlog and pays for it in risk, so the guardrail set carries the whole
safety burden.

Choose by the backlog, not by taste. The deciding question: *could a gate, with no human
reading the diff, decide every item in this backlog correctly?*

**Autonomous fits** a large, mechanical, well-specified backlog:

- The work is repetitive and the pattern is known — migrate every call site to a new API,
  fix one lint rule across hundreds of files, port a test suite, regenerate fixtures.
- Each item is gate-decidable, so correctness needs no human judgment per step.
- The backlog is large enough that stopping for approval each step wastes the autonomy.
- A mistake is cheap to catch and revert — the gate is strong and the blast radius is
  contained to the working tree.

**Checkpointed is safer** for high-stakes, judgment-heavy work:

- A step forces a design decision a gate cannot make — an architecture choice, an API
  contract, a product trade-off.
- A mistake is expensive or hard to reverse — irreversible migrations, security-sensitive
  code, anything touching production or money.
- The acceptance criteria are fuzzy enough that a human must judge whether a slice is
  really done.
- The diff per step needs a human review to stay trustworthy.

A confident yes to the deciding question points to autonomous; any real doubt points to
checkpointed. The default is checkpointed — the cost of an unnecessary checkpoint is
minutes; the cost of an autonomous loop loose on judgment-heavy work is a runaway nobody
caught.

## Done — the definition as acceptance criteria

The loop terminates against a fixed target written before the first iteration. Write that
target as a numbered backlog of acceptance criteria. A loop with no definition of done
either stops early on a hunch or never stops at all. Both halves of the stop condition are
required: an empty open set with a red gate is not done, and a green gate with open items
left is not done — only the conjunction stops the loop with success.

A criterion is well-formed when it is:

- **Observable** — a gate, a test, or a scripted check decides it, not an opinion. "The
  login form validates the email" becomes "POST /login with a malformed email returns 422
  and the test asserting it passes."
- **Binary** — it passes or it fails; there is no eighty-percent. Split a fuzzy criterion
  into the sharp sub-criteria that compose it.
- **Gate-decidable** — the gate, or a check the gate runs, can rule on the item. A
  criterion no gate can decide has no place in an autonomous loop, because nothing
  unattended can close it; in checkpointed mode such a criterion needs a human ruling at
  the checkpoint.
- **User-visible** — it names a behavior someone can exercise, not an internal step.
  "Refactor the auth module" is a task, not a criterion; "an expired token is rejected
  with 401" is a criterion.
- **Independent** — criteria do not overlap, so a single slice closes one without silently
  reopening another, and the open set shrinks monotonically.

The list as a whole is the contract: when every criterion passes its gate, the codebase is
done, and no other change is in scope. The loop never adds work to the backlog on its own
— discovered work is recorded and surfaced (at a checkpoint in checkpointed mode, at
termination in autonomous mode), never absorbed mid-run.

Red flags: a definition of done written as a feature list rather than as testable
conditions; a criterion no test could decide; "polish", "robust", or "production-ready"
standing in for a checkable condition; a criterion that hides three behaviors behind one
sentence; a "done-condition" that is just the iteration cap with no real target.

## The state file — the resumable contract

The loop carries no memory across iterations beyond a durable, committed state file. The
file ties to [handoff](../../../productivity/handoff/SKILL.md): the loop writes a handoff
to itself every iteration, so the next iteration — or a fresh agent after a crash — resumes
cold with zero context loss. Read it first each loop, write it back each loop.

A `handoff/state.json` holds, at minimum:

- **`mode`** — checkpointed or autonomous, fixed for the run.
- **`backlog_open`** — the remaining criteria, top-first, each binary and gate-decidable.
- **`backlog_done`** — the closed criteria, so the loop neither redoes them nor distrusts
  them.
- **`iteration`** — the current count, checked against the cap N in autonomous mode.
- **`spend`** — accumulated cost and elapsed time, checked against the budget in autonomous
  mode.
- **`stall_count`** — consecutive iterations that closed nothing, checked against K.
- **`gate`** — the named gate command and its last recorded result.
- **`termination`** — empty while running; on halt, the reason (done, cap, budget, stall,
  guardrail, redirect) and the final counts.

The discipline is strict: every iteration opens by reading this file and closes by writing
it back atomically, so a reader never sees a half-written state and a crash mid-iteration
loses at most one item's progress. Loop position lives in the file, never only in the
agent's head — that is what makes the loop resumable.

Red flags: loop counters tracked in context instead of the file; a state file written
non-atomically, so a crash corrupts it; a file that records done items but not the stall
count or spend, blinding the guardrails; reconstructing position from chat scrollback after
a reset.

## Slice — cutting the smallest unit that moves a criterion

A **slice** is the smallest change that moves one acceptance criterion measurably toward
passing. Slicing is the core skill of the loop, because slice size sets review cost, blast
radius, and how fast drift is caught.

Rules for cutting a slice:

- **Smallest first.** Cut the smallest slice that produces an observable change in a
  criterion's status. A slice that closes a whole criterion is good; a slice that closes a
  verifiable fraction of one is fine; a slice that touches everything and closes nothing is
  the anti-pattern.
- **Vertical over horizontal.** Prefer a thin vertical slice — one path from edge to store
  and back, demonstrable end to end — over a horizontal layer that builds infrastructure no
  criterion yet exercises. "One field saves and reloads" beats "the entire data layer for
  every field." A vertical slice is provable at its checkpoint; a horizontal layer is dead
  weight until something calls it.
- **One criterion per slice.** A slice advances one criterion. A slice that needs to touch
  several criteria signals coupled criteria or an oversized slice; split it.
- **Provable.** A slice must be expressible as a single failing test before it is built. A
  slice with no test you can write first is not yet understood well enough to build.
- **Reviewable in one sitting.** A slice whose diff a human cannot read in one review is too
  big. Split it at the planning checkpoint, before any code is written, never after.

Sequencing across slices: order them so each slice builds on a green predecessor — a
walking skeleton first (the thinnest end-to-end path), then slices that thicken it. Defer a
slice that depends on an unmade decision; surface the decision rather than guess.

When breadth within one slice dominates depth — several independent units that each touch a
disjoint file set — fan the slice across owned-file workers via
[the fan-out pattern](../SKILL.md), then gate the
merged tree as one. The loop owns the slice boundary; the orchestrator owns the fan-out
inside it.

Red flags: a slice described by the files it touches rather than the behavior it delivers;
a slice that cannot be stated as one failing test; a "foundation" slice that closes no
criterion; a slice that grows mid-build as new work is discovered (stop, re-cut, re-plan).

## Checkpoint — the protocol for pausing and reporting (checkpointed mode)

A **checkpoint** is a halt at a phase boundary where the agent reports and waits for a
human. Checkpointed mode has two checkpoints per iteration: one after planning a slice
(before code), one after gating it (before the next slice). The checkpoint is the andon
cord — it stops the line so a human sees real output and steers.

### The planning checkpoint (after the slice is cut, before building)

Report, then wait for approval:

- the slice goal as one line, naming the criterion it advances;
- the test that will prove the slice;
- the expected diff size and the files in scope;
- any decision the slice forces that a human should make first.

This checkpoint exists to catch a slice that is too big or aimed at the wrong criterion
*before* the cost of building it. The checkpoint clears only on explicit approval.

### The result checkpoint (after the gate, before looping)

Report, then wait for approval:

- **Delivered** — what the slice changed, in one or two lines.
- **Criteria status** — which criteria now pass, which remain open, against the numbered
  definition of done.
- **Gate** — the `skill-gate --strict` result; a slice is never reported as done with a red
  or skipped gate.
- **Deviations** — anything built that differed from the approved plan, and why.
- **Blockers** — anything that stopped the slice short of its goal.
- **Next** — the proposed next slice, for the human to approve or redirect.

What needs human approval at a checkpoint: any scope change (adding, dropping, or reshaping
a criterion); any deviation from the approved slice; any architectural decision the slice
forced; the choice of the next slice. What does not need approval: the mechanical work
inside an approved slice — writing the test, writing the code, fixing the gate. The human
approves the *what* and the *boundaries*; the agent owns the *how* inside them.

Report at altitude. A checkpoint is a decision surface, not a diff dump: state criteria
status and deviations, link to the diff, and skip the hundreds of lines a human did not ask
to read. Apply the same depth bar a tech lead applies in
[the review lenses](../../code-review/references/review-lenses.md) — does the slice deliver
the criterion, in the right place, before line-level detail.

Red flags: a checkpoint that reports activity ("edited five files") instead of criteria
status; looping past a checkpoint without waiting for approval; a result checkpoint that
omits the gate result or buries a deviation.

## The guardrails — what keeps an autonomous loop safe

Checkpointed mode is kept safe by a human at every boundary. Autonomous mode has no such
human, so safety is mechanical. Seven guardrails bound the run, and every one is set or
enforced before the first iteration:

- **Bounded iteration cap (N).** A hard ceiling on iterations. The loop halts at N
  regardless of backlog state. The cap is the last-resort brake against an infinite loop —
  even with every other detector failing, the loop cannot run past N. Set N from the
  backlog size with headroom for retries, not to an open-ended large number.
- **Cost/time budget.** A ceiling on spend — wall-clock minutes, token cost, or both. The
  loop checks accumulated spend at the top of each iteration and halts the moment the
  budget is exhausted. The budget bounds the blast radius of a loop that makes slow,
  expensive progress without ever quite stalling.
- **No-progress detector (K stalled rounds).** A counter of consecutive iterations that
  closed no backlog item. One stalled round is noise; K in a row is a halt. The detector
  catches the loop that is busy but not converging — editing, gating, failing, and retrying
  the same item forever. Reset the counter to zero on any iteration that closes an item;
  halt when it reaches K.
- **Gate-green required each iteration.** No iteration reports an item done with a red or
  skipped gate. The gate runs every pass and its result is recorded verbatim. A red gate
  reverts the item to open; it never advances behind a narrowed or skipped check. Eroding
  the gate to make an item pass is the silent-gate-skipping failure mode, and the practice
  is banned.
- **Reset the working tree on a red gate.** Reverting an item to open is a status change;
  the failed attempt's edits still sit dirty in the working tree. So a red gate also
  restores that item's changed files to their pre-iteration state from version control
  before the retry — covered in its own section below.
- **No destructive operations.** The loop runs no irreversible command unattended — no
  history rewrite, no recursive delete, no force-push, no schema drop. Destruction routes
  through a guarded helper or is forbidden outright, because no human is watching to catch a
  mistaken delete. Determinism doctrine: the dangerous path is structurally impossible, not
  merely discouraged.
- **No external mutation without approval.** The loop does not mutate state outside the
  working tree — no deploy, no production write, no third-party API call that changes remote
  state, no published release — without recorded prior approval. The loop's reach ends at
  the repository unless a human has signed off in advance on a specific external action.

A loop that trips a guardrail halts and writes its termination reason to the state file. A
guardrail halt is the loop working as designed; a loop that runs past its guardrails is the
exact failure this skill exists to prevent.

## Resetting the working tree on a red gate

A red gate reverts the failed item to open, but the failed attempt's edits remain in the
working tree. Both modes restore that item's changed files to their pre-iteration state
from version control before the next attempt, exactly as the
[the orchestration reference](orchestration.md) re-dispatch
loop resets a failed unit's owned files from VCS. Without this reset the loop accumulates
dirty, half-applied changes across retries until the gate can no longer tell which edit is
under test.

The mechanics: the loop runs on its own unshared branch, and on a red gate it restores only
that item's scope — `git restore <files>` for the touched paths, or a scoped reset of the
loop's branch to the pre-iteration commit — so the next attempt starts from a clean tree
rather than compounding a half-done edit. The branch-level reset spelled out:

```
git reset --hard <pre-iteration-commit>   # <!-- skill-lint: allow SK040 -->
```

The reset restores only the loop's own unshared branch to a commit the loop itself made one
iteration earlier, so no shared history and no un-committed human work is at risk.

## Blockers and deviations mid-loop (checkpointed mode)

A slice meets reality and the plan bends. Handle the bend explicitly; never paper over it.

- **Blocker** — something prevents the slice from reaching its goal: a missing dependency,
  an undecided requirement, a failing external system, a criterion untestable as written.
  Stop the slice, report the blocker at the result checkpoint with the options you see, and
  let the human choose. Do not silently swap to a different slice; do not push a half-slice
  through the gate.
- **Deviation** — the slice can be finished but only by departing from the approved plan (a
  different seam, an extra file, a changed interface). A small deviation inside the slice's
  intent: make the change and disclose it under "Deviations" at the checkpoint. A deviation
  that changes scope or crosses into another criterion: stop and re-plan before continuing.
- **Discovered work** — the slice reveals adjacent work that needs doing (a bug, a missing
  criterion). Record it as a candidate criterion and raise it at the checkpoint; do not
  absorb it into the current slice. Absorbing discovered work is how a one-test slice
  becomes an unreviewable sprawl.

The rule under all three: the gate is never skipped and the checkpoint is never bypassed to
"save time." A blocker reported honestly costs one checkpoint; a blocker hidden costs the
trust that lets the loop run at all. In autonomous mode the equivalent rule holds without a
checkpoint — a blocked item stays open, the stall detector counts the failure, and
discovered work is recorded for termination rather than absorbed mid-run.

## Drift and thrash — detecting a loop that has stopped converging

The loop assumes monotone progress: each iteration leaves strictly fewer criteria open.
When that assumption breaks, the loop stops and surfaces the break rather than grinding on.
Watch for these signals:

- **No-progress iteration** — a full iteration closes no criterion. One is a warning; two
  in a row is a stop. In autonomous mode the stall detector (K) enforces this; in
  checkpointed mode the agent reports and asks for redirection.
- **Reopen / regression** — a slice turns a previously passing criterion red. The gate
  catches the test regression; the loop's job is to halt rather than patch forward over a
  regression it caused.
- **Thrash** — the same file or the same criterion is edited across three or more
  iterations without its status converging. Thrash means the slice keeps missing; stop and
  re-cut the slice or re-examine the criterion.
- **Slice inflation** — successive slices grow larger and diffs grow harder to review.
  Inflation precedes the runaway; cut back to a thinner vertical slice.
- **Gate erosion** — a gate starts being rerun more than a couple of times per slice, or
  the temptation appears to narrow what the gate checks. Eroding the gate to make a slice
  pass is silent gate-skipping; the slice is wrong, not the gate.
- **Prompt drift** (autonomous mode) — the stable prompt is edited mid-run, so the run is
  no longer one reproducible loop. The prompt stays fixed for the whole run; the *state*
  changes, the prompt does not.

On any stop signal the loop halts — at a checkpoint in checkpointed mode, against a
guardrail in autonomous mode — reports the signal and the evidence, and waits for a human to
redirect. A loop that detects its own drift and stops is working as designed; a loop that
drifts silently is the thing this skill prevents.

## Failure modes

Six ways the loop fails, each with its countermeasure:

- **The non-converging loop** — the loop runs forever, closing nothing, because no fixed
  target bounds it or because slices keep missing. Countermeasure: a numbered definition of
  done bounds the loop, the no-progress and thrash signals stop it when iterations stop
  reducing the open set, and in autonomous mode the iteration cap N is the hard last-resort
  brake the loop cannot run past.
- **Scope creep** — work not in the definition of done leaks in, slice by slice ("while I
  was here"). Countermeasure: the definition of done is the only scope; new work becomes a
  candidate criterion raised at a checkpoint (checkpointed) or recorded for termination
  (autonomous), never code smuggled into a slice.
- **The slice too big to review** — a slice's diff is too large for a human to judge, so the
  checkpoint becomes a rubber stamp and review collapses. Countermeasure: cut the smallest
  vertical slice, and split at the planning checkpoint before building, not after.
- **Silent gate-skipping** — the gate is skipped, narrowed, or reported green when it is
  not, to keep the loop moving. Countermeasure: `skill-gate --strict` runs every slice and
  its result is reported verbatim; a red or skipped gate is never reported as done and
  reverts the item to open.
- **Runaway cost** (autonomous mode) — the loop makes slow, expensive progress that never
  quite stalls and never quite finishes, burning budget the whole way. Countermeasure: the
  cost/time budget, checked at the top of every iteration, halts the loop the moment spend
  is exhausted.
- **Dirty-tree compounding** (autonomous mode) — a red gate reverts the item to open but
  leaves the failed edit in the tree, so the next attempt stacks on a half-done change.
  Countermeasure: the working-tree reset restores the failed item's files from VCS before
  the retry, so every attempt starts clean.

## Worked example — one checkpointed iteration, one autonomous iteration

### Checkpointed — a URL-shortener slice with a handled deviation

Application: a small URL-shortener service, run in checkpointed mode. Definition of done,
written first:

1. POST /shorten with a valid URL returns 201 and a short code.
2. GET /{code} for a known code returns 302 to the original URL.
3. POST /shorten with a malformed URL returns 422.
4. GET /{code} for an unknown code returns 404.

Iteration on criterion 2 (criterion 1 closed in a prior pass, an in-memory store already
returns 201 with a code).

**Open and plan the slice.** Read `handoff/state.json`: criteria 2, 3, 4 open, mode
checkpointed. Smallest slice for criterion 2: GET /{code} for a code that exists returns
302 to the stored URL, reusing the existing store.

**Planning checkpoint.** "Slice: GET /{code} redirects a known code with 302 (criterion 2).
Test: shorten a URL, then GET its code, expect 302 with the original URL in Location. Diff:
one route handler, one test." A human approves.

**Build test-first.** Per [tdd](../../tdd/SKILL.md): write the failing test (shorten, then
GET the code, expect 302) — the test fails, no GET route. While building, a blocker
surfaces: the store returns the record but the slice needs a lookup-by-code that does not
exist, and adding it touches the store's shape — a deviation from the "one route handler"
plan. The deviation stays inside criterion 2's intent (it is the lookup the redirect
needs), so make the change and note it for the checkpoint rather than silently expanding
scope. Finish the handler; the test goes green.

**Gate.** Run `skill-gate --strict`. The gate exits zero.

**Record and result checkpoint.** Write state back, then report:
- Delivered: GET /{code} redirects a known code with 302 to the original URL.
- Criteria: 1, 2 pass. 3, 4 open.
- Gate: `skill-gate --strict` green.
- Deviations: added a lookup-by-code to the store; in scope for criterion 2, disclosed here.
- Blockers: none outstanding (the lookup blocker was resolved by the disclosed deviation).
- Next: criterion 3, malformed URL returns 422 — a slice with no new storage, pure
  validation at the edge.

A human approves continuing. The loop repeats from planning until criteria 3 and 4 pass
their gates, at which point the backlog is empty, the gate is green, and the final
checkpoint closes the loop.

### Autonomous — a call-site migration with a stalled round and a tree reset

Task: migrate every call site of a deprecated `getUser(id)` helper to the new
`fetchUser({ id })` signature, run in autonomous mode. Done-condition — backlog (each item
gate-decidable), plus the gate green:

1. `src/profile.ts` calls `fetchUser` and the type-check passes.
2. `src/admin.ts` calls `fetchUser` and the type-check passes.
3. `src/report.ts` calls `fetchUser` and the type-check passes.
4. No reference to `getUser` remains anywhere in `src/` (grep returns nothing).

Guardrails: iteration cap N = 8; budget = 15 minutes; stall limit K = 2; gate =
`skill-gate --strict`. State seeds with these four open items, `iteration: 0`, `spend: 0`,
`stall_count: 0`, mode autonomous, and an empty `termination`.

Iteration on item 2 (item 1 closed in iteration 1, which rewrote `src/profile.ts` and exited
the gate clean).

**Open by re-reading state.** Read `handoff/state.json`: three items open, iteration 1 of 8,
spend under budget, stall count 0, gate-green precondition holds. The cap, budget, and stall
limit all permit another iteration.

**Advance one item.** Take item 2. Rewrite the `getUser(adminId)` call in `src/admin.ts` to
`fetchUser({ id: adminId })`. No destructive command runs; no external state is touched.

**Gate.** Run `skill-gate --strict`. The gate fails: `src/admin.ts` passed a second
positional argument the old helper accepted and the new one rejects.

**Reset and record.** Per the gate-green guardrail, item 2 stays open and `stall_count`
increments to 1. Per the working-tree-reset guardrail, the loop restores the file the failed
attempt touched — `git restore src/admin.ts` on the loop's own branch — so the dirty edit
rolls back and the tree is clean again. Write `iteration: 2` and the spend. No item closed
this round.

The next iteration re-reads state, sees `stall_count: 1` (below K = 2), and retries item 2
from that clean tree — this time writing `fetchUser({ id: adminId })` without the stray
argument the gate flagged, rather than patching on top of a reverted-but-still-dirty first
attempt. That pass closes item 2 and resets the stall count to zero. A second consecutive
empty iteration instead would have driven `stall_count` to K = 2, halting the loop with
`termination: { reason: "stall", item: 2 }` for a human to inspect.

The loop continues — re-read, advance, gate, reset-on-red, record — until items 3 and 4 close
with the gate green. At that point the open set is empty and `skill-gate --strict` exits
zero: the done-condition holds, the loop writes `termination: { reason: "done" }`, and it
stops. Every iteration was bounded by the cap, the budget, and the stall detector; every red
gate reset the failed item's files so no half-done edit survived into the retry; no
destructive or external operation ran; and the state file plus a clean tree alone could have
resumed the run after any crash.
