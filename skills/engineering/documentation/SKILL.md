---
name: documentation
description: Keep documentation in sync with code — detect link drift deterministically with skill-docs, then reconcile the prose a tool cannot write. Run after every code change. Use when the user changes code, renames or moves a file, updates a public API, edits a README or guide, or asks to verify, refresh, or audit the docs.
---

Docs drift the moment code moves and the prose stays still. A doc that lies is worse than no doc: a reader trusts it, acts on it, and fails in a way the missing doc never would have caused. This skill catches the drift a tool can prove, then reconciles the prose a tool cannot.

Run the deterministic link check first. Spend judgment on what the check cannot see — stale signatures, dead examples, an out-of-date README. The kinds of drift, which are tool-checkable, what to update per change, and a worked rename live in [doc drift](references/doc-drift.md).

## Steps

1. **Name what changed.** State the changed surface: the renamed file, the edited signature, the new flag, or the behavior that moved. A sync without a named change checks docs against nothing, so name the change before reading a page. This step is done when the changed surface is written down.

2. **Detect link drift.** Run `skill-docs` at the repo root. The output lists each repo-relative Markdown link and file reference that no longer resolves, with its line number; a non-zero exit blocks the change. This step is done when the broken-target list is captured.

3. **Repair the references.** Retarget each broken link from step 2 to the moved or renamed path. Rerun `skill-docs` per repair until it exits zero. This step is done when `skill-docs` reports no broken targets.

4. **Reconcile the prose.** Walk the named set from [doc drift](references/doc-drift.md) — the README, the public API reference, the affected guides — against the changed surface. A page that describes the old behavior is rewritten to state the new. This step is done when every page in that set states current behavior.

5. **Re-run the examples.** Execute each documented code example against the current code; a snippet that imports a moved module or calls a renamed symbol is dead and gets rewritten. This step is done when every example runs without error.

6. **Regenerate the reference.** Where the stack ships a doc generator (typedoc, godoc, sphinx), run it so the generated reference matches the current signatures. This step is done when the generator exits clean and its output is committed.

7. **Record and verify.** Run `skill-docs` once more, then hand the user-visible change to [changelog-gen](../changelog-gen/SKILL.md) for its CHANGELOG entry. This step is done when the link check exits zero and the changelog records the change.

See also: [the foundation doctrine](../../meta/foundation/SKILL.md).

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md, task list, and project brain (brain.md) current.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
