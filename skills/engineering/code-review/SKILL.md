---
name: code-review
description: Review a change as a tech lead — against intent and architecture, not only line-level correctness — gates first, then judgment. Use when the user asks to review code, a diff, a PR, or a design.
---

Review the change the way a tech lead does: judge it against what it must deliver and how it fits the system, not only whether the lines are locally correct. Mechanical correctness is the floor; the leverage is in delivery, architecture, and conceptual integrity.

Run the deterministic gates first, then spend judgment on what no tool can see.

## Steps

1. **Recover intent.** State what the change must deliver: the requirement, the ticket, or the architectural decision it implements. A review without intent checks correctness against nothing — so name the intent before reading a line.

2. **Run the gates.** Run `skill-gate --strict` at the repo root. Record each failing gate as a finding; a green gate needs no comment. The gates own formatting, lint, types, SAST, SCA, secrets, and tests.

3. **Review through the lenses.** Work the change against [the review lenses](references/review-lenses.md), top-weighted first: delivery, architecture, conceptual integrity, abstraction, then correctness, security, tests, operability. Each lens yields a finding or an explicit pass.

4. **Judge the abstraction.** Name the abstraction level the change chose and whether it fits the problem. Over-abstraction (a framework for one caller) and under-abstraction (a concept copied four times) are both findings.

5. **Weigh the trade-offs.** State what the change traded — complexity, coupling, performance, time — and whether the trade earns the intent. A silent trade-off is itself the finding.

6. **Rank and report.** Label each finding blocker, major, or minor, tied to the lens it failed and the intent it endangers. The review is done when every changed file and every lens has a verdict.

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md, task list, and project brain (brain.md) current.

The gates in step 2 are the [appsec](../appsec/SKILL.md) pipeline — a code change clears appsec before it merges.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
