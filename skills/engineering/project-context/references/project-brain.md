# The project brain (brain.md)

The depth behind the "use the project brain" step in [the skill](../SKILL.md). **brain.md**
([github.com/mindmuxai/brain.md](https://github.com/mindmuxai/brain.md), Apache-2.0) is a
file-based, agent-agnostic standard plus a zero-dependency `brain` CLI for persistent
project memory. It is the project-scoped, in-repo, CLI-driven sibling of the personal
[second brain](../../../obsidian/second-brain/SKILL.md): same idea (durable Markdown memory
an agent reads and writes), different scope (this project, committed beside the code).

## Why it belongs in this repo

brain.md's cardinal rule **is** the [determinism doctrine](../../../meta/foundation/SKILL.md):

> brain files are **never hand-edited**. Agents read `BRAIN.md`, then use the `brain` CLI
> exclusively for every read and write — *correct by construction, no validator needed*.

That is exactly "the model only thinks; a deterministic tool does the work." The agent
supplies the judgment — what is worth recording and the *why* — and the CLI performs the
write identically every time. So adopting brain.md is not a new convention to police; it
is the doctrine, already enforced by someone else's tool.

## The model

- **`./brain/`** — the brain directory (root is configurable via `brainRoot` in
  `.mindmux/preferences.json`).
- **`BRAIN.md`** — the protocol manifest the agent reads first, scaffolded by setup.
- **Pages** — each holds a rewritable **`compiled_truth`** (the current understanding) and
  an append-only **`timeline`** (what happened, in order). `update-truth` rewrites the
  understanding and records why in a single atomic write; `append-timeline` only adds.

## Install (once per machine)

```sh
git clone https://github.com/mindmuxai/brain.md && cd brain.md
./setup          # symlinks its skills into ~/.claude/skills and ~/.codex/skills; puts `brain` on PATH
```

## The CLI the skills call

Never hand-edit a brain file — drive it through these:

| Command | Use |
| --- | --- |
| `brain brain-dir` | locate the brain (and detect whether the project has one) |
| `brain list-pages` / `brain read-page <id>` | ingest context before working |
| `brain create-page --id <id> --category <type> --title "<title>"` | open a page for a new entity or topic |
| `brain update-truth --id <id> --summary "<why>"` | rewrite the current understanding, with the reason |
| `brain append-timeline --id <id> --kind <type> --summary "<msg>"` | log a decision or event |
| `brain wire --agent claude-code,codex` | wire the brain into an agent |
| `brain reindex && brain lint-links` | rebuild the index and check links |

## How a skill uses it

1. **Detect.** Run `brain brain-dir`. A non-zero exit means the project has no brain — skip
   the brain steps and fall back to AGENTS.md.
2. **Ingest before acting.** `brain list-pages`, then `brain read-page <id>` for the pages
   the task touches, so the agent inherits prior context instead of rediscovering it.
3. **Record on change.** When a decision lands or the understanding shifts,
   `brain update-truth --summary "<why>"`; for an event, `brain append-timeline`. The CLI
   owns the file write; the agent owns only the summary.

## Relationship to AGENTS.md / TODO

AGENTS.md and TODO.md (this skill's `scripts/project-context.sh`) are the **lightweight,
always-present entry** — how to build, test, and work here, and what is in flight. The
brain is the **deep, evolving memory** — the accumulated truth and timeline per topic. A
project can have the entry layer without a brain; a project with a brain keeps the entry
layer pointing into it. The canonical spec, page schema, and frontmatter live in the
brain.md repository.
