# agent-loop

> Drive a codebase to done in an iterative loop — define done as acceptance criteria, plan the smallest slice, build it test-first, gate it, record state, repeat until the backlog is empty and the gate is green. Two modes — checkpointed pauses for human approval at each phase boundary, autonomous runs unattended under hard guardrails. Use when the user wants to finish an app, burn down a backlog to acceptance criteria, or run an autonomous or checkpointed loop until done.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- finish an app
- burn down a backlog to acceptance criteria
- run an autonomous
- checkpointed loop until done

## What it does

1. Define done as acceptance criteria.
2. Seed the resumable state.
3. Open the iteration and plan one slice.
4. Build the slice test-first.
5. Gate the slice.
6. Record the result, then halt or loop on the checkable condition.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
