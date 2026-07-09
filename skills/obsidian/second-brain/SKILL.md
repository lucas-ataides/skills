---
name: second-brain
description: "Durable Obsidian memory for an agent or founder: capture notes, recall connected context, compile a source-backed vault from raw sources, and optionally maintain it autonomously. Use when the user wants to capture a person, project, meeting, idea, task, or daily note; jot into their vault; link or correlate entities; recall what they know, pull a context pack, or find a note by tag, title, or text; build or refresh a second brain from chats, emails, or connectors; or keep a vault validated."
---

A second brain is the durable, source-backed memory for an agent or founder: a
folder of plain Markdown notes that opens in Obsidian as an ordinary vault and
reads as a clean knowledge base. This skill unifies four capabilities under one
roof — **capture** notes fast, **retrieve** connected context, **compile** a
vault from raw sources, and optionally **maintain** it autonomously. Two rules
dominate the whole skill: never invent a fact a source does not support, and never
ship a copied secret.

Every vault mutation delegates to a script in `scripts/`, so a filename never
overwrites, a write is never half-finished, and the deterministic validators own
every verdict. The vault root resolves itself — `vault.sh` reads the configured
path from `skill-config`, an explicit `$VAULT` overrides it, and `./vault` is the
last-resort fallback; never hardcode an absolute path.

The depth bar is [code-review](../../engineering/code-review/SKILL.md): judge the
vault against what it must deliver — fast recall of connected, source-backed
context — not only whether each note is tidy. The determinism doctrine is the
[foundation](../../meta/foundation/SKILL.md).

## The vault structure (Life OS)

The vault follows Karpathy's LLM Wiki pattern with domain-based top-level
organization. Every mutation delegates to `scripts/vault.sh` or the
Obsidian MCP tools; the vault root resolves from `$VAULT`, `skill-config`,
or `./vault`.

```
<vault>/
├── SCHEMA.md              # Constitution — rules, conventions, tag taxonomy
├── index.md               # Master catalog of all pages
├── log.md                 # Chronological action log
│
├── raw/                   # Layer 1: Immutable sources
│   ├── work/              #   DefensePoint source documents
│   ├── personal/          #   Journal entries, personal docs
│   ├── finance/           #   Statements, receipts
│   └── assets/            #   Images, attachments
│
├── work/                  # Layer 2: Work domain
│   ├── companies/         #   DefensePoint and client profiles
│   ├── people/            #   Colleague profiles
│   ├── products/          #   point, hercules, etc.
│   ├── projects/          #   Active work projects
│   ├── topics/            #   Concepts: keycloak, azure, etc.
│   ├── decisions/         #   Architecture decisions (ADRs)
│   ├── procedures/        #   Runbooks and how-tos
│   ├── preferences/       #   Communication, working style
│   ├── maps/              #   Maps of Content
│   └── context-packs/     #   Pre-assembled task briefings
│
├── personal/              # Personal life
│   ├── health/            #   Medical, fitness, sleep
│   ├── relationships/     #   Family, friends
│   ├── goals/             #   Short and long-term goals
│   ├── journal/           #   Daily reflections
│   └── preferences/       #   Personal rules, values
│
├── finance/               # Money management
│   ├── accounts/          #   Bank accounts, cards
│   ├── income/            #   Salary, client income
│   ├── investments/       #   Portfolio, strategies
│   └── planning/          #   Budget, tax, retirement
│
├── clients/               # Direct/personal clients
│   ├── entities/          #   Client profiles
│   └── projects/          #   Client projects
│
├── learning/              # Knowledge & growth
│   ├── books/             #   Book notes
│   ├── courses/           #   Course notes
│   └── concepts/          #   Ideas and frameworks
│
├── _templates/            # Note templates
└── _archive/              # Superseded content
```

Capture routes notes to the correct domain folder via `vault.sh capture <type> "<title>" [domain=<domain>] [key=value...]`.
The domain defaults to `work`. Set `domain=personal`, `domain=finance`, `domain=clients`, or `domain=learning` for other life areas.

Route the request to one capability, then follow its step:

- **Capture / correlate** (the everyday path) — a thought to log, an entity to
  link → step 2, via [crud-and-retrieval.md](references/crud-and-retrieval.md).
- **Retrieve** (the point of a second brain) — recall a fact, brief a task, find a
  note → step 3, via [crud-and-retrieval.md](references/crud-and-retrieval.md).
- **Compile** (build from sources) — turn chats, emails, or connector output into
  a source-backed vault → steps 4–5, via [compiler.md](references/compiler.md).
- **Maintain** (autonomous) — burn down a source backlog unattended until the
  validators pass → step 6, via [maintenance.md](references/maintenance.md).

The memory model shared by all four — the four memory types, note formats, and
frontmatter contract — is in
[memory-architecture.md](references/memory-architecture.md).

## Steps

1. **Initialize and name the capability.** Run `scripts/vault.sh init` to resolve
   and create the vault root — the script reads the configured path from
   `skill-config`, so no manual `$VAULT` export is needed. Then map the request to
   one capability — capture, retrieve, compile, or maintain. This step is done once
   `init` prints the vault path and one capability is named for the request.

