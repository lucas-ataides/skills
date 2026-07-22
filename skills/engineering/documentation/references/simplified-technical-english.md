# Simplified Technical English (ASD-STE100) for the docs this skill writes

ASD-STE100 — Simplified Technical English — is the aerospace industry's controlled language
for maintenance documentation: a small set of writing rules plus a one-word-one-meaning
dictionary. The reason it fits here: documentation written under STE is unambiguous for a
tired human at 3 a.m. and for an agent parsing it — the same reader this repo's determinism
doctrine serves. The skill applies STE to **the documentation it writes and reconciles**
(READMEs, guides, API prose); SKILL.md files keep the repo's own house style under
`skill-lint`.

`scripts/ste-lint.py` owns the mechanical rules; the judgment rules below are the agent's.
This page is a distillation in the spirit of the specification, not a reproduction of it —
the official specification is issued by ASD and is available from asd-ste100.org.

## The mechanical rules — the script's verdict

| Rule | Limit | Why |
|---|---|---|
| STE01 | A sentence has at most 25 words; write procedures toward 20 | Short sentences carry one idea each |
| STE02 | A paragraph has at most 6 sentences | One topic per paragraph |
| STE03 | No passive voice | The actor is explicit; instructions name who does what |
| STE04 | No perfect tenses (has/have/had + participle) | Simple present, past, and future only |
| STE05 | No word from the unapproved list | One word, one meaning; the short common verb wins |
| STE06 | No gerund opener | An instruction starts with the imperative verb |

The unapproved→approved list lives as data in `ste-lint.py` (`UNAPPROVED`), curated in the
STE dictionary's spirit: `utilize`→use, `commence`→start, `terminate`→stop, `perform`→do,
`in order to`→to, `prior to`→before, and the rest. Grow the list one pair at a time as new
offenders appear (Kaizen); the script is the single source of truth.

## The judgment rules — the agent's discipline

The script cannot hold these; the writer must:

- **One instruction per sentence.** "Remove the cover and disconnect the pump" is two
  instructions — write two sentences, or a numbered list with one action per item.
- **One word, one meaning, everywhere.** Pick one term per concept and keep it: a config
  file is "the config file" in every sentence, never "the settings file" two pages later.
- **Keep the articles.** Write "install the driver", never the telegraphic "install driver".
- **Break noun clusters.** More than three nouns in a row ("the vault manifest verifier
  exit code") unpacks into a phrase with prepositions ("the exit code of the manifest
  verifier").
- **Warnings come first.** A warning or caution is its own short sentence before the
  instruction it protects, and it starts with the hazard, not the background.
- **Prefer vertical lists** for sequences: one numbered item per action, in the order the
  reader acts.

## Before and after

Before (23-word passive soup):

> The configuration file should have been updated by the administrator prior to the service
> being restarted in order to facilitate the migration.

After (STE):

> Update the config file before you restart the service. This change makes the migration
> possible.

## Scope and the escape hatch

STE governs prose. Code blocks, inline code, tables, headings, and frontmatter are out of
scope, and `ste-lint.py` skips them. A quoted error message or a required proper term stays
verbatim inside backticks, where the linter does not look — that is the escape hatch for
text the writer does not control.
