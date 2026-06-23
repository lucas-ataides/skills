# The compiler

Build the vault the way a build system compiles source: raw sources go in one
end, source-backed canonical notes come out the other, and deterministic
validators gate the result. This is the *compile* capability — distinct from
fast hand capture ([crud-and-retrieval.md](crud-and-retrieval.md)) and from the
autonomous loop ([maintenance.md](maintenance.md)). This page holds the
orientation phase, the two HARD CHECKPOINTS, the connector-verification gate, the
resumable state contract, the nine-stage pipeline, the smoke pass, the validator
scripts, the validation HARD GATES, and the redaction policy. Preserve every
safety element here exactly — they are the difference between a trustworthy memory
and an invented one.

Two rules dominate the whole compile — never invent a fact a source does not
support, and never ship a copied secret. The depth bar is
[code-review](../../../engineering/code-review/SKILL.md): mechanical correctness is
the floor, conceptual integrity is the leverage. The change discipline — orient,
gate, never mutate externally without approval — is the
[git-guardrails](../../../engineering/git-guardrails/SKILL.md) posture applied to
memory. The memory model and note formats live in
[memory-architecture.md](memory-architecture.md).

## Orientation and HARD CHECKPOINT 1

Broad ingestion never begins until the user approves a plan. Orientation produces
that plan and stops for sign-off:

1. **Resume check.** Look for `state.json` and `INGESTION-LOG.md` at the
   configured vault path. On a resume, read both before any other action, then
   continue from `current_phase` and `next_actions`.
2. **Confirm the four, then inspect.** Before any substantive read, confirm the
   working directory, the output root, the source locations, and each connector's
   connected account. Enumerate available sources — working-directory
   files, pasted text, and the connectors the user named — and record the source
   inventory.
3. **Scaffold the vault.** Run `scripts/scaffold.py <output-root>` to lay the
   canonical folders, the six control files, the `state.json` schema, and a
   self-contained `_tools/` (the validators copied in, so the vault re-validates on
   its own). The default output root is
   `Compiled-Vaults/compiled-vault-brain-<date>/` under the working directory; an
   existing vault may be the root, to compile in place. The scaffold never
   overwrites an existing file.
4. **Verify accounts before proposing.** Per external connector, capture which
   account and workspace it is signed into. A connector signed into the wrong
   account is recorded as a blocker, not a source.
5. **Write the orientation report.** Produce `Reports/ORIENTATION-REPORT.md`
   holding the working directory, output root, source and connector inventory,
   account verification, the proposed compilation plan, and any blockers.
6. **HARD CHECKPOINT 1 — pause for approval.** Present the orientation report and
   stop. Broad ingestion waits until the user approves, amends, or rejects the
   plan.

## The connector-verification gate

A connector is the gated doorway through which external sources enter, and the
gate runs *before* the first read:

- **Record every connector before a read.** Per connector, write a
  SOURCE-MANIFEST.md block with `id`, `account`, `workspace`, `verified`,
  `timestamp`, `capability` (read-only for compilation), and `approval`. Run
  `scripts/generate-manifest.py --vault <path> --verify` to confirm the contract;
  the script's exit code is the verdict.
- **Block a wrong-account connector.** A connector whose account does not match
  the user's intended account stays blocked — no read, no ingestion — until the
  mismatch is resolved.
- **Reads only, no external mutation.** Compilation reads sources. An external
  write (sending mail, editing a Notion page, creating a calendar event) is out
  of scope and needs separate, explicit per-action approval.

## Resumable state

The compile is resumable and gated. Progress is journaled after every batch so a
crashed or paused run resumes from the last checkpoint:

- **`state.json`** holds `output_path`, `current_phase`, `completed_phases`,
  `sources_discovered`, `sources_ingested`, `connector_status`,
  `batches_completed`, `canonical_notes_created`, `validation_status`,
  `next_actions`, and `blockers`. Write it back atomically so a reader never sees
  a half-written file.
