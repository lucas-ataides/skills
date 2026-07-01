# TODO

The single source of truth for what is in flight. One item per line, each phrased
as a checkable outcome. Move finished items to Done; keep the history.

## Now
- [ ] Nothing in flight — 2026-07-01 review landed, tree clean, gate green

## Next
- [ ] Identify the untracked-file reaper (suspect: PostCompact vault agent; brain committed as mitigation)
- [ ] skill-changelog --verify: assert rendered entries match the commit range (kills the manual re-read in git-guardrails step 7)
- [ ] brandkit tokens.py validate: reject hue-named tokens (color.blue-500) so role-naming is a gate, not prose
- [ ] outreach-lint.py: CAN-SPAM/GDPR floor check (unsubscribe link, postal address, real sender) for cold outbound drafts
- [ ] docx: section-vs-archetype validator so a skipped section fails the render, not the eye
- [ ] pdf render.py: pin or record the chosen engine (auto-detect is per-machine non-deterministic)
- [ ] Observe one scheduled 11:00 content-radar run write a radar note end-to-end
- [ ] Wire LINEAR_API_KEY (or OAuth the Linear MCP) and smoke-test the linear skill live
- [ ] Export Cursor rules into an active repo (`skill-cursor <repo>/.cursor/rules --prune`)
- [ ] Audit the quality domain for overlap (verification-before-completion / polish / overdrive / full-output-enforcement)
- [ ] Bootstrap `.brain/` into active repos (pulse, redlens) and draw their real architecture maps

## Done
- [x] 2026-07-01 review: drift gate, cursor --prune, router routes, scaffold protocol line, setup drift, PostCompact dedupe
- [x] Fill and commit this repo's `.brain/` (architecture map + 5 synthesis pages + log)
- [x] Consolidate engineering 47 → 43 (appsec⊃autoguardrails, agent-orchestration, git-guardrails⊃changelog-gen)
- [x] Rename the project brain to `.brain/`; project-context bootstraps it by default
- [x] Second-brain protocol two-way (prime + feed) + alias-aware `vault.sh find`
- [x] skill-cursor: export skills as Cursor .mdc rules
- [x] Rename plugin to ataides-skills; SHA versioning; skill-router hook; marketplaces pruned 997 → 259
