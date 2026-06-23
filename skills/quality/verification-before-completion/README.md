# verification-before-completion

> Never declare work done without observing that it is done — claimed-done must equal observed-done. Use when about to report a task finished, a bug fixed, a feature working, a file written, tests passing, or a build green; when tempted to write "it should work", "this will fix it", or "done" without running anything; when handing back code, a UI change, or a doc; or when a prior turn asserted success with no command output to back it.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- about to report a task finished
- a bug fixed
- a feature working
- a file written
- tests passing
- a build green; when tempted to write "it should work"
- "this will fix it"
- "done" without running anything; when handing back code
- a UI change
- a doc;
- when a prior turn asserted success with no command output to back it

## What it does

1. Name the completion claim and its output type.
2. Pick the verification method for that type.
3. Run it and capture the real output.
4. Read the output against the claim.
5. Scale the verification to the cost of being wrong.
6. Reject stale or assumed evidence.
7. Report the claim with its evidence attached.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
