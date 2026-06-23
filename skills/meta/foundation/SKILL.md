---
name: foundation
description: The determinism doctrine every skill in this repo inherits. Read before authoring or running any skill. Invoke with /foundation.
disable-model-invocation: true
---

Every skill in this repository inherits the rules below. The root virtue is **predictability**: the agent takes the same *process* every run. A skill earns its place by removing ambiguity, not by being clever.

## The determinism ladder

Climb until a rung holds, then stop:

1. A script or existing tool can do the work — call it. The output is deterministic and free of agent judgment.
2. A linter or schema can validate the work — gate on it.
3. A deterministic primitive exists for the operation — use `skillkit`, never improvise the file operation in prose.
4. Only the irreducibly stochastic part is left — hand that, and only that, to the model.

Push as much work down the ladder as the task allows. The model is the last resort, not the first rung.

## Non-negotiable rules

`skill-lint` enforces every rule below. The patterns live in `tools/skill_lint/rules.yaml` — the single source of truth — and the reasoning is in [references/ambiguity-rules.md](references/ambiguity-rules.md).

- **Anchored references.** A sentence cannot open with a bare pronoun standing in for its subject. Name the noun.
- **Bounded scope.** A step cannot range over an open set with the unbounded quantifiers (the "for-each" family). <!-- skill-lint: allow SK020 --> Name the exact set, or pass it to a script that enumerates it.
- **Shallow branching.** One conditional per sentence. Split each branch into its own step, or move the decision into a script.
- **Guarded destruction.** A destructive command is never inlined. Call a guarded helper so the dangerous path is impossible, not merely discouraged.
- **Collision-free creation.** A new file takes its name from `skillkit.unique_path`, never a hand-rolled timestamp. The kernel guarantees uniqueness; the agent does not.
- **Checkable completion.** Every step ends on a condition the agent can observe. Vague imperatives ("make sure", "as needed") are banned. <!-- skill-lint: allow SK060 -->

## The deterministic primitives

Skills call `skillkit` instead of describing a file operation in prose:

- `unique_path` / `unique_id` — collision-free names.
- `atomic_write` — a reader never sees a half-written file.
- `safe_remove` — refuses anything outside its root, refuses the root itself, never recurses.

## Subtraction — the least code that works

The best code is the code never written. Before adding, climb the subtraction ladder and stop at the first rung that holds: does this need to exist at all; does the standard library cover it; does a native platform feature cover it; does an installed dependency solve it; can it be one line. New code earns its place only past those rungs. This principle is imbued in every skill; the full ladder, the never-simplify-away carve-outs (validation, data-loss safety, security, accessibility), and worked examples live in [references/subtraction.md](references/subtraction.md).

## Feed the second brain

When a vault is configured (`skill-config path`), a skill records its salient outcome on the way out — a decision made, a fact learned, a task closed — through the [second-brain](../../obsidian/second-brain/SKILL.md) capture at the configured vault path. The feed is opt-out: on by default, skipped silently when no vault is set, and the agent judges what is worth keeping. When the value of recording is unclear, it asks before writing. Configuration (the vault path, the feed toggle, per-skill settings) lives in `skills.toml` and is read through `skillkit.config`.

## Japanese quality principles

The doctrine is grounded in manufacturing discipline, mapped to concrete mechanics in [references/japanese-principles.md](references/japanese-principles.md):

- **Poka-yoke** — make the mistake structurally impossible (guarded helpers, the scaffolder).
- **Jidoka** — stop the line on a defect (the linter blocks the commit and the build).
- **Genchi Genbutsu** — verify by observing real output, never by assumption.
- **Kaizen** — every new ambiguity becomes a new rule and a new test.
- **Kanso** — eliminate the superfluous; the shortest skill that works wins.

## The gate

`make lint` runs `skill-lint --strict skills/`. The same gate runs in pre-commit and in CI. A violation is a red build, not a warning to weigh.

## Going deeper

- [references/determinism.md](references/determinism.md) — why determinism, and the DSL / linter strategy.
- [references/script-standard.md](references/script-standard.md) — how every skill script must be written.
- [GLOSSARY.md](GLOSSARY.md) — the leading words this doctrine thinks in.
