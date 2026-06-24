---
name: project-context
description: Keep every project legible to agents — an AGENTS.md/CLAUDE.md, a current TODO list, and the project brain (brain.md) for deep CLI-managed memory. Use when starting work in a project, when an AGENTS.md/CLAUDE.md or TODO is missing, to adopt or read the project brain, or to keep them current as the project changes.
---

<!-- skill-lint: disable SK080 — "TODO" is this skill's subject (the TODO.md task file), not a stray authoring marker. -->

A project an agent can pick up cold needs two living files: an AGENTS.md (or CLAUDE.md) that states how to build, test, and work here, and a TODO list that holds what is in flight. This skill creates them when absent and keeps them true to the project. Stale instructions mislead, so the files are updated in the same change as the code.

For deep, evolving memory, a project can adopt the **project brain** (brain.md) — a CLI-managed store the agent reads and writes without ever hand-editing, covered in step 6.

## Steps

1. **Detect.** Run the helper `skills/engineering/project-context/scripts/project-context.sh check` at the project root. The output reports whether AGENTS.md or CLAUDE.md and TODO.md are present. The step is done once the status of all three is known.

2. **Create what is missing.** Run the helper with `init`. It writes an AGENTS.md only in the absence of both AGENTS.md and CLAUDE.md, adds a missing TODO.md, and never overwrites an existing file. The step is done once an agent-instructions file and a TODO file both exist.

3. **Fill the agent-instructions file.** Replace the placeholders with the real build, test, run, and lint commands, the conventions, the load-bearing architecture facts, the quality gates, and the gotchas. Each entry is concrete enough to act on without guessing. The step is done once a newcomer could build and test from the file alone.

4. **Keep the TODO current.** Put the in-flight item under Now, the queue under Next, and finished items under Done. One item per line, each a checkable outcome. The step is done once the TODO matches the actual state of the work.

5. **Maintain on change.** A changed command, convention, or gotcha updates AGENTS.md in the same commit; a started or finished task moves in TODO.md. The depth — what a strong AGENTS.md contains and the anti-ambiguity rules it follows — lives in [the context-files guide](references/context-files.md).

6. **Use the project brain for deep memory.** Run `brain brain-dir` to detect whether the project has a brain (brain.md). When it does, read context with `brain list-pages` and `brain read-page` before working, then record a decision or shifted understanding with `brain update-truth` or `brain append-timeline` — never hand-edit the files. The CLI, the page model, and install live in [the project brain reference](references/project-brain.md). The step is done once the brain is read for context, or `brain brain-dir` confirms there is none.

<!-- skill-lint: enable SK080 -->

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
