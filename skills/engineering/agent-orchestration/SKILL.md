---
name: agent-orchestration
description: Orchestrate work too large for one straight pass to done — drive it as a bounded iterative loop (checkpointed or autonomous), or fan it out across parallel subagents with no concurrent-write corruption. Use when the user wants to finish an app, burn down a backlog to acceptance criteria, run an autonomous or checkpointed loop, split a job across agents, fan out, parallelize, or orchestrate subagents.
---

Orchestrate work too large for one straight pass to done. Two patterns share one concern — bounded units that converge to a green gate, never an unbounded run that edits without reporting and never two agents racing the same file:

- **The loop** — drive to done one bounded iteration at a time, in sequence. Pick it for depth: each slice builds on the last, and done is a backlog of gate-decidable criteria.
- **Fan-out** — decompose into independent owned-file units and run them through parallel subagents. Pick it for breadth: the units are independent and the work can be cut so no two agents write the same file.

The two compose — a loop slice with independent sub-parts fans out. Pick the pattern, then follow its steps.

## The loop — drive to done iteratively

Pick the mode before the first iteration. **Checkpointed** (default, safe) — a human approves at each phase boundary, for high-stakes or judgment-heavy work. **Autonomous** (ralph-style) — one stable prompt re-reads the state file and advances the backlog unattended under the full guardrail set, for a large mechanical gate-decidable backlog. The deciding question: could a gate, with no human reading the diff, decide each backlog item correctly? A confident yes permits autonomous; any real doubt selects checkpointed.

1. **Define done as acceptance criteria.** Write done as a numbered backlog where each item is observable, binary, and gate-decidable, and record the chosen mode on the same page. This step ends once every backlog item is checkable, the list as a whole means the codebase is finished, and the mode is recorded. See [the loop protocol](references/loop-protocol.md).

2. **Seed the resumable state.** Write the backlog and counters into a committed `handoff/state.json` tied to [handoff](../../productivity/handoff/SKILL.md) — open items, done items, iteration count, spend, and the consecutive-stall count. In autonomous mode, set the four bounds now: an iteration cap N, a cost/time budget, a stall limit K, and the named gate command. This step ends once a cold reader could reconstruct the loop position from the file alone.

3. **Open the iteration and plan one slice.** Read `handoff/state.json` fresh, then cut the smallest slice that moves one open criterion measurably — a thin vertical cut expressible as a single failing test. Autonomous checks the four halt conditions before any work; checkpointed reports the slice goal, its target criterion, and the expected diff size, then pauses for approval. This step ends once one slice names its target criterion and the mode's precondition clears.

4. **Build the slice test-first, then gate it.** Follow [tdd](../tdd/SKILL.md): a failing test for the slice's behavior, then the minimum code that turns it green, with no destructive or external mutation without recorded approval. To fan one slice across independent owned-file units, use the fan-out pattern below. Then run `skill-gate --strict`: a red gate holds the slice open, restores its changed files to their pre-iteration state, and increments the stall count; a green gate moves the criterion to done and resets the stall count. This step ends once `skill-gate --strict` exits zero, or the failed slice's edits are reverted.

5. **Record the result, then halt or loop.** Write the new open set, counts, and spend back to `handoff/state.json` atomically. Checkpointed reports delivered work, criteria status, the gate result, and any blocker, then pauses; autonomous checks the guardrails and continues. The loop is finished once the backlog is empty with the gate green, or one stop signal trips — a tripped guardrail under autonomous, a drift signal or human redirect under checkpointed; otherwise it returns to plan the next slice. The modes, the guardrail set, the working-tree reset, and drift detection live in [the loop protocol](references/loop-protocol.md).

## Fan-out — parallel subagents

The orchestrator decomposes the work, dispatches a brief per unit, verifies each result, and merges. The governing invariant: **no two agents write the same file** — concurrent writes race and corrupt non-reproducibly. Worker agents are non-user-facing, so each dispatch carries the [cavecrew](../../meta/cavecrew/SKILL.md) protocol; the mechanics and a worked example live in [the orchestration reference](references/orchestration.md).

1. **Confirm the work fits and decompose into owned units.** State why subagents earn their cost — the units are independent, breadth dominates, or heavy context wants isolating — then list the deliverables, group them by the files each touches, and cut the groups so no two share a writable file. Name each unit's file set, scope, and output contract. This step is done when every unit is completable from its brief alone and writes a disjoint file set.

2. **Verify ownership is disjoint.** Check that the units' owned-file sets are pairwise non-overlapping, and assign every piece of shared state (manifest, lockfile, barrel export, registry) to the orchestrator, owned by no worker. The step passes when no file appears in two ownership sets and shared state is orchestrator-only.

3. **Dispatch, then verify each result before trusting it.** Give each brief five parts — self-contained context, exact scope with non-goals, the named owned-file set, the output contract, and a pointer to the [cavecrew](../../meta/cavecrew/SKILL.md) protocol — then run the units, parallel where independent and ordered along dependency edges. Per agent, read the actual diff, run the contract's proof command and observe it pass, and check the change against [the review lenses](../code-review/references/review-lenses.md). Re-dispatch a failure from a clean state: reset the unit's owned files from source control, re-brief, then re-run; stop and re-decompose after a unit fails twice. This step is done when every result is confirmed against its contract by observed output.

4. **Integrate and gate the whole tree.** Apply the orchestrator-owned shared-state changes serially, resolve the flagged seams, then run the build, type-check, and full test suite across the merged tree. The task is done when the integrated tree passes the gate — unit-level green alone does not satisfy this.

## See also

- [tdd](../tdd/SKILL.md) — how each loop slice is built test-first.
- [cavecrew](../../meta/cavecrew/SKILL.md) — the output protocol every dispatched worker follows.
- [project-context](../project-context/SKILL.md) — keep the project's AGENTS.md, task list, and project brain current.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
