---
name: project-management
description: Run a project the way a tech lead and founder does — a lightweight project record in the Obsidian second brain, with honest milestones, tracked tasks, logged risks and decisions, and a status cadence. Use when planning or running a job or personal project, setting up a project record, breaking a goal into milestones, tracking tasks or WIP, writing a status update (changed / next / blocked), logging a risk or decision, or correlating a project to people, companies, and commitments in the vault.
---

Run a project the way a working tech lead and founder does: a single project record carries goal, scope, milestones, status, owner, risks, decisions, and next actions, and the record lives in the Obsidian second brain so the project correlates with the people, companies, and commitments around it. The system serves the work — the lightest record that keeps the project honest wins.

Note CRUD is not this skill's job. Reads, writes, links, and frontmatter go through [second-brain](../../obsidian/second-brain/SKILL.md); this skill decides *what* the project record must contain and *when* the state changes.

The depth bar, the failure modes, and a worked example live in [references/pm-system.md](references/pm-system.md). Read that reference before running a project for the first time.

## Steps

1. **Define the project record.** Create one project note holding goal (the outcome in one sentence), scope (in and out), the owner, and the current status — `vault.sh capture project "<name>" owner=<owner> company=<company> cadence=weekly` sets those fields at capture through [second-brain](../../obsidian/second-brain/SKILL.md). The goal names a result a reader can test, not an activity. The step is done when the project note states a testable goal plus an explicit out-of-scope line.

2. **Break the goal into milestones and tasks.** Split the goal into 3–7 milestones, each with a date and a done-condition, then split the nearest milestone into tasks that each carry one acceptance criterion. Estimate against past actuals, not hope; mark every dependency and the longest dependent chain (the critical path). The step is done when each near-term task has an acceptance criterion and the critical path is named in the note.

3. **Track work on a cadence.** Hold work-in-progress under the stated WIP limit, move a task forward only when its acceptance criterion is met, and record the state on a fixed cadence (weekly is the default). The step is done when open tasks sit at or below the WIP limit and the last cadence entry carries the current date.

4. **Log risks and decisions as they surface.** Record each material risk with a likelihood, an impact, and an owner; capture each material decision in a decision note linked from the project via [second-brain](../../obsidian/second-brain/SKILL.md). A risk without an owner does not count as logged. The step is done when every open risk has an owner and every decision since the last review is linked.

5. **Report status as changed / next / blocked.** Write the status update in three parts — what changed since last report, what is next, what is blocked — and tie each blocker to the risk or decision it traces to. A status update that omits blockers is status theater. The step is done when the update names what changed, what is next, and the blockers (or states "none blocked").

6. **Correlate the project in the vault.** Link the project note to the people, companies, and commitments it touches via [second-brain](../../obsidian/second-brain/SKILL.md), so a query across the vault surfaces this project beside related work. The step is done when the project links to at least its owner and one company-or-commitment note, and the link resolves.

7. **Verify the record against the checklist.** Confirm the project passes the completion checklist in [references/pm-system.md](references/pm-system.md): testable goal, explicit scope, dated milestones, acceptance-tagged tasks, a current cadence entry, owned risks, linked decisions, a changed/next/blocked update, and vault links that resolve. The step is done when every checklist line holds or carries a dated, owned exception.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
