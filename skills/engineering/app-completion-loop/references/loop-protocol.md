# The loop protocol

The reference behind the loop steps. The loop drives an application to **done** in
checkpointed iterations: plan a slice, build it test-first, gate it, checkpoint for
approval, repeat. This page is the judgment the steps assume — how to write *done*, how
to cut a *slice*, what a *checkpoint* must report, how to survive a blocker, and how to
recognize a loop that has stopped converging. The deterministic gates
(`skill-gate --strict`) own the mechanical checks; the loop owns the discipline that
keeps each pass small, reviewable, and reversible.

The loop is checkpointed, not autonomous. A human approves at each phase boundary. The
single largest failure of an agent driving an app to done is the runaway: an unbounded
loop that edits for an hour and reports nothing reviewable. Every rule below exists to
make that runaway impossible.

## Done — the definition as acceptance criteria

The loop terminates against a fixed target. Write that target first, as a numbered list
of acceptance criteria, before planning a single slice. A loop with no definition of
done either stops early on a hunch or never stops at all.

A criterion is well-formed when it is:

- **Observable** — a gate, a test, or a scripted check decides it, not an opinion. "The
  login form validates the email" becomes "POST /login with a malformed email returns
  422 and the test asserting it passes."
- **Binary** — it passes or it fails; there is no eighty-percent. Split a fuzzy criterion
  into the sharp sub-criteria that compose it.
- **User-visible** — it names a behavior someone can exercise, not an internal step.
  "Refactor the auth module" is a task, not a criterion; "an expired token is rejected
  with 401" is a criterion.
- **Independent** — criteria do not overlap, so a single slice can close one without
  silently reopening another.

The list as a whole is the contract: when every criterion passes its gate, the app is
done, and no other change is in scope. Anything not on the list is out of scope until a
human adds it to the list at a checkpoint.

Red flags: a definition of done written as a feature list rather than as testable
conditions; a criterion no test could decide; "polish", "robust", or "production-ready"
standing in for a checkable condition; a criterion that hides three behaviors behind one
sentence.

## Slice — cutting the smallest unit that moves a criterion

A **slice** is the smallest change that moves one acceptance criterion measurably toward
passing. Slicing is the core skill of the loop, because slice size sets review cost,
blast radius, and how fast drift is caught.

Rules for cutting a slice:

- **Smallest first.** Cut the smallest slice that produces an observable change in a
  criterion's status. A slice that closes a whole criterion is good; a slice that closes
  a verifiable fraction of one is fine; a slice that touches everything and closes nothing
  is the anti-pattern.
- **Vertical over horizontal.** Prefer a thin vertical slice — one path from edge to
  store and back, demonstrable end to end — over a horizontal layer that builds
  infrastructure no criterion yet exercises. "One field saves and reloads" beats "the
  entire data layer for every field." A vertical slice is provable at its checkpoint; a
  horizontal layer is dead weight until something calls it.
- **One criterion per slice.** A slice advances one criterion. A slice that needs to
  touch several criteria is a sign the criteria are coupled or the slice is too big;
  split it.
- **Provable.** A slice must be expressible as a single failing test before it is built.
  A slice with no test you can write first is not yet understood well enough to build.
- **Reviewable in one sitting.** A slice whose diff a human cannot read in one review is
  too big. Split it at the planning checkpoint, before any code is written, never after.

Sequencing across slices: order them so each slice builds on a green, checkpointed
predecessor — a walking skeleton first (the thinnest end-to-end path), then slices that
thicken it. Defer a slice that depends on an unmade decision; surface the decision at a
checkpoint instead of guessing.

Red flags: a slice described by the files it touches rather than the behavior it
delivers; a slice that cannot be stated as one failing test; a "foundation" slice that
closes no criterion; a slice that grows mid-build as new work is discovered (stop, re-cut,
re-checkpoint).

## Checkpoint — the protocol for pausing and reporting

