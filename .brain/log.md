# Log

Append-only and parseable — one line per event:
`## [YYYY-MM-DD] <kind> | <summary>`  — kind is decision | ingest | change | risk.

## [2026-06-24] decision | plugin versioning: pinned 0.1.0 → commit SHA, so every push is an update
## [2026-06-25] decision | plugin renamed to ataides-skills; marketplaces pruned 997 → 259 skills
## [2026-06-25] change | skill-router hook ships in the plugin (invoke nudge + second-brain prime)
## [2026-06-25] decision | second-brain protocol goes two-way: prime in, feed out (all skills)
## [2026-06-25] change | vault.sh find made alias-aware after a stress test lost 2/5 notes
## [2026-06-25] decision | consolidation 47 → 43 (see consolidation-2026-06)
## [2026-06-25] change | project brain dir renamed brain/ → .brain/; bootstrap seeds it by default
## [2026-07-01] ingest | brain filled from the full-session review (see review-2026-07-01)
## [2026-07-01] change | drift gate, skill-cursor --prune, router routes, scaffold protocol line
## [2026-07-01] risk | untracked .brain/ deleted twice by an unidentified agent — mitigated by committing it
## [2026-07-01] ingest | all-43 skills deep review: abuse tests passed, 10 prose fixes, git-commit hardened, ruff gates skills/, 5 script features queued
