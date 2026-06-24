# The project brain

The depth behind the "use the project brain" step in [the skill](../SKILL.md). The project
brain is a **predefined Markdown structure** committed in a repo's `brain/` directory — no
tool to install, no script to run. It is the project-scoped, in-repo sibling of the personal
[second brain](../../../obsidian/second-brain/SKILL.md): durable memory an agent reads before
working and updates as understanding changes. The structure *is* the determinism — a fixed,
predictable shape the agent fills the same way every time. (Model inspired by brain.md.)

## Why a structure, not a script

A brain lives in every repo you touch, so a per-repo script would be friction — something to
install and remember to call. A predefined structure travels for free: it is plain Markdown,
readable by any agent (Claude, Cursor, Codex) and any human, with nothing to run. The
trade-off is honest — without a script enforcing it, the agent must hold the shape itself, so
the template below is fixed and small enough to follow exactly, and an optional validator
pass (below) catches drift.

## The structure

```
brain/
  README.md        the protocol + index (every brain has this)
  <slug>.md        one page per topic, entity, decision, or system
```

- **One page per thing.** Filenames are lowercase slugs (`auth-flow.md`, `acme-corp.md`) so
  they double as `[[wikilink]]` targets.
- **Two parts per page.** A **Truth** section is the current understanding, *rewritten in
  place* — keep it current, never a log. A **Timeline** section is *append-only* — what
  changed and why, newest at the bottom.

### `brain/README.md` — drop this in each repo's `brain/`

```markdown
# Project brain

Durable project memory for agents. One page per topic under `brain/`, plain Markdown — no
tool required. Each page has:

- **Truth** — the current understanding, rewritten in place.
- **Timeline** — append-only: what changed, when, and why.
- **Related** — `[[wikilinks]]` to other pages.

Read the pages a task touches before working; update Truth and append a Timeline line when
something changes. Never let Truth drift from what the code actually does.

## Pages
- [[auth-flow]] — how auth works
```

### Page template — copy for a new page

```markdown
---
title: "Auth flow"
type: topic        # topic | person | project | decision | system | risk
updated: 2026-06-24
---

# Auth flow

## Truth
Sessions are JWTs issued by Keycloak via OIDC; the API validates them at the edge.

## Timeline
- 2026-06-24 — Switched off Cognito to Keycloak (ADR-1): self-host control, OIDC parity.

## Related
- [[keycloak-deploy]]
```

## How a skill uses it

1. **Read before acting.** Open the pages a task touches (start from `brain/README.md`), so
   the agent inherits the settled understanding instead of rediscovering it.
2. **Update on change.** When a decision lands or the understanding shifts, rewrite that
   page's Truth in place and append a dated Timeline line with the *why*. Open a new page
   from the template for a new topic. Cross-link with `[[wikilinks]]`.

## Optional validation (no per-repo tool)

Because the format matches the second brain's, the plugin's generic validators check a
`brain/` directory deterministically — links resolve, slugs are clean — without anything
installed in the project:

```sh
python skills/obsidian/second-brain/scripts/validate-wikilinks.py --vault ./brain
python skills/obsidian/second-brain/scripts/validate-slugs.py --vault ./brain
```

## Relationship to AGENTS.md / TODO

AGENTS.md and TODO.md (`scripts/project-context.sh`) are the **lightweight, always-present
entry** — how to build, test, and work here, and what is in flight. The brain is the
**deep, evolving memory** — the accumulated truth and timeline per topic. A small project may
need only the entry layer; a long-lived one keeps `brain/README.md` linked from AGENTS.md so
an agent always finds it.
