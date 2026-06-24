# The project brain

The depth behind the "use the project brain" step in [the skill](../SKILL.md). The project
brain is **our own** deterministic, CLI-only project memory — `scripts/brain.py` plus a
`./brain/` directory committed beside the code. It is the project-scoped, in-repo sibling of
the personal [second brain](../../../obsidian/second-brain/SKILL.md): same idea (durable
Markdown memory an agent reads and writes), different scope (this project). The page model
is inspired by brain.md; the implementation is ours, with no external dependency to install.

## Why it belongs here

Its cardinal rule **is** the [determinism doctrine](../../../meta/foundation/SKILL.md): a
brain file is **never hand-edited** — `scripts/brain.py` is the only writer, so the
structure is correct by construction and `--selftest` proves it. The agent supplies the
judgment (what to record and the *why*); the script performs the write, atomically and
identically every run.

## The model

- **`./brain/`** — the brain directory, committed in the project it describes.
- **`brain/index.md`** — the hub: the protocol note plus a wikilinked list of every page,
  rebuilt by `reindex`.
- **Pages** (`brain/<id>.md`) — each carries a rewritable **`## Truth`** (the current
  understanding) and an append-only **`## Timeline`** (what happened, in order). Updating
  the truth records *why* on the timeline in the same atomic write, so the reasoning is
  never lost.

## The CLI

| Command | Use |
| --- | --- |
| `scripts/brain.py init` | scaffold `./brain/` and its index |
| `scripts/brain.py list` | list pages (id · category · title); empty output means no brain yet |
| `scripts/brain.py read <id>` | print a page to ingest its context |
| `scripts/brain.py create --id <id> --title "<t>" [--category <c>]` | open a page for a new entity or topic |
| `scripts/brain.py truth <id> --text "<truth>" --why "<reason>"` | rewrite the current understanding, logging the reason |
| `scripts/brain.py timeline <id> --kind <type> --text "<msg>"` | append a decision or event |
| `scripts/brain.py reindex` | rebuild `brain/index.md` from the pages |

Run it at the project root; the brain lives in `./brain/`. Pass `--root <dir>` to point
elsewhere.

## How a skill uses it

1. **Detect + ingest.** `scripts/brain.py list`; for the pages the task touches,
   `scripts/brain.py read <id>` — so the agent inherits prior context instead of
   rediscovering it. No pages means no brain; fall back to AGENTS.md.
2. **Record on change.** When a decision lands or the understanding shifts,
   `scripts/brain.py truth <id> --text "…" --why "…"`; for an event,
   `scripts/brain.py timeline <id> --kind decision --text "…"`. Never open the file in an
   editor — the CLI owns the write.

## Relationship to AGENTS.md / TODO

AGENTS.md and TODO.md (`scripts/project-context.sh`) are the **lightweight, always-present
entry** — how to build, test, and work here, and what is in flight. The brain is the
**deep, evolving memory** — the accumulated truth and timeline per topic. A small project
may need only the entry layer; a long-lived one keeps the entry layer pointing into the
brain. Both are validated deterministically: the entry by `project-context.sh --selftest`,
the brain by `brain.py --selftest` and the repo's selftest gate.
