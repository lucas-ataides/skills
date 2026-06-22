---
name: creating-skills
description: Author a new skill the deterministic way — scaffold, write to the doctrine, gate, verify, register. Use when the user wants to create, add, scaffold, or write a new skill in this repository, or to convert a process or runbook into a conformant skill.
---

Author a skill that is born conformant. The process is deterministic end to end: a
scaffolder writes a valid skeleton, and the linter gates the result. Spend the saved
judgment on the one stochastic part — the wording of the procedure itself.

The depth of that wording — invocation choice, descriptions, the information hierarchy,
completion criteria, leading words, pruning, and the failure modes — lives in [the
authoring guide](references/authoring-guide.md). Read it before writing the body. See
also the [foundation doctrine](../foundation/SKILL.md), whose rules this skill assumes.

## Steps

1. **Choose the invocation.** Decide model-invoked versus user-invoked from the
   trade-off in [the authoring guide](references/authoring-guide.md#the-invocation-choice):
   model-invoked pays permanent context for unprompted firing; user-invoked is free but
   only the human can summon it. Completion: you have named the invocation and, for
   model-invoked, drafted a description under 500 characters that opens with the job's
   verb and lists "Use when …" triggers.

2. **Scaffold.** Run `make new-skill CATEGORY=<category> NAME=<name>` (which calls
   `skill-new`), adding `--invocation model` for a model-invoked skill. The scaffolder
   writes a lint-clean `skills/<category>/<name>/SKILL.md` and registers the skill.
   Completion: the command prints `created skills/<category>/<name>/SKILL.md`, and that
   file is present.

3. **Write the body.** Replace the scaffold steps with the real procedure, applying the
   information hierarchy and progressive-disclosure rules from [the authoring
   guide](references/authoring-guide.md#the-information-hierarchy): the load-bearing
   steps stay in SKILL.md, and depth moves behind a pointer in `references/`. Prefer a
   script over freehand judgment per the [determinism ladder](../foundation/SKILL.md).
   Completion: each step ends on a checkable, exhaustive completion criterion, and no
   methodology depth remains inlined that a reference should hold.

4. **Gate.** Run `make lint` (which runs `skill-lint --strict skills/`). A finding is a
   red build, not a warning to weigh. Correct the skill, never the linter — a genuinely
   wrong rule earns a new test plus a `rules.yaml` change instead (Kaizen). Completion:
   `skill-lint --strict` prints 0 findings.

5. **Verify scripts.** A skill that ships a script ships a test that fails when the
   logic breaks, per the [script standard](../foundation/references/script-standard.md).
   Run `make test` to exercise the suite. Completion: `make test` exits zero with the new
   test included; a skill with no script may record this step as not applicable.

6. **Confirm registration.** Read `.claude-plugin/plugin.json` and locate the entry the
   scaffolder added (Genchi Genbutsu — verify against the file, never assume).
   Completion: the line `"./skills/<category>/<name>"` is present in that manifest.
