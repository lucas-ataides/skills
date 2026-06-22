# Test strategy

How to turn acceptance criteria into tests that catch real defects without becoming a
slow, brittle suite. The test gate (`skill-gate --category test`) runs whatever you
write here; this page decides *what* to write and *where*.

## The pyramid (by cost and confidence)

Place each behavior at the lowest level that can prove it. Lower is faster and more
stable; higher is closer to the user but slower and flakier.

- **Unit** — pure logic, branches, edge cases. The bulk of the suite. Fast, deterministic,
  no I/O. If logic has many cases, it belongs here, not in an end-to-end test.
- **Integration** — the seams: a real database, a real HTTP boundary, a real file. Proves
  the wiring and the contract between units. Fewer than unit, more than end-to-end.
- **End-to-end** — the critical user path, through the running system. The fewest tests:
  expensive and the first to flake. Reserve for the journeys that must never break.

Anti-pattern — the ice-cream cone: most tests at the end-to-end level. Slow, flaky,
hard to localize a failure. Push behavior down.

## What makes a test worth keeping

- **It can fail.** Comment out the code under test; the test must go red. A test that
  passes regardless tests nothing.
- **It asserts behavior, not implementation.** Assert the output and the observable
  effect, not the internal call sequence. Implementation tests break on every refactor
  and catch no real defect.
- **It covers the failure path.** The happy path is the easy half. Test the rejection,
  the timeout, the empty, the boundary, the concurrent case.
- **It is deterministic.** No reliance on wall-clock, network flakiness, or test order.
  Inject time and randomness.

## Coverage — a floor, not a goal

Coverage measures lines executed, not behavior verified. High coverage with weak
assertions is false comfort; a covered line with no assertion proves only that it did not
crash. Use coverage to find *untested* code, never as the definition of done — the
acceptance criteria are the definition of done.

Red flags: a coverage number quoted as quality; snapshot tests as the only assertion;
a test suite that has never been seen to fail; mocks asserting their own call order.

## Flaky tests

A flaky test is worse than no test: it trains the team to ignore red. Quarantine it
immediately, file the cause (usually time, order, or shared state), and fix or delete it.
A suite is only as trustworthy as its flakiest test.

## Worked example

Criterion: "a user cannot withdraw more than their balance."

- Unit: the balance check rejects an over-limit amount and accepts an at-limit amount
  (boundary). Pure, instant, many cases.
- Integration: the withdraw endpoint returns 422 and leaves the balance unchanged when
  the amount exceeds it — proves the check is wired to the transaction.
- End-to-end: one path — a user attempts an over-limit withdrawal and sees the error —
  proves the journey, nothing more.

The over-limit and at-limit cases live in the unit layer; the end-to-end test does not
re-enumerate them.
