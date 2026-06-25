---
name: tdd
description: Build features and fix bugs test-first — red, green, refactor — with the loop enforced by the test gate. Use when the user wants to add a feature, fix a bug, change behavior under tests, or reproduce a defect with a failing test before fixing it.
---

Write the test before the code. The loop is red, then green, then refactor, and the loop is not optional. The discipline is the order: a test written first fails for a real reason and pins behavior the code does not yet have; a test written after the code tends only to ratify what the code already does.

Each phase ends on a condition the test gate can observe, so the loop is enforced, not merely intended. The deep mechanics — sizing a step, the false red, when TDD does not fit, a worked example — live in [tdd practice](references/tdd-practice.md).

## Steps

1. **Frame the next behavior.** State one observable behavior the change must add: this input yields that output, or this call produces that effect. A bug fix frames the behavior as the defect reproduced. The step is framed when the behavior is a single fact specific enough to pass or fail without judgment.

2. **Red — write one failing test.** Write a single test for that behavior, asserting the output or the observable effect rather than the internals. Run `skill-gate --category test`. The step is done when the gate reports one new test failing, and the failure message names the missing behavior rather than a syntax or import error. See the false-red trap in [tdd practice](references/tdd-practice.md).

3. **Green — write the least code that passes.** Write the minimum production code that turns the bar green, adding nothing for a behavior no current test demands. Run `skill-gate --category test` again. The step is done when the full suite is green, with no test skipped or commented out.

4. **Refactor — improve the design on green.** Improve naming, duplication, and structure while behavior stays constant; never reshape a red suite, because a red suite cannot tell a safe change from a breaking one. Run `skill-gate --category test` once more. The step is done when the suite is still green and no observable behavior changed.

5. **Harden the change.** Run `skill-gate --category lint`, then `skill-gate --category types`. The step is done when both commands exit zero.

6. **Advance or close.** Per remaining behavior, return to step 1 with the next one. The change is done when every framed behavior has a green test and steps 2 through 5 have each reported their completion criterion.

See also: [the foundation doctrine](../../meta/foundation/SKILL.md).

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md and task list current.

The full gate is [appsec](../appsec/SKILL.md) — clear it before the change ships.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
