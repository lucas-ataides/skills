---
title: "Plugin distribution and runtime integration"
type: system
updated: 2026-07-01
sources: [".claude-plugin/marketplace.json", "hooks/hooks.json", "hooks/skill-router.sh"]
---

# Plugin distribution and runtime integration

Public repo `github.com/lucas-ataides/skills`, installed as the Claude Code plugin
**`ataides-skills`** (invoke as `ataides-skills:<skill>`). Naming history:
ldatb-skills → lucas-ataides-skills → ataides-skills; the Python package stays
`lucas-ataides-skills-tools`.

**SHA versioning (postmortem).** The original `marketplace.json` pinned `version: 0.1.0`, so
`/plugin update` always reported "already at latest" — skills looked "not called natively"
while the installed copy was stale. Fix: no version field → every commit is an update. The
drift test now asserts the pin never returns. Update flow after every push:
`claude plugin marketplace update ataides-skills && claude plugin update
ataides-skills@ataides-skills`, then **restart** (no hot reload).

**The invocation problem and the router.** Skills are model-invoked *suggestions*; with ~1000
installed skills (15 marketplaces) they lost the competition. Two-part fix: pruned
marketplaces 997 → 259 skills, and shipped `hooks/skill-router.sh` (UserPromptSubmit) — a
POSIX-sh keyword router that injects "invoke `ataides-skills:<x>`" plus the second-brain
prime nudge on matching prompts. Deterministic insurance, not enforcement: the model still
chooses, the user's words still win. Selftested and gated.

**Cursor path.** `skill-cursor <project>/.cursor/rules` exports each SKILL.md as an
"Agent Requested" rule (`description` + `alwaysApply: false`) — the same trigger model as
Claude Code. Rules bake machine-specific source paths, so they are generated per machine,
never committed; `--prune` (marker-guarded) removes rules whose skill was merged away.
Hooks do not port to Cursor; the rule body carries the protocol text instead.

**Cross-tool floor.** `project-context.sh bootstrap` writes AGENTS.md (skills directive +
`.brain/` pointer) + TODO.md + seeded `.brain/` — read by both Claude Code and Cursor.

## Related
- [[architecture]] · [[toolchain]] · [[consolidation-2026-06]]