- **`INGESTION-LOG.md`** is the append-only companion: one entry per batch naming
  the source compiled, the notes created and rewritten, and the validator result
  verbatim. Append, never rewrite.
- The discipline is strict — read both first each batch, write both back each
  batch. A crash mid-batch loses at most one batch's progress.

## The nine-stage pipeline

Each source batch flows through these stages in order. A stage consumes the prior
stage's output and produces a checkable artifact.

1. **Parse.** Read the raw source into structured units — messages, emails,
   paragraphs, rows. Strip transport noise (signatures, quoted reply chains,
   boilerplate). Output: clean text units, each tagged with its source id and
   position. Checkable: every unit traces to a source id.
2. **Thread / group.** Cluster units that belong together — a mail thread, a
   chat conversation, a document section. Memory is built from conversations, not
   isolated lines. Output: coherent groups. Checkable: no orphan units outside a
   group.
3. **Classify.** Label each group by entity type (person, company, decision,
   preference, …) and the candidate entities it names. Output: each group tagged
   with a type and a candidate-entity list. Checkable: every group has a type or
   an explicit "no canonical content" mark.
4. **Extract.** Pull the atomic claims from each group: subject, predicate,
   object, and the source span that supports it. "Ada → prefers → async standups
   [span 14–18]." Output: a claim list with spans. Checkable: every claim cites a
   span; no claim without a source.
5. **Canonicalize.** Resolve each candidate entity to a single canonical identity
   (see "Entity canonicalization" below). Merge duplicates; pick the canonical
   name; collect aliases. Output: a map from mentions to canonical entities.
   Checkable: no two canonical entities share a normalized name.
6. **Rehydrate provenance.** Per claim, write or update the matching source trace
   note under `Sources/`, and record the connector in SOURCE-MANIFEST.md if not
   already present. Output: source notes exist for every claim's origin.
   Checkable: `validate-sources.py` finds no unresolved ref.
7. **Author.** Write the canonical note: frontmatter, body claims with
   confidence, provenance section. When the canonical note already exists,
   **update it** — append new claims and new provenance, raise confidence where a
   second source corroborates — never create a duplicate. Output: canonical notes
   written via atomic write. Checkable: one note per canonical entity.
8. **Validate links.** Resolve every `[[wikilink]]` to a real note. Fix or flag
   unresolved and ambiguous links. Output: a wikilink report. Checkable:
   `validate-wikilinks.py` exits 0.
9. **Critic / audit.** A separate pass re-reads each new note against its sources
   and asks: is every claim supported? Any invented fact? Any secret copied? Any
   confidence overstated? Output: COMPLETION-AUDIT.md. Checkable: the audit lists
   zero unsupported claims and zero copied secrets.

## Entity canonicalization and dedup

The hardest stage. "Ada", "Ada Lovelace", "A. Lovelace", and "the Countess" must
collapse to one note; "Apple the company" and "apple the fruit" must not.

- **Normalize for matching.** Casefold, trim, and strip honorifics to form a
  match key. `validate-slugs.py` uses the same casefold so the on-disk filename
  and the match key agree.
- **Alias capture, not renaming.** When a new mention matches an existing entity,
  add it to that note's `aliases` — never rename the note. Obsidian resolves
  links through aliases, so every historical reference keeps working.
- **Type guards the merge.** Two mentions merge only when they share an entity
  type. A person named "Apple" never merges into the company.
- **Ambiguity is surfaced, not guessed.** When a mention could be two entities
  and the sources do not disambiguate, the compiler writes the claim under the
  more specific match and flags it for the critic pass — never a silent pick.
- **Update over duplicate.** Stage 7 reads the existing note first. A second
  source for an existing claim raises its confidence and appends a provenance
  line rather than spawning a second note.

## Model tiering

The [foundation](../../../meta/foundation/SKILL.md) determinism ladder says: push
work down to scripts, hand the model only the irreducibly stochastic part. Within
the model work, tier by difficulty to control cost without losing quality:

