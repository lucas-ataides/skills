# Memory architecture

The shared model under all four capabilities — capture, compile, retrieve,
maintain. A second brain is a durable, source-backed memory layer for an
agent/founder: a folder of plain Markdown notes that opens in Obsidian as an
ordinary vault and reads as a clean knowledge base for a human. Capture writes to
it fast, the compiler builds it from raw sources without inventing facts,
retrieval reads it back as connected context, and the maintenance loop keeps it
current. This page defines the four memory types, the note formats, the
frontmatter contract, and how retrieval traverses the result.

The doctrine these choices inherit — predictability over cleverness, a script
over freehand judgment — is the [foundation](../../../meta/foundation/SKILL.md).
The review depth bar is [code-review](../../../engineering/code-review/SKILL.md):
judge the vault against what it must deliver (fast recall of connected context),
not only whether each note is individually tidy.

## The four memory types

A useful agent memory separates what it *knows* from how it *acts*, and keeps the
evidence for both:

1. **Declarative memory** — entities and facts. People, Companies, Projects,
   Products, Topics, Decisions. "Ada prefers async standups." Each fact is a
   claim with a source and a confidence.
2. **Procedural memory** — how things are done and what is preferred. Procedures
   ("how we cut a release") and Preferences ("Lucas wants negative conclusions
   stated first"). These steer the agent's behavior.
3. **Source traces** — the raw provenance. One note per ingested source under
   `raw/<domain>/`, recording where a fact came from so any claim audits back
   to its origin.
4. **Context packs** — pre-assembled briefings. A context pack stitches the
   declarative and procedural notes relevant to one recurring task into a single
   note the agent loads at the start of that task, so retrieval is one read, not
   a graph walk.

Connectors are the fifth concern — not a memory type but the gated doorway
through which external sources enter. Every connector is recorded in
SOURCE-MANIFEST.md before a read; the gate lives in
[the compiler reference](compiler.md).

## The folder structure

The vault follows the Life OS domain structure (Karpathy's LLM Wiki pattern):

```
<vault>/
  work/               personal/          finance/
  ├── companies/      ├── health/        ├── accounts/
  ├── people/         ├── relationships/ ├── income/
  ├── products/       ├── goals/         ├── investments/
  ├── projects/       ├── journal/      └── planning/
  ├── topics/         └── preferences/
  ├── decisions/      clients/           learning/
  ├── procedures/     ├── entities/      ├── books/
  ├── preferences/    └── projects/      ├── courses/
  ├── maps/                              └── concepts/
  └── context-packs/
  raw/
  ├── work/            personal/         finance/         assets/
  _templates/          _archive/         _tools/
  SCHEMA.md            index.md          log.md           AGENTS.md
  README.md
```

- **Domain folders** (`work/`, `personal/`, etc.) hold canonical knowledge — one entity
  or fact-cluster per note, source-backed.
- **`raw/`** holds one note per ingested source — the provenance layer, organized
  by domain. Never modified after ingestion.
- **`Context Packs/`** (under `work/`) holds assembled briefings retrieval loads.
- **`Maps/`** (under `work/`) holds Maps of Content (MOCs): index notes that link
  related canonical notes.
- **`_templates/`** holds note templates for consistent creation across domains.
- **`_tools/`** holds validator scripts so the vault re-validates on its own.
- **`_archive/`** holds superseded content.
- Root files: `SCHEMA.md` (constitution), `index.md` (catalog), `log.md` (timeline),
  `AGENTS.md` (agent orientation), `README.md` (human intro).

Fast CRUD capture writes typed notes into the matching domain folders through
`scripts/vault.sh`, routing by type and domain.

## Note formats

Every canonical note carries YAML frontmatter, a body of source-backed claims,
and a provenance section. The frontmatter is the machine-readable contract; the
body is the human-readable knowledge.

### Person note

```markdown
---
type: person
aliases: [Ada, Countess Lovelace]
tags: [person, collaborator]
status: active
confidence: high
sources:
  - [[Sources/gmail-2026-06-ada-thread]]
  - manifest:gmail-personal
updated: 2026-06-22
---

# Ada Lovelace

Collaborator on the Analytical Engine project. Prefers async standups over
synchronous meetings (confidence: high, two independent sources).

Reportedly fluent in French — single source, unconfirmed (confidence: low).

## Relationships
- Works with [[Charles Babbage]] on [[Analytical Engine]].

## Sources
- [[Sources/gmail-2026-06-ada-thread]] — async-standup preference.
- [[Sources/notion-team-roster]] — role and relationships.
```

### Decision note

```markdown
---
type: decision
tags: [decision, architecture]
status: accepted
date: 2026-05-10
confidence: high
sources:
  - [[Sources/slack-arch-channel-2026-05]]
updated: 2026-06-22
---

# Decision: adopt event-driven sync between billing and ledger

## Context
Cross-service calls coupled billing to ledger latency (per
[[Sources/slack-arch-channel-2026-05]]).

## Decision
Replace the synchronous call with a domain event.

## Consequences
- Looser coupling; eventual consistency the ledger must tolerate.

## Sources
- [[Sources/slack-arch-channel-2026-05]] — the thread where this was agreed.
```

### Context pack note

The retrieval workhorse — one read that briefs a whole recurring task:

```markdown
---
type: context-pack
task: "weekly-investor-update"
tags: [context-pack]
confidence: medium
sources:
  - manifest:notion-workspace
updated: 2026-06-22
---

# Context pack: weekly investor update

Load before drafting the investor update.

## Who
- [[People/Ada Lovelace]] — lead, async preference.

## Decisions in force
- [[Decisions/adopt-event-driven-sync]]

## Preferences
- [[Preferences/investor-update-tone]] — numbers first, no hedging.

## Open commitments
- [[Commitments/ship-billing-v2-by-q3]]

## Sources
- manifest:notion-workspace — roster, roadmap, prior updates.
```

### Source trace note

```markdown
---
type: source
connector: gmail
account: lucasatab@gmail.com
captured: 2026-06-22T10:00:00Z
sensitivity: personal
manifest:
  - gmail-personal
---

# Source: Gmail thread "Standup cadence" (2026-06)

Summary of the thread, not a verbatim copy. Ada states a preference for async
standups; Babbage agrees. No credentials, no private contact details copied.
```

## Frontmatter contract

| Key | Meaning | Required on canonical notes |
|-----|---------|------------------------------|
| `type` | note class (person, company, decision, …) | yes |
| `sources` / `provenance` | list of `[[Sources/…]]` links or `manifest:<id>` | yes |
| `confidence` | high / medium / low — the weakest claim sets the floor | yes |
| `aliases` | alternate names Obsidian resolves links by | when the entity has them |
| `status` | active / archived / accepted / superseded | recommended |
| `updated` | ISO date of the last compile touch | yes |
| `sensitivity` | public / internal / personal / restricted | on any source-derived note |

Hand-captured notes carry a lighter shared block — `title`, `type`, `created`,
`tags` — owned by the `vault.sh` template; the compiler adds the provenance and
confidence fields when a note graduates into source-backed canonical knowledge.

## Representing uncertainty and never inventing facts

The cardinal rule: a note states only what a source supports. Three mechanics
enforce it:

- **Confidence per claim.** A claim backed by one source is `low`; corroborated
  by two independent sources, `high`. The note's frontmatter `confidence` is the
  minimum across its claims.
- **Explicit unknowns.** A gap is written as a gap ("role unknown — not in any
  source"), never filled by inference. An invented fact is a defect the critic
  pass and `validate-sources.py` exist to catch.
- **Single-source flags.** A claim from one unverified source carries an inline
  "single source, unconfirmed" marker so a reader weights it correctly.

## Retrieval: the point of a second brain

Memory exists to be looked up. Retrieval reads the vault three ways, cheapest
first, and the procedure lives in full in
[crud-and-retrieval.md](crud-and-retrieval.md):

1. **Context pack first.** When a recurring task already has a pack under
   `Context Packs/`, one `vault.sh find` for that pack returns the whole
   briefing — the cheapest path, and the reason packs exist.
2. **Search by entity, tag, or text.** `scripts/vault.sh find "<query>"` locates
   notes by tag (`tags: [project]`), title, or full text — the entry point when
   no pack covers the need.
3. **Follow the links.** Open a located note and read its `## Related` /
   `## Relationships` wikilinks and its `## Sources`, then read the linked notes.
   The graph walk turns one hit into the connected context the task needs, and
   every claim traces back to a source.

A retrieval answer cites the notes it came from, so the founder (or the agent
acting for them) can audit the recall against its provenance — the same
source-backed discipline the compiler enforces on the way in.
