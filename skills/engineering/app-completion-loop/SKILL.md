---
name: app-completion-loop
description: Drive an application to done in checkpointed iterations — plan a slice, build it test-first, gate it, checkpoint for approval, repeat. Use when the user wants to finish an app, burn down a backlog to acceptance criteria, or build feature-by-feature with a human approving each step rather than running fully autonomously.
---

Drive the application to done one checkpointed iteration at a time. Each pass plans the smallest slice that moves a criterion, builds the slice test-first, gates it, then halts at a checkpoint for human approval before the next pass begins. The loop is checkpointed, not autonomous — the value is that a human steers at every phase boundary, so progress stays reviewable and reversible.

The loop converges because every iteration is bounded: a named slice, a green gate, an approved checkpoint. An unbounded loop that never reports is the failure this skill exists to prevent.

## Steps

1. **Define done.** Write the definition of done as a numbered list of acceptance criteria, each an observable condition a gate or a test can decide. The definition is complete when every criterion is checkable and the list, taken together, means the app is finished. See [the loop protocol](references/loop-protocol.md) for how to phrase a criterion.

2. **Plan the slice.** Choose the smallest slice that moves one open criterion measurably closer to done, preferring a thin vertical cut over a broad horizontal one. Write the slice as a one-line goal naming the criterion it advances and the test that will prove it. The step is done when the slice fits one review and names its target criterion.

3. **Checkpoint the plan.** Report the slice goal, the criterion it advances, and the expected diff size, then pause for approval before any code is written. A slice too large to review in one sitting is split here, not after building. This checkpoint clears once a human approves the planned slice.

4. **Build the slice test-first.** Follow [tdd](../tdd/SKILL.md) for the slice: a failing test that states the slice's behavior, then the minimum code that turns it green. The step is done when the slice's behavior has a test that failed before the code existed and passes after.

5. **Gate the slice.** Run `skill-gate --strict` at the repo root. A red gate holds the slice open; correct the code and rerun until the gate exits zero. The slice is gated when `skill-gate --strict` reports zero failures.

6. **Checkpoint the result.** Report what the slice delivered, which criteria now pass, which remain open, and any blocker or deviation from the plan, following the checkpoint protocol in [the loop protocol](references/loop-protocol.md). The checkpoint clears once a human approves continuing or redirects the next slice.

7. **Loop or finish.** Return to step 2 while an acceptance criterion remains open and no drift signal has tripped. The loop is finished when every criterion in the definition of done passes its gate and the final checkpoint is approved.

See also [the loop protocol](references/loop-protocol.md) for slicing, the checkpoint report format, blocker handling, drift detection, the failure modes, and a worked two-iteration example.