2. **Capture through the script.** Create a typed note with
   `scripts/vault.sh capture <type> "<title>" [key=value ...]`, append a
   timestamped log bullet with `scripts/vault.sh append <note> "<text>"`, and
   correlate entities with `scripts/vault.sh link <from> <to>` — the script
   renders uniform frontmatter, derives a safe slug, reserves a collision-free
   filename, and keeps each `link` idempotent. The eleven types and the
   capture-fast principle are in
   [crud-and-retrieval.md](references/crud-and-retrieval.md). This step is done
   once the command prints the note path and the requested links sit under
   `## Related`.

3. **Retrieve connected context.** Read `index.md` first (refresh with
   `scripts/vault.sh index`), then load an existing pack from `Context Packs/`
   for a recurring task, else locate notes with `scripts/vault.sh find "<query>"`
   by entity, tag (`tags: [project]`), text, or a declared alias, then follow the matched note's
   `## Related` and `## Sources` links into the connected notes — the retrieval
   procedure is in [crud-and-retrieval.md](references/crud-and-retrieval.md). This
   step is done once the recall cites the notes it came from, an empty result
   reported plainly rather than filled by invention.

4. **Compile: confirm, scaffold, orient, and pass HARD CHECKPOINT 1.** Confirm the
   four — the working directory, the output root, the source locations, and each
   connector's connected account. Scaffold the canonical vault with
   `scripts/scaffold.py <output-root>` (default
   `Compiled-Vaults/compiled-vault-brain-<date>/`, or an existing vault to compile
   in place), which lays the folders, the control files, and a self-contained
   `_tools/`. Inventory the sources, record every connector in SOURCE-MANIFEST.md,
   write `Reports/ORIENTATION-REPORT.md`, then run
   `scripts/generate-manifest.py --vault <path> --verify`. The four confirmations,
   the connector gate, the model tiering, and the resumable `state.json` contract
   live in [compiler.md](references/compiler.md). This step is done once the
   scaffold validates, the manifest verifier exits 0, and the user has approved at
   HARD CHECKPOINT 1.

5. **Compile: run the pipeline, smoke-pass at HARD CHECKPOINT 2, then hold the
   HARD GATES.** Drive each source batch through the nine-stage pipeline
   (parse → … → critic), journal `state.json` and `INGESTION-LOG.md` per batch,
   present a representative slice at HARD CHECKPOINT 2, then run every validator —
   `validate-wikilinks.py`, `validate-slugs.py`, `scan-secrets.py`,
   `validate-sources.py`, `validate-artifacts.sh`, and
   `generate-manifest.py --verify` — and branch on each exit code. The pipeline,
   the gates, and the redaction policy are in
   [compiler.md](references/compiler.md). This step is done once the user has
   approved the smoke pass and every validator exits 0 with the HARD GATES
   recorded as held in `COMPLETION-AUDIT.md`.

6. **Maintain: run the bounded autonomous loop.** Write the done-condition and the
   guardrails first (iteration cap N, cost/time budget, stall limit K, the
   validator command), seed `state.json` and `INGESTION-LOG.md`, then loop —
   re-read state, compile one source, run the validators, write state back — until
   the backlog is empty with the HARD GATES green, or a guardrail halts the run.
   The loop, the seven guardrails, and the autonomous-versus-checkpointed choice
   are in [maintenance.md](references/maintenance.md). This step is done once a
   termination reason (done, cap, budget, stall, or guardrail) is written to
   `state.json`.

7. **Remove only through the guard.** Delete a single note with
   `scripts/vault.sh rm <note>` — the one guarded path, which refuses the vault
   root and any target outside it. Bulk deletion is unsupported by design. This
   step is done once the command prints the removed path, or stops at the guard
   with its message.

## Scripts

Every operation delegates here; a script runs `--selftest` to build temp
fixtures, assert, and exit 0:

- `scripts/vault.sh` — init, capture, append, link, daily, find, index, and the guarded
  `rm` (the CRUD + correlation engine).
- `scripts/scaffold.py` — build the canonical vault (folders, control files, the
  `state.json` schema) and copy the validators into the vault's `_tools/`.
- `scripts/validate-wikilinks.py` — resolve `[[wikilinks]]`; report unresolved and
  ambiguous.
- `scripts/validate-slugs.py` — empty filenames, invalid paths, duplicate slugs,
  unsafe chars.
- `scripts/scan-secrets.py` — credential-shaped strings, reported masked for
  redaction.
- `scripts/validate-sources.py` — provenance present; every source ref resolves.
- `scripts/validate-artifacts.sh` — required folders and control files present.
- `scripts/generate-manifest.py` — generate or verify SOURCE-MANIFEST.md from
  `state.json`.

## References

- [memory-architecture.md](references/memory-architecture.md) — the four memory
  types, note formats, frontmatter contract, and the retrieval model.
- [crud-and-retrieval.md](references/crud-and-retrieval.md) — capture taxonomy,
  correlation patterns, and the retrieval decision procedure.
- [compiler.md](references/compiler.md) — the four confirmations, the scaffold,
  orientation, the two HARD CHECKPOINTS, the connector gate, the nine-stage
  pipeline, model tiering, the validators, the HARD GATES, and redaction.
- [maintenance.md](references/maintenance.md) — the autonomous loop, its
  guardrails, and when to prefer checkpointed compilation.