A **checkpoint** is a halt at a phase boundary where the agent reports and waits for a
human. The loop has two checkpoints per iteration: one after planning a slice (before
code), one after gating it (before the next slice). The checkpoint is the andon cord of
the loop — it stops the line so a human can see real output and steer.

### The planning checkpoint (after step 2, before building)

Report, then wait for approval:

- the slice goal as one line, naming the criterion it advances;
- the test that will prove the slice;
- the expected diff size and the files in scope;
- any decision the slice forces that a human should make first.

This checkpoint exists to catch a slice that is too big or aimed at the wrong criterion
*before* the cost of building it. It clears only on explicit approval.

### The result checkpoint (after step 5, before looping)

Report, then wait for approval:

- **Delivered** — what the slice changed, in one or two lines.
- **Criteria status** — which criteria now pass, which remain open, against the numbered
  definition of done.
- **Gate** — the `skill-gate --strict` result; a slice is never reported as done with a
  red or skipped gate.
- **Deviations** — anything built that differed from the approved plan, and why.
- **Blockers** — anything that stopped the slice short of its goal.
- **Next** — the proposed next slice, for the human to approve or redirect.

What needs human approval at a checkpoint: any scope change (adding, dropping, or
reshaping a criterion); any deviation from the approved slice; any architectural decision
the slice forced; the choice of the next slice. What does not need approval: the
mechanical work inside an approved slice — writing the test, writing the code, fixing the
gate. The human approves the *what* and the *boundaries*; the agent owns the *how* inside
them.

Report at altitude. A checkpoint is a decision surface, not a diff dump: state criteria
status and deviations, link to the diff, and do not paste hundreds of lines a human did
not ask to read.

Red flags: a checkpoint that reports activity ("edited five files") instead of criteria
status; looping past a checkpoint without waiting for approval; a result checkpoint that
omits the gate result or buries a deviation.

## Blockers and deviations mid-loop

A slice meets reality and the plan bends. Handle the bend explicitly; never paper over it.

- **Blocker** — something prevents the slice from reaching its goal: a missing
  dependency, an undecided requirement, a failing external system, a criterion that turns
  out to be untestable as written. Stop the slice, report the blocker at the result
  checkpoint with the options you see, and let the human choose. Do not silently swap to a
  different slice; do not push a half-slice through the gate.
- **Deviation** — the slice can be finished but only by departing from the approved plan
  (a different seam, an extra file, a changed interface). Small deviations inside the
  slice's intent: make the change and disclose it under "Deviations" at the checkpoint.
  Deviations that change scope or cross into another criterion: stop and re-checkpoint the
  plan before continuing.
- **Discovered work** — the slice reveals adjacent work that needs doing (a bug, a
  missing criterion). Record it as a candidate criterion and raise it at the checkpoint;
  do not absorb it into the current slice. Absorbing discovered work is how a one-test
  slice becomes an unreviewable sprawl.

The rule under all three: the gate is never skipped and the checkpoint is never bypassed
to "save time." A blocker reported honestly costs one checkpoint; a blocker hidden costs
the trust that lets the loop run at all.

## Drift and thrash — detecting a loop that has stopped converging

The loop assumes monotone progress: each iteration leaves strictly fewer criteria open.
When that assumption breaks, the loop must stop and surface it, not grind on. Watch for
these signals:

- **No-progress iteration** — a full iteration closes no criterion and opens none toward
  closing. One is a warning; two in a row is a stop. Report and ask for redirection.
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

On any stop signal, halt the loop at a checkpoint, report the signal and the evidence, and
wait for a human to redirect. A loop that detects its own drift and stops is working as
designed; a loop that drifts silently is the thing this skill prevents.

## Failure modes

Four ways the loop fails, each with its countermeasure:

- **Scope creep** — work not in the definition of done leaks in, slice by slice
  ("while I was here"). Countermeasure: the definition of done is the only scope; new work
  becomes a candidate criterion raised at a checkpoint, never code smuggled into a slice.
