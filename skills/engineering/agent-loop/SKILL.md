---
name: agent-loop
description: Drive a codebase to done in an iterative loop — define done as acceptance criteria, plan the smallest slice, build it test-first, gate it, record state, repeat until the backlog is empty and the gate is green. Two modes — checkpointed pauses for human approval at each phase boundary, autonomous runs unattended under hard guardrails. Use when the user wants to finish an app, burn down a backlog to acceptance criteria, or run an autonomous or checkpointed loop until done.
---

Drive the codebase to **done** one bounded iteration at a time. Each pass plans the smallest slice that moves an acceptance criterion, builds the slice test-first, gates the slice, records state, then either pauses for human approval or continues unattended. The loop converges because every iteration is bounded — a named slice, a green gate, a recorded result — and the stop condition is fixed: the backlog is empty and the gate is green. An unbounded loop that edits without reporting and never terminates is the failure this skill exists to prevent.

Pick one of two modes before the first iteration:

- **checkpointed** (default, safe) — a human approves at each phase boundary, so progress stays reviewable and reversible. Suited to high-stakes, judgment-heavy work where a gate alone cannot decide whether a slice is done, or where a mistake is expensive to reverse.
- **autonomous** (ralph-style) — one stable prompt re-reads the state file and advances the backlog with no human between iterations, bounded by the full guardrail set. Suited to a large, mechanical, well-specified backlog where each item is gate-decidable and stopping for approval each step wastes the autonomy.

The deciding question: *could a gate, with no human reading the diff, decide each backlog item correctly?* A confident yes permits autonomous; any real doubt selects checkpointed. The default is checkpointed — an unnecessary checkpoint costs minutes, an autonomous loop loose on judgment-heavy work is a runaway nobody catches.

## Steps

1. **Define done as acceptance criteria.** Write the definition of done as a numbered backlog where each item is observable, binary, and gate-decidable — a condition a gate or a test rules on, not an opinion. State the chosen mode (checkpointed or autonomous) on the same page as the backlog. This step ends once every backlog item is checkable, the list as a whole means the codebase is finished, and the mode is recorded. See [the loop protocol](references/loop-protocol.md) for phrasing a criterion and choosing the mode.

2. **Seed the resumable state.** Write the backlog and the loop counters into a durable, committed state file — a `handoff/state.json` tied to [handoff](../../productivity/handoff/SKILL.md) — holding the open items, the done items, the iteration count, the spend, and the consecutive-stall count. In autonomous mode, set the four bounds now: an iteration cap N, a cost/time budget, a stall limit K, and the named gate command. This step ends once a cold reader could reconstruct the entire loop position from the file alone.

3. **Open the iteration and plan one slice.** Read `handoff/state.json` fresh rather than from memory of the previous pass, then cut the smallest slice that moves one open criterion measurably toward done — a thin vertical cut, expressible as a single failing test, reviewable in one sitting. The mode sets the precondition: autonomous checks the four halt conditions before any work; checkpointed reports the slice goal, its target criterion, and the expected diff size, then pauses for approval. This step ends once one slice names its target criterion and the mode's precondition clears. See [the loop protocol](references/loop-protocol.md) for slicing and the checkpoint protocol.

4. **Build the slice test-first.** Follow [tdd](../tdd/SKILL.md) for the slice: a failing test stating the slice's behavior, then the minimum code that turns the test green, taking no destructive operation and no external mutation without recorded approval. To fan one slice across independent owned-file units, compose [subagent-driven-development](../subagent-driven-development/SKILL.md). This step ends once the slice's behavior has a test that failed before the code existed and passes after, and no banned operation ran.

5. **Gate the slice.** Run `skill-gate --strict` at the repo root. A red gate holds the slice open, restores that slice's changed files to their pre-iteration state from version control so the next attempt starts clean, and increments the stall count; a green gate moves the criterion to done and resets the stall count to zero. This step ends once `skill-gate --strict` exits zero, or the failed slice's edits are reverted from the working tree. See [the loop protocol](references/loop-protocol.md) for the working-tree reset.

6. **Record the result, then halt or loop on the checkable condition.** Write the new open set, counts, and spend back to `handoff/state.json` atomically. The mode sets the boundary action: checkpointed reports delivered work, criteria status, the gate result, and any deviation or blocker, then pauses for approval; autonomous checks the guardrails and continues. This step ends, and the loop is finished, once the backlog is empty with the gate green (success), or one stop signal trips — a tripped guardrail under autonomous, a drift signal or human redirect under checkpointed. A loop with neither condition met returns to step 3.

See also [the loop protocol](references/loop-protocol.md) for the two modes, done-as-criteria, slicing, the checkpoint protocol, the guardrail set, the working-tree reset on a red gate, drift and thrash detection, the failure modes, and a worked example of one checkpointed iteration and one autonomous iteration.

## See also

- [tdd](../tdd/SKILL.md) — how each slice is built test-first.
- [subagent-driven-development](../subagent-driven-development/SKILL.md) — fan one slice across independent owned-file subagents when breadth dominates.

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md and task list current.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
