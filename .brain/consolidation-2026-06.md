---
title: "Consolidation 2026-06: 47 → 43 skills"
type: decision
updated: 2026-07-01
sources: ["commit 0ce966f", "commit f84e167"]
---

# Consolidation 2026-06: 47 → 43 skills

Engineering had grown to 14 skills with real duplication. Merged where responsibilities
genuinely overlapped; deliberately kept apart where triggers or callers differ.

| merged | into | rationale |
|---|---|---|
| autoguardrails | appsec (step 4) | the POLICY.md scanner is one of appsec's gates |
| agent-loop + subagent-driven-development | agent-orchestration | one job, two patterns: iterate-to-done (loop) and fan-out (parallel, owned-file invariant) |
| bootstrap (skill) | project-context | thin wrapper over `project-context.sh bootstrap`, which already triggers on it |
| changelog-gen | git-guardrails (steps 6–7) | the changelog is generated from commits — a release/git operation |

Engineering 14 → 10; total 47 → 43.

**What stayed apart, and why (the anti-mega-skill rule):** `tdd`, `code-review`,
`software-architecture` are **shared primitives** — each has ≥2 callers (`engineering` and
`agent-orchestration`/the brain map) and its own sharp trigger. Folding them into
`engineering` would couple callers to the whole lifecycle and blunt the description that
makes model-invocation fire. DRY applies to duplication, not to distinct triggers.

**Follow-ups from the merge:** empty dir husks lingered after `git mv` + `git rm` (git does
not delete emptied directories) — cleaned; the manifest kept dead entries — now impossible
(drift gate). The project brain dir was renamed `brain/` → `.brain/` (meta-dir convention,
still committable) and `project-context` step 2 now defaults to `bootstrap`, so the brain is
created for every repo, not only fresh ones.

Open candidate: the quality domain (verification-before-completion / polish / overdrive /
full-output-enforcement) smells of the same overlap — unaudited.

## Related
- [[plugin-distribution]] · [[architecture]] · [[review-2026-07-01]]