- **The non-converging loop** — the loop runs forever, closing nothing, because no fixed
  target bounds it or because slices keep missing. Countermeasure: a numbered definition
  of done bounds the loop, and the no-progress and thrash signals stop it when iterations
  stop reducing the open set.
- **The slice too big to review** — a slice's diff is too large for a human to judge, so
  the checkpoint becomes a rubber stamp and review collapses. Countermeasure: cut the
  smallest vertical slice, and split at the planning checkpoint before building, not after.
- **Silent gate-skipping** — the gate is skipped, narrowed, or reported green when it is
  not, to keep the loop moving. Countermeasure: `skill-gate --strict` runs every slice and
  its result is reported verbatim at the result checkpoint; a red or skipped gate is never
  reported as done.

## Worked example — two iterations

Application: a small URL-shortener service. Definition of done, written first:

1. POST /shorten with a valid URL returns 201 and a short code.
2. GET /{code} for a known code returns 302 to the original URL.
3. POST /shorten with a malformed URL returns 422.
4. GET /{code} for an unknown code returns 404.

### Iteration 1 — the walking skeleton

**Plan the slice.** Smallest vertical slice that moves criterion 1: accept a valid URL,
store it, return 201 with a code. Not the validation (criterion 3), not the redirect
(criterion 2) — one path, edge to store.

**Planning checkpoint.** "Slice: POST /shorten stores a valid URL and returns 201 + code
(criterion 1). Test: posting a valid URL yields 201 and a non-empty code. Diff: one route
handler, one store function, one test. No decision blocked." A human approves.

**Build test-first.** Per [tdd](../../tdd/SKILL.md): write the failing test (POST a valid URL
expects 201 and a code) — it fails because no route exists. Write the minimum handler and
in-memory store to return 201 with a generated code. The test goes green.

**Gate.** Run `skill-gate --strict`. Lint flags an unused import; correct it and rerun.
The gate exits zero.

**Result checkpoint.**
- Delivered: POST /shorten stores a valid URL and returns 201 with a short code.
- Criteria: 1 passes. 2, 3, 4 open.
- Gate: `skill-gate --strict` green.
- Deviations: none.
- Blockers: none.
- Next: criterion 2, GET /{code} redirects a known code.

A human approves continuing.

### Iteration 2 — a blocker, handled

**Plan the slice.** Smallest slice for criterion 2: GET /{code} for a code that exists
returns 302 to the stored URL. Reuses iteration 1's store.

**Planning checkpoint.** "Slice: GET /{code} redirects a known code with 302 (criterion 2).
Test: shorten a URL, then GET its code, expect 302 with the original URL in Location.
Diff: one route handler, one test." A human approves.

**Build test-first.** Write the failing test (shorten, then GET the code, expect 302) — it
fails, no GET route. While building, a blocker surfaces: the store from iteration 1
returns the record but the slice needs a lookup-by-code that does not exist, and adding it
touches the store's shape — a deviation from the "one route handler" plan.

**Handle the deviation.** The deviation stays inside criterion 2's intent (it is the
lookup the redirect needs), so make the change and note it for the checkpoint rather than
silently expanding scope. Finish the handler; the test goes green.

**Gate.** Run `skill-gate --strict`. The gate exits zero.

**Result checkpoint.**
- Delivered: GET /{code} redirects a known code with 302 to the original URL.
- Criteria: 1, 2 pass. 3, 4 open.
- Gate: `skill-gate --strict` green.
- Deviations: added a lookup-by-code to the store; in scope for criterion 2, disclosed
  here.
- Blockers: none outstanding (the lookup blocker was resolved by the disclosed deviation).
- Next: criterion 3, malformed URL returns 422 — a slice with no new storage, pure
  validation at the edge.

A human approves continuing. The loop repeats from planning the next slice until criteria
3 and 4 pass their gates, at which point every criterion in the definition of done is
green and the final checkpoint closes the loop.
