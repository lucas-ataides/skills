---
title: "Second-brain protocol"
type: concept
updated: 2026-07-01
sources: ["skills/meta/foundation/SKILL.md", "skills/obsidian/second-brain/scripts/vault.sh"]
---

# Second-brain protocol

Every skill works against the configured Obsidian vault in **both directions** — "a real
second brain that feeds and reads itself":

- **Prime (read, on the way in):** `vault.sh find "<subject>"` → follow `## Related` /
  `## Sources`. Read-only; an empty result is reported, never invented.
- **Feed (write, on the way out):** capture the salient outcome (decision, fact, closed
  task). Agent judges worth; asks when unclear.

Both opt-out, silent when no vault is configured. Vault resolution: `$VAULT` env →
`skill-config path` → `./vault`. Configured vault:
`~/Library/Mobile Documents/com~apple~CloudDocs/Obsidian/Second Brain`. The router hook
reinforces the prime on every matched prompt.

**Token economics (the design constraint):** `find` returns *paths only* — the agent reads
only the hits, never the vault. Deterministic cheap read; LLM-judged write.

**Alias-aware find (stress-test finding, 2026-06-25):** plain substring grep lost 2 of 5
notes for a customer named three ways (IndySoft / Indy Soft / ISoft). Fix: pass 1 substring →
pass 2 widens by the matched notes' `name:`/`aliases:` frontmatter. 5/5 on every spelling,
decoy excluded, regression-asserted in the selftest. Boundary that remains: undeclared
aliases, typos, and bare pronouns are invisible — the discipline is declaring aliases on the
entity note and keeping `## Related` links.

**Two brains, one pattern (Karpathy LLM-wiki):** the personal vault (cross-project, entities,
daily notes) and the per-repo [[architecture]] wiki in `.brain/` (index + architecture map +
log + synthesis pages). Same rules: index first, synthesis not restatement, contradictions
flagged with source, append-only parseable log.

## Related
- [[determinism-doctrine]] · [[architecture]] · [[review-2026-07-01]]
