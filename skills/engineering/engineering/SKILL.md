---
name: engineering
description: Build and change software end to end — app code, infrastructure, and tests — design judged first, built test-first, shipped behind the gates. Use when the user implements a feature, edits code, builds an API or UI, changes infrastructure, or writes tests.
---

Build software that fits the system and delivers the requirement, across application code, infrastructure, and the tests that prove it. Judge the design before writing code, build test-first, and ship behind the gates. The hard part is rarely the code — it is choosing the right seam, guarding the blast radius, and proving the change does what was asked.

Keep the project legible as you work: maintain its AGENTS.md/CLAUDE.md and task list via [project-context](../project-context/SKILL.md).

## Steps

1. **State the requirement.** Write what the change must deliver and the acceptance criteria that decide done. Code measured against nothing cannot be reviewed.

2. **Design the seam.** Name the boundary the change lives behind: the interface, the data shape, the dependency direction. Check it against [engineering practices](references/engineering-practices.md) before writing code; a wrong seam is expensive to move later.

3. **Build test-first.** Follow [tdd](../tdd/SKILL.md): a failing test per stated behavior, then the minimum code that passes. Layer the tests by [the test strategy](references/test-strategy.md): unit for logic, integration for boundaries, end-to-end for the critical path.

4. **Validate at the boundary.** Reject malformed or unauthorized input before any work runs. Untrusted data is checked at the edge, not deep in the call stack.

5. **Change infrastructure behind a plan.** For an infrastructure change, follow [infra safety](references/infra-safety.md): validate, scan, read the plan, and name the blast radius before any mutation. A teardown runs only against a named, non-production target with recorded approval.

6. **Finish the user-facing edges.** For a UI change, cover the loading, empty, and error states and the accessibility checklist. For an API change, cover the error contract, pagination, and idempotency.

7. **Gate and verify.** Pass the [appsec](../appsec/SKILL.md) gate — every code change, app or infra, runs `skill-gate --strict` through that skill's fixed order — then confirm each acceptance criterion against the running change. The work is done when every criterion passes and the appsec gate is green.

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md, task list, and project brain (brain.md) current.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
