# TDD practice

How to run the red-green-refactor loop so each step stays small, each test earns its
keep, and the suite stays trustworthy. The test gate (`skill-gate --category test`)
runs whatever you write; this page decides *what* to write at each phase and *why*.

## The loop

Three phases, run in order, one behavior at a time:

- **red** — write one failing test for the next behavior, and watch it fail.
- **green** — write the least code that turns the test green, and nothing more.
- **refactor** — improve the design while the suite stays green.

The order is the discipline. A test written after the code tends to assert what the
code already does, so it cannot expose the bug the code already has. The failure you
observe in red is the proof that the test is wired to real behavior, not to a typo in
the test harness.

## What makes a good first failing test

The first test sets the target for the whole loop, so it must be narrow and honest:

- **One behavior.** A single observable fact: this input yields that output, or this
  call produces that effect. A test that asserts three behaviors fails for three
  reasons, and the red gives no clear next step.
- **Fails for the stated reason.** Before any implementation exists, run the test and
  read the failure message. The message must name the missing behavior — a wrong
  return value, a missing function — not a syntax error or an import that does not
  resolve. A test that errors out for the wrong reason is a false red.
- **Asserts behavior, not implementation.** Pin the output and the observable effect,
  never the internal call sequence. A test bound to internals goes red on every
  refactor and catches no real defect (see the failure modes below).
- **Names the contract.** The test name states the rule under test, so a future reader
  learns the spec from the test list alone.

A test that passes the moment you write it tests nothing. Delete it, or fix it until
the absence of code makes it red.

## The size of a step

A step is small enough that you can hold the whole change in your head and return to
green within a few minutes. Smaller steps mean each red has exactly one cause, so a
surprise failure points at the line you just touched.

- **Too big** — the test demands a whole feature, the green phase sprawls across many
  files, and a failure mid-way leaves you debugging code that has never been green.
- **Right-sized** — the test demands the next single behavior; the green is a handful
  of lines; the bar returns to green before you write the next test.

When a behavior feels too large for one step, split it: pick the simplest sub-case
(the empty input, the single element, the boundary), drive that to green, then add the
next case as its own red. The loop tightens; the design grows in observed increments.

## The three phases — what each allows

**Red — write the test.**

- Allowed: write or extend exactly one test; run the gate; confirm it fails for the
  named reason.
- Not allowed: writing production code, or stubbing a return only to dodge the failure.
- Done when: the gate reports one new failing test whose message names the missing
  behavior.

**Green — make it pass.**

- Allowed: the least production code that turns the bar green. A blunt, even ugly,
  implementation is fine here — a hard-coded return that satisfies the one case is a
  legitimate first green.
- Not allowed: code for a behavior no current test demands (speculative generality);
  unrelated cleanup; a second feature.
- Done when: the full suite is green, with no test commented out or skipped.

**Refactor — improve the design.**

- Allowed: rename, extract, inline, de-duplicate, and reshape — behavior held constant.
  The green suite is the safety net that makes the change safe.
- Not allowed: new behavior (that is a fresh red), and refactoring while the suite is
  red.
- Done when: the design reads better, the suite is still green, and no observable
  behavior changed.

Refactoring on red is the cardinal sin of the loop: a red suite cannot tell a
behavior-preserving change from a behavior-breaking one, so the net vanishes. Return
to green first, then refactor.

## Common failure modes

- **Testing implementation, not behavior.** The test asserts that a private helper was
  called, or pins a mock's call order. The test then breaks on every refactor and
  catches no defect. Fix: assert the output and the observable effect, never the
  internals.
- **Steps too big.** The red demands a whole feature; the green never reaches the bar;
  debugging happens in code that was never green. Fix: shrink to the next single case.
- **Refactoring on red.** Reshaping the design while a test is failing, so the safety
  net is gone. Fix: get to green, commit the green, then refactor.
- **Writing the assertion after seeing the output.** Running the code first, then
  pasting the printed value into the assertion. The test now ratifies whatever the code
  does, bug included. Fix: write the expected value from the spec, before running.
- **The false red.** The test fails on an import error or a typo, not on the missing
  behavior, so red proves nothing about the wiring. Fix: read the failure message and
  confirm it names the behavior under test.
- **Skipping refactor.** Stopping at green every time, so duplication and mess
  accumulate until the next change is expensive. Fix: treat refactor as part of the
  loop, not an optional extra.

## When TDD fits, and when it does not

TDD pays off whenever the behavior is specifiable up front and regression matters:
business logic, parsers, algorithms, bug fixes (the failing test reproduces the bug
first), and any API with a contract. A bug fix without a reproducing test is a fix you
cannot prove and a regression waiting to return.

TDD fits poorly, or not at all, in these cases:

- **Spikes and exploration.** When the goal is to learn whether an approach is viable,
  the spec does not exist yet, so write throwaway code to answer the question — then
  delete it and start the real work test-first.
- **Throwaway prototypes.** Code slated for the bin, never to ship, earns no test.
- **Pure presentation tweaks.** A spacing or color change has no behavior an assertion
  can pin; a visual or snapshot check serves better than a unit test.
- **Generated or trivial code.** A pass-through accessor with no logic has nothing to
  drive.

The boundary is behavior: where there is a rule that can pass or fail, drive it
test-first. Where the only question is "does it look right", reach for a different tool.

## A worked example: red → green → refactor

Behavior wanted: `slugify(title)` lowercases the title and joins words with hyphens.

**Red — the first failing test.**

```python
def test_slugify_joins_words_with_hyphens():
    assert slugify("Hello World") == "hello-world"
```

Run `skill-gate --category test`. The failure names the missing function
(`slugify` is not defined) — a true red. The test pins one behavior, drawn from the
spec, written before the value was ever printed.

**Green — the least code that passes.**

```python
def slugify(title):
    return title.lower().replace(" ", "-")
```

Run the gate again; the suite is green. The implementation is blunt and handles only
the one case the test demands — correct for this phase. No support for empty input or
punctuation is added yet, because no test asks for it.

**Refactor — improve with the net up.**

The two-step `lower().replace(...)` reads fine, so the production code needs no change.
The test name already states the contract. With the suite green, the loop closes.

**The next red — drive the next case.**

```python
def test_slugify_collapses_repeated_spaces():
    assert slugify("Hello   World") == "hello-world"
```

Run the gate; this new test goes red, because the blunt `replace(" ", "-")` yields
`hello---world`. That red is the signal to return to green with a real implementation:

```python
import re

def slugify(title):
    return re.sub(r"\s+", "-", title.lower().strip())
```

Run the gate once more; both tests pass. The design grew one observed case at a time,
and no production code exists that a red did not first demand.
