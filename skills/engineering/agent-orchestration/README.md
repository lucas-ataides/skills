# agent-orchestration

> Orchestrate work too large for one straight pass to done — drive it as a bounded iterative loop (checkpointed or autonomous), or fan it out across parallel subagents with no concurrent-write corruption. Use when the user wants to finish an app, burn down a backlog to acceptance criteria, run an autonomous or checkpointed loop, split a job across agents, fan out, parallelize, or orchestrate subagents.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- finish an app
- burn down a backlog to acceptance criteria
- run an autonomous
- checkpointed loop
- split a job across agents
- fan out
- parallelize
- orchestrate subagents

## What it does

1. Define done as acceptance criteria.
2. Seed the resumable state.
3. Open the iteration and plan one slice.
4. Build the slice test-first, then gate it.
5. Record the result, then halt or loop.
6. Confirm the work fits and decompose into owned units.
7. Verify ownership is disjoint.
8. Dispatch, then verify each result before trusting it.
9. Integrate and gate the whole tree.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
