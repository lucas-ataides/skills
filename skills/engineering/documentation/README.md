# documentation

> Keep documentation in sync with code and hold its prose to Simplified Technical English (ASD-STE100) — detect link drift deterministically with skill-docs, reconcile the prose a tool cannot write, then gate it with ste-lint. Run after every code change. Use when the user changes code, renames or moves a file, updates a public API, edits a README or guide, asks to verify, refresh, or audit the docs, or wants docs in STE or simplified technical English.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- changes code
- renames
- moves a file
- updates a public API
- edits a README
- guide
- asks to verify
- refresh
- audit the docs
- wants docs in STE
- simplified technical English

## What it does

1. Name what changed.
2. Detect link drift.
3. Repair the references.
4. Reconcile the prose in STE, then gate it.
5. Re-run the examples.
6. Regenerate the reference.
7. Record and verify.

## Scripts

- `scripts/ste-lint.py`

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
