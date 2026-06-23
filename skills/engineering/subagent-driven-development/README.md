# subagent-driven-development

> Decompose a large task into independent units and run them through parallel subagents without concurrent-write corruption. Use when a job is big and splits cleanly across agents, when breadth dominates depth (per-module, per-endpoint, per-package work), when isolating heavy context into workers, or when the user asks to fan out, parallelize, or orchestrate subagents. Not for tightly-coupled work or tiny single-file edits.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- a job is big and splits cleanly across agents
- when breadth dominates depth (per-module
- per-endpoint
- per-package work)
- when isolating heavy context into workers
- when the user asks to fan out
- parallelize
- orchestrate subagents

## What it does

1. Confirm the work fits.
2. Decompose into owned units.
3. Verify ownership is disjoint.
4. Write a dispatch brief per unit.
5. Dispatch, then verify each result before trusting it.
6. Re-dispatch failures from a clean state.
7. Integrate and gate the whole tree.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
