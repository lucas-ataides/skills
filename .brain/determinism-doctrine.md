---
title: "Determinism doctrine"
type: concept
updated: 2026-07-01
sources: ["skills/meta/foundation/SKILL.md", "tools/skill_lint/rules.yaml"]
---

# Determinism doctrine

The root virtue is **predictability**: the same process every run. The LLM does only what it
is good at — thinking; every deterministic step is offloaded to a script, linter, or
primitive. The doctrine is enforced, not aspirational: `skill-lint` blocks the commit and the
build on a violation.

**The ladder** (stop at the first rung that holds): script/tool → linter/schema →
deterministic primitive (`skillkit`) → only the irreducibly stochastic part goes to the model.
Determinism is also token-efficiency: a script replaces generated output with a one-line
verdict.

**The lint-enforced rules:** anchored references (no sentence-initial bare pronoun), bounded
scope (no unbounded for-each), shallow branching (one conditional per sentence), guarded
destruction (never inline rm — `skillkit.safe_remove`), collision-free creation
(`unique_path`), checkable completion (no "make sure"/"as needed").

**Japanese principles → mechanics:** Poka-yoke = guarded helpers and the scaffolder; Jidoka =
red gate stops the line; Genchi Genbutsu = verify by running, never by assumption; Kaizen =
every new ambiguity becomes a rule + test; Kanso = the shortest skill that works.

The doctrine paid for itself repeatedly: the `trends.py` selftest caught a ranking bug
(weighted sum let 2000 likes beat 160 saves — inverted intent); the selftest gate caught a
`SystemExit` abort in a brain helper; the alias-aware `find` fix shipped with a permanent
regression assertion.

## Related
- [[toolchain]] · [[architecture]] · [[second-brain-protocol]]
