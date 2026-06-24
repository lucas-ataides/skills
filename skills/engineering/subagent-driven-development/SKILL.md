---
name: subagent-driven-development
description: Decompose a large task into independent units and run them through parallel subagents without concurrent-write corruption. Use when a job is big and splits cleanly across agents, when breadth dominates depth (per-module, per-endpoint, per-package work), when isolating heavy context into workers, or when the user asks to fan out, parallelize, or orchestrate subagents. Not for tightly-coupled work or tiny single-file edits.
---

Subagent-driven development splits one large task into independent units and runs them through parallel worker agents. The orchestrator decomposes the work, dispatches a brief per unit, verifies each result, and merges. The governing invariant: **no two agents write the same file** — concurrent writes to one file race and corrupt non-reproducibly, the exact failure this protocol exists to prevent.

This procedure is the orchestrator's. Worker agents are non-user-facing, so each dispatch carries the [cavecrew](../../meta/cavecrew/SKILL.md) protocol. The mechanics, failure modes, and a worked example live in [references/orchestration.md](references/orchestration.md).

## Steps

1. **Confirm the work fits.** State why subagents earn their cost: the units are independent, breadth dominates, or heavy context wants isolating. Reject the pattern for tightly-coupled or tiny work and do it inline instead. Proceed only once the justification names independence, not speed.

2. **Decompose into owned units.** List the deliverables, group them by the files each touches, and cut the groups so no two share a writable file. Name each unit's exact file set, scope, and output contract; flag cross-unit dependencies as sequential edges. The step is done when every unit is completable from its brief alone and writes a disjoint file set.

3. **Verify ownership is disjoint.** Check that the units' owned-file sets are pairwise non-overlapping, and assign every piece of shared state (manifest, lockfile, barrel export, registry) to the orchestrator, owned by no worker. The step passes when no file appears in two ownership sets and shared state is orchestrator-only.

4. **Write a dispatch brief per unit.** Give each brief five parts: self-contained context, exact scope with non-goals, the named owned-file set, the output contract the orchestrator will consume, and a pointer to the [cavecrew](../../meta/cavecrew/SKILL.md) data protocol. A brief is ready when a reader with zero prior context could execute the unit and produce the contracted output.

5. **Dispatch, then verify each result before trusting it.** Run the units, parallel where independent and ordered along dependency edges. Per agent, read the actual diff, run the contract's proof command and observe it pass, and check the change against [the review lenses](../code-review/references/review-lenses.md) — scope delivered, inside owned files. Verification is complete when every result is confirmed against its contract by observed output, not by the worker's claim.

6. **Re-dispatch failures from a clean state.** State the precise failure, reset that unit's owned files to their pre-dispatch version from source control, re-brief with the corrected constraint, and re-dispatch. Stop and re-decompose after a unit fails twice. The step resolves once each unit has verified clean, with any twice-failed unit escalated as a decomposition fault.

7. **Integrate and gate the whole tree.** Apply the orchestrator-owned shared-state changes serially, resolve the flagged seams, then run the build, type-check, and full test suite across the merged tree. The task is done when the integrated tree passes the gate — unit-level green alone does not satisfy this.

## See also

- [cavecrew](../../meta/cavecrew/SKILL.md) — the output protocol every dispatched worker follows.
- [project-context](../project-context/SKILL.md) — keep the project's AGENTS.md, task list, and project brain current.