- **Cheap / fast model — parse, thread, classify, extract.** High-volume,
  low-judgment, structurally constrained. The output is checkable (spans, types),
  so a cheaper model's errors are caught downstream.
- **Strong model — canonicalize, author, critic.** Identity resolution, prose
  authoring, and the adversarial audit need the strongest reasoning. The critic
  pass must be a strong model and must be a *separate* invocation from the author,
  so it never rubber-stamps its own work.
- **No model — validate.** Stage 8 and the gates are scripts. Determinism owns the
  verdict; the model never decides whether a link resolves.

## Smoke pass and HARD CHECKPOINT 2

The bulk never lands before a representative slice is approved:

1. **Compile a representative slice.** From Tier 0 and Tier 1 sources only,
   compile a small representative sample across entity types — at least one
   canonical note per major type.
2. **HARD CHECKPOINT 2 — show the sample, then pause.** Present sample canonical
   notes, one source trace from claim to source, one context pack, the
   SOURCE-MANIFEST.md, and the validation report. Stop. Broad ingestion waits
   until the user approves the sample.

### Ingestion tiers

Sources are ingested cheapest-signal and lowest-risk first, so the checkpoint
after the smoke pass reviews a representative slice before the bulk lands:

1. **Tier 0 — local, already-present sources.** Working-directory files, pasted
   text, exports the user already handed over. No connector, no external call.
   Always first.
2. **Tier 1 — verified read-only connectors.** Gmail, Notion, Calendar, and
   similar, each gated through SOURCE-MANIFEST.md with account verified and
   read-only capability confirmed. Read, never write.
3. **Tier 2 — broad connector sweeps.** Larger historical pulls (full mailbox,
   whole workspace) run only after the Tier 1 smoke pass is approved at HARD
   CHECKPOINT 2.
4. **Tier 3 — derived and cross-source synthesis.** Context packs and Maps of
   Content, built once enough canonical notes exist to stitch together.

## The validator scripts

A script runs `--selftest` to build temp fixtures, assert, and exit 0. Each is
read-only against the vault except `generate-manifest.py --generate`. A script's
exit code is the verdict — branch on the code, not on its prose:

- `scripts/validate-wikilinks.py` — resolve `[[wikilinks]]`; report unresolved
  and ambiguous.
- `scripts/validate-slugs.py` — empty filenames, invalid paths, duplicate slugs,
  unsafe chars.
- `scripts/scan-secrets.py` — credential-shaped strings, reported masked for
  redaction.
- `scripts/validate-sources.py` — provenance present; every source ref resolves.
- `scripts/validate-artifacts.sh` — required folders and control files present.
- `scripts/generate-manifest.py` — generate or verify SOURCE-MANIFEST.md from
  `state.json`.

Record each validator's result in `VALIDATION-REPORT.md` — every validator named
with its pass-or-fail verdict.

## The validation HARD GATES

A compile is complete only when all of the conditions below hold. A red gate
blocks completion: fix the cause, re-run the validator, re-check.

- 0 placeholder source refs — the placeholder-ref class of `validate-sources.py`
  is empty.
- 0 broken wikilinks; 0 ambiguous wikilinks left unresolved.
- 0 empty slugs; 0 invalid paths (no `People/.md`); 0 duplicate slugs.
- 0 copied secrets reported by the secret scan.
- Provenance present on each promoted canonical note.
- Each connector documented in SOURCE-MANIFEST.md with a verified account.
- `README.md`, `VALIDATION-REPORT.md`, `COMPLETION-AUDIT.md`, `INGESTION-LOG.md`,
  and `state.json` exist.
- The vault opens as a normal Obsidian folder of plain Markdown.

Then write `COMPLETION-AUDIT.md`: the gate results, the count of canonical notes
and sources, and any residual low-confidence claims, with every gate recorded as
held and the validators green.

## Redaction policy

The vault is compiled from the exact places live secrets leak from, so redaction
is a hard gate, not a courtesy:

