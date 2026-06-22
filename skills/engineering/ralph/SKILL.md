---
name: ralph
description: Drive a backlog to done in a tight autonomous loop — one stable prompt re-reads a persistent state file, advances one item, gates it, and repeats with no human between iterations until every item is done and the gate is green. Use when the user wants to "ralph" a task, run a fixed prompt on a loop, burn down a large mechanical backlog autonomously, or run an agent unattended until done. For high-stakes, judgment-heavy work needing per-step approval, use the checkpointed app-completion-loop.
---

Run one stable prompt against a persistent backlog in a tight loop: re-read the state file, advance one item, prove it with the gate, record progress, and repeat with no human between iterations. The loop is autonomous, not checkpointed — the value is throughput on a backlog already well-specified enough that no per-step judgment is needed. The danger is the runaway, so the loop is bounded before the first iteration runs.

Ralph trades the human checkpoint for hard guardrails: a definition of done that decides termination, an iteration cap, a budget, and a no-progress detector that halts on stalled rounds. The checkpointed [app-completion-loop](../app-completion-loop/SKILL.md) is the safer cousin when stakes are high; ralph is for a large, mechanical, fully-specified backlog where stopping for approval each step wastes the autonomy.

## Steps

1. **Write the done-condition and the guardrails first.** Record the definition of done as a numbered backlog where each item is a binary, gate-decidable condition, then set the four bounds: an iteration cap N, a cost/time budget, a stall limit K, and the named gate command. The step ends once the backlog, N, the budget, K, and the gate all sit in writing before any iteration runs. See [the ralph loop](references/ralph-loop.md) for phrasing a backlog item and choosing the bounds.

2. **Seed the resumable state file.** Write the backlog and the loop counters into a durable committed state file — a `handoff/state.json` tied to [handoff](../../productivity/handoff/SKILL.md) — holding the open items, the done items, the iteration count, the spend, and the consecutive-stall count. The step ends once a cold reader could reconstruct the entire loop position from that file alone.

3. **Open the iteration by re-reading state.** Begin every iteration by reading `handoff/state.json` fresh, never from memory of the previous pass, then check the four halt conditions before doing any work. The step ends once the loop has loaded the current open set and confirmed the cap, budget, stall limit, and gate-green precondition all still permit another iteration.

4. **Advance exactly one backlog item under the safety rules.** Select the top open item and make the smallest change that closes it, taking no destructive operation and no external mutation without recorded approval. The step ends once one item's code change exists and no banned operation ran — see the safety rules in [the ralph loop](references/ralph-loop.md).

5. **Gate the change, then write the result back to state.** Run the named gate command; a red gate reverts the item to open and increments the stall count, and a green gate moves the item to done and resets the stall count to zero. The step ends once the gate result is recorded and `handoff/state.json` reflects the new open set, counts, and spend.

6. **Halt or loop on the checkable conditions.** Stop when the open set is empty with the gate green (success), or when the iteration cap, the budget, or the stall limit K trips (guardrail halt); otherwise return to step 3. The step ends, and the loop is finished, once one stop condition holds and a final state with its termination reason is written.

See also [the ralph loop](references/ralph-loop.md) for the technique, the done-condition, every guardrail, the state-file contract, when ralph fits versus the checkpointed loop, the failure modes, the red flags, and a worked two-iteration example, and the checkpointed [app-completion-loop](../app-completion-loop/SKILL.md) for high-stakes work.
