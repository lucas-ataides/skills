---
name: bootstrap
description: Bootstrap a repository to use ataides-skills in one pass — scaffold AGENTS.md (with the skills directive), a TODO list, and a project brain (index, a Mermaid architecture map, and a log), then fill them. Use to set up a new or existing repo for the skills, to onboard a project, when a repo lacks an AGENTS.md/CLAUDE.md or a brain, or when the user says bootstrap, onboard, or set up this repo.
---

<!-- skill-lint: disable SK080 — "TODO" names the TODO.md file the scaffold writes, not a stray authoring marker. -->

Set a repository up so an agent — Claude Code or Cursor — can pick it up cold and work in it with ataides-skills. One deterministic scaffold writes the files; the agent then fills the parts that need synthesis. The scaffold never overwrites an existing file, so it is safe to run on a populated repo.

## Steps

1. **Scaffold the files.** At the repository root, run `skills/engineering/project-context/scripts/project-context.sh bootstrap`. The helper writes the files that are missing — an `AGENTS.md` carrying the build/test placeholders and the ataides-skills directive, a `TODO.md`, and a `brain/` holding `index.md`, a Mermaid `architecture.md`, and an append-only `log.md` — and never overwrites an existing one. The step is done once the helper prints its created-or-kept lines.

2. **Fill the scaffolds.** Replace the `AGENTS.md` placeholders with the real install, build, test, run, and lint commands, the conventions, the quality gates, and the gotchas via [project-context](../project-context/SKILL.md); then draw the system's real components, boundaries, and data flow into `brain/architecture.md` via [software-architecture](../software-architecture/SKILL.md). The step is done once a newcomer could build and test from `AGENTS.md` alone and the Mermaid map shows the actual components and their seams.

<!-- skill-lint: enable SK080 -->

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
