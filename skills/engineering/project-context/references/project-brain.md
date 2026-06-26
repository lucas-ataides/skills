# The project brain — an LLM wiki for the repo

The depth behind the "use the project brain" step in [the skill](../SKILL.md). The project
brain is a **predefined Markdown structure** in a repo's `brain/` directory, following
[Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
No tool to install: the structure is plain Markdown and the agent does all the bookkeeping.
It is the project-scoped sibling of the personal
[second brain](../../../obsidian/second-brain/SKILL.md), which follows the same pattern.

## The idea

Not retrieval-over-files-each-time, but a **persistent, compounding synthesis**. The repo's
code, commits, and PRs are the immutable raw sources; the brain is the understanding they do
not carry — why the system is shaped this way, what was decided and rejected, where the
bodies are buried. The agent compiles that once and keeps it current, so the next agent
reads a settled wiki instead of re-deriving it. The tedious part is the bookkeeping
(cross-links, the index, the log) — and that is exactly what an agent does without getting
bored.

## The structure

```
brain/
  index.md         the catalog — every page, one-line summary, by category. Read FIRST.
  architecture.md  the system map — a Mermaid graph of components, boundaries, data flow.
  log.md           append-only, parseable: ## [YYYY-MM-DD] <kind> | <summary>
  <slug>.md        wiki pages — synthesis of an entity, concept, decision, or system
```

`project-context.sh bootstrap` seeds `index.md`, `architecture.md`, and `log.md`; the agent
fills the rest.

Filenames are lowercase slugs so they double as `[[wikilink]]` targets. Pages are
**synthesis kept current** (rewritten in place), not a log — the chronology lives once in
`log.md`. The repo's `AGENTS.md` points at `brain/index.md` so an agent always finds it.

### `brain/index.md`

```markdown
# Project brain

An LLM wiki for this repo (Karpathy pattern). The agent owns it: read `index.md` first,
then the pages a task touches. On a change, update the page, refresh its line here, and
append to `log.md`. Synthesis only — never restate the code; flag contradictions with their
source. Plain Markdown, no tool required.

## Architecture
- [[auth-flow]] — how auth works end to end
## Decisions
- [[adr-keycloak]] — Cognito → Keycloak, and why
## Systems
- [[billing-service]] — the billing service and its seams
```

### `brain/architecture.md`

Read first for orientation: the whole system as one **Mermaid graph** — components, the
boundaries between them, and how data flows — plus entry points and a "how to work here" note.
It is synthesis, not a file listing; draw and maintain it with
[software-architecture](../../software-architecture/SKILL.md) (C4 + Mermaid).

### A wiki page

```markdown
---
title: "Auth flow"
type: concept        # concept | entity | decision | system | risk
updated: 2026-06-24
sources: [commit a1b2c3d, "PR #45"]
---

# Auth flow

Sessions are JWTs issued by Keycloak via OIDC; the API validates them at the edge.
Replaced Cognito for self-host control and OIDC parity (see [[adr-keycloak]]).

> Contradiction (2026-06-24): `legacy-api` still calls Cognito directly — not yet migrated.
> Source: commit a1b2c3d.

## Related
- [[adr-keycloak]] · [[billing-service]]
```

### `brain/log.md`

```markdown
# Log

## [2026-06-24] decision | Cognito → Keycloak (adr-keycloak)
## [2026-06-24] ingest | auth-flow synthesized from PR #45
```

## The rules (from the pattern)

1. **The agent owns the wiki.** Every page, cross-reference, index line, and log entry is the
   agent's to maintain — you curate the code and ask questions.
2. **Index first.** Read `brain/index.md` before drilling into pages.
3. **Synthesis, not a dump.** A page compiles understanding the code lacks; it never restates
   the code, which is the raw source.
4. **Contradictions are flagged, not silenced.** New information that conflicts with a page is
   noted inline with its source, never quietly overwritten.
5. **The log is append-only and parseable.** One line per event, the `## [date] kind | …`
   prefix, so it stays machine-readable.
6. **One change touches many files.** A decision updates the affected page, refreshes its
   `index.md` line, and appends `log.md` — the agent does the whole sweep in one pass.

## Workflow

- **Read:** `brain/index.md` → the listed pages a task touches → follow `[[wikilinks]]`.
- **Update:** rewrite the affected page in place, refresh its `index.md` summary, append a
  `log.md` line; flag a contradiction with its source.
- **Lint (optional, no per-repo tool):** the format matches the second brain, so the plugin's
  generic validators check `./brain` deterministically — links resolve, slugs are clean:
  ```sh
  python skills/obsidian/second-brain/scripts/validate-wikilinks.py --vault ./brain
  python skills/obsidian/second-brain/scripts/validate-slugs.py --vault ./brain
  ```

## Relationship to AGENTS.md / TODO

`AGENTS.md` and `TODO.md` (`scripts/project-context.sh`) are the **lightweight, always-present
entry** — how to build, test, and work here, and what is in flight. The brain is the **deep,
compounding wiki** — the synthesized understanding per topic. A small project may need only
the entry layer; a long-lived one keeps `brain/index.md` linked from `AGENTS.md` so every
agent starts from the catalog.
