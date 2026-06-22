---
name: least-code
description: Write the least code that fully works — climb the subtraction ladder and stop at the first rung that holds before adding anything new. Use when the user wants to simplify, cut scope, delete code, avoid over-engineering, kill a premature abstraction, or review a change for unnecessary complexity.
---

The best code is the code never written. Every line is a liability someone reads, tests, debugs, and carries forever — so the discipline is subtraction: reach for new code only after nothing simpler covers the requirement in full. Cleverness is not the goal; the smallest thing that works and survives a 3am page is.

Subtraction is YAGNI turned into a procedure. Climb the ladder rung by rung, and stop at the first rung that holds.

## The ladder

Each rung ends on a checkable condition. Stop at the first rung whose condition is met; the rungs below it are the answer.

1. **Does this need to exist?** Delete the requirement before writing for it. A need is real when a current user or a committed contract demands it — a speculative one is dropped, and the one-line reason sits in the commit message or the ticket.
2. **Does the standard library cover it?** A stdlib call ships, is documented, and is already trusted. Reach for it before any third-party name.
3. **Does a native platform feature cover it?** A database constraint, an HTTP-framework guard, a language built-in — a platform primitive beats a dependency that re-implements it.
4. **Does an installed dependency solve it?** A package already in the lockfile costs nothing new. Use the existing one before adding a fresh supply-chain edge.
5. **Can it be one expression?** A single readable expression beats a helper, a class, or a config layer. Write the one line when one line is clear.
6. **The last rung — minimum code that works.** Write the smallest implementation that satisfies the requirement in full, carve-outs included, and no further.

Work each rung against [the subtraction reference](references/subtraction.md), which expands every rung with a before/after, defines the carve-outs, fixes the comment convention, and walks one over-engineered snippet down to size.

## The carve-outs — never simplify these away

Four things stay in at every rung. Brevity is never the reason to cut them, because their absence is silent until production bites.

1. **Input validation at trust boundaries.** Validate external data — request bodies, CLI args, file contents, API responses — before any work runs on it.
2. **Error handling that prevents data loss.** A partial write, a swallowed exception, or an unchecked failure on a destructive path stays handled.
3. **Security controls.** Authorization checks, output encoding, and parameterized queries are load-bearing, not boilerplate.
4. **Accessibility basics.** A role, an accessible name, and keyboard operation per interactive element survive every cut.

The check: confirm each carve-out relevant to the change is present after the simplification, not before.

## The check

Non-trivial logic leaves one runnable check behind — the smallest test that fails when the logic breaks. A deliberate shortcut carries a comment that names the ceiling it stops at and the upgrade path past it, so the next reader inherits the decision instead of re-deriving it. See [the subtraction reference](references/subtraction.md) for the comment convention and the failure modes that ignoring it produces.

See also: [the determinism doctrine](../../meta/foundation/SKILL.md).
