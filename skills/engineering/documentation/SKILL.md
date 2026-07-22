---
name: documentation
description: Keep documentation in sync with code and hold its prose to Simplified Technical English (ASD-STE100) — detect link drift deterministically with skill-docs, reconcile the prose a tool cannot write, then gate it with ste-lint. Run after every code change. Use when the user changes code, renames or moves a file, updates a public API, edits a README or guide, asks to verify, refresh, or audit the docs, or wants docs in STE or simplified technical English.
---

Docs drift the moment code moves and the prose stays still. A doc that lies is worse than no doc: a reader trusts it, acts on it, and fails in a way the missing doc never would have caused. This skill catches the drift a tool can prove, then reconciles the prose a tool cannot.

Run the deterministic link check first. Spend judgment on what the check cannot see — stale signatures, dead examples, an out-of-date README. The kinds of drift, which are tool-checkable, what to update per change, and a worked rename live in [doc drift](references/doc-drift.md).

The prose this skill writes follows **Simplified Technical English (ASD-STE100)**: short sentences, one instruction each, active voice, simple tenses, one word per meaning. The mechanical rules are `scripts/ste-lint.py`'s verdict; the judgment rules — and why STE fits agent-read docs — live in [the STE reference](references/simplified-technical-english.md).

## Steps

1. **Name what changed.** State the changed surface: the renamed file, the edited signature, the new flag, or the behavior that moved. A sync without a named change checks docs against nothing, so name the change before reading a page. This step is done when the changed surface is written down.

2. **Detect link drift.** Run `skill-docs` at the repo root. The output lists each repo-relative Markdown link and file reference that no longer resolves, with its line number; a non-zero exit blocks the change. This step is done when the broken-target list is captured.

3. **Repair the references.** Retarget each broken link from step 2 to the moved or renamed path. Rerun `skill-docs` per repair until it exits zero. This step is done when `skill-docs` reports no broken targets.

4. **Reconcile the prose in STE, then gate it.** Walk the named set from [doc drift](references/doc-drift.md) — the README, the public API reference, the affected guides — against the changed surface. A page that describes the old behavior is rewritten to state the new, written to [the STE rules](references/simplified-technical-english.md). Then run `scripts/ste-lint.py check <the touched pages>` and fix each printed violation at its line. This step is done when every page in that set states current behavior and `ste-lint.py check` exits zero on the touched pages.

5. **Re-run the examples.** Execute each documented code example against the current code; a snippet that imports a moved module or calls a renamed symbol is dead and gets rewritten. This step is done when every example runs without error.

6. **Regenerate the reference.** Where the stack ships a doc generator (typedoc, godoc, sphinx), run it so the generated reference matches the current signatures. This step is done when the generator exits clean and its output is committed. A stack with no doc generator skips the run, and the step is then done by recording that no generated reference exists.

7. **Record and verify.** Run `skill-docs` once more, then hand the user-visible change to [git-guardrails](../git-guardrails/SKILL.md) for its CHANGELOG entry. This step is done when the link check exits zero and the changelog records the change.

## Scripts

`scripts/ste-lint.py` owns the mechanical STE verdict, so the agent never re-checks a sentence length, a tense, or a banned word by eye. The script runs `--selftest`, and the repo's selftest gate covers it.

- `check <file.md> [file.md ...]` — check Markdown prose against the six mechanical rules (sentence and paragraph caps, passive voice, perfect tense, the unapproved-word list, gerund openers). Code fences, inline code, headings, tables, and frontmatter are skipped. Each violation prints as `file:line: [RULE] message`; exit is zero when the set is clean, nonzero on any violation.

See also: [the foundation doctrine](../../meta/foundation/SKILL.md).

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md, task list, and project brain current.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