- **Never copy a secret.** API keys, tokens, private keys, passwords,
  bearer/OAuth tokens, database URLs with inline credentials, SSH keys,
  webhook/signing secrets, and session cookies are never written to a note.
  `scan-secrets.py` is the backstop; the author is the first line.
- **Summarize sensitive content, never paste it.** A source note records *what a
  source says*, not a verbatim dump. Personal data (home address, medical detail,
  private financial figures) is summarized to the minimum the memory needs, or
  omitted.
- **Mark sensitivity.** Every source-derived note carries a `sensitivity` field.
  A `restricted` note names the constraint ("share only with the named party").
- **Redact in place with a marker.** Where a quoted line would carry a secret,
  the secret is replaced by `[REDACTED: <kind>]` so the structure survives and the
  omission is visible.

## Failure modes

| Failure | Symptom | Guard |
|---------|---------|-------|
| Invented fact | A claim with no supporting span | Stage 4 span requirement; critic pass; `validate-sources.py` |
| Duplicate entity | `Ada.md` and `Ada Lovelace.md` both exist | Stage 5 canonicalization; `validate-slugs.py` duplicate class |
| Copied secret | An API key sits in a source note | Redaction policy; `scan-secrets.py` hard gate |
| Broken graph | A `[[wikilink]]` resolves to nothing | `validate-wikilinks.py` unresolved class |
| Placeholder provenance | A `source:` field shipped with a stub value | `validate-sources.py` placeholder-ref class |
| Wrong-account connector | Vault built from the wrong mailbox | Connector gate; `generate-manifest.py --verify` |
| Confidence inflation | One source, marked `high` | Critic pass re-reads sources against confidence |
| Lost resumability | A crash mid-batch loses progress | `state.json` + `INGESTION-LOG.md` updated per batch |

## Red flags

- A canonical note with no `## Sources` section and no `sources:` frontmatter.
- A note that reads more confidently than its single low-confidence source.
- A second note for an entity that already has one — a dedup miss.
- A source trace that quotes a credential, an OTP, or a full home address.
- A connector read before its SOURCE-MANIFEST.md block exists.
- A "smoke pass" that ingested the whole mailbox instead of a representative
  slice.
- A critic pass run by the same invocation that authored the notes.

## Worked example: compiling one person from one source

**Source:** a Gmail thread, captured as `Sources/gmail-2026-06-ada-thread.md`,
sensitivity `personal`.

1. **Parse** — strip the reply chain and signature; keep three message bodies,
   each tagged `gmail-2026-06-ada-thread:msg-N`.
2. **Thread** — the three messages form one group (subject "Standup cadence").
3. **Classify** — type `person`; candidate entities: "Ada", "Charles".
4. **Extract** — claim `Ada → prefers → async standups`, span `msg-1:14–18`;
   claim `Charles → agrees`, span `msg-2:3–6`.
5. **Canonicalize** — "Ada" matches existing `People/Ada Lovelace.md` (alias
   "Ada" already present). "Charles" matches `People/Charles Babbage.md`. No new
   entities; no duplicates created.
6. **Rehydrate** — the source note already exists; confirm `gmail-personal` sits
   in SOURCE-MANIFEST.md with account verified and read capability.
7. **Author** — open `People/Ada Lovelace.md`. The async-standup claim is new and
   now has a *second* source, so its confidence rises `low → high` and a
   provenance line is appended. The note is rewritten via atomic write. No
   duplicate note is created.
8. **Validate links** — `[[Charles Babbage]]` and `[[Analytical Engine]]` both
   resolve; `validate-wikilinks.py` exits 0.
9. **Critic** — a separate strong-model pass confirms: both claims supported by
   cited spans, no invented facts, no secret in the source note, confidence now
   justified by two independent sources. COMPLETION-AUDIT.md records the note as
   clean.

Result: one updated canonical note, one confirmed source trace, one manifest
entry, and a green run from all six validators — no duplication, full provenance,
no invented facts.
