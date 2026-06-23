# full-output-enforcement

> Enforce complete output — every requested item delivered in full, every file written end to end, no truncation, no placeholders, no stub handed back as done. Use when a deliverable spans many files or items, when output is long enough to tempt an ellipsis, when writing or editing whole files, when enumerating a list, when handing back generated code, or when a prior turn left "// ... rest" / "fill in the rest" / "(repeat for the others)" / a stub presented as finished.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- a deliverable spans many files
- items
- when output is long enough to tempt an ellipsis
- when writing
- editing whole files
- when enumerating a list
- when handing back generated code
- when a prior turn left "//

## What it does

1. List the requested items.
2. Deliver each item in full.
3. Split large output into complete pieces.
4. Scan for banned shortcuts.
5. Count delivered against requested.
6. Verify claimed done equals observed done.
7. Report against the three criteria.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
