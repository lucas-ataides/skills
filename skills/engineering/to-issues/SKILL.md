---
name: to-issues
description: Turn a conversation, plan, or pile of notes into well-formed, independently-shippable tracker issues (GitHub or Linear) — each with an outcome title, context, and acceptance criteria. Use when the user asks to write issues, file tickets, break a plan or feature into tasks, "make GitHub/Linear issues", or convert a discussion or spec into a backlog.
---

A raw request becomes a backlog only after someone names the discrete work, writes acceptance criteria, and cuts the oversized pieces into shippable slices. This skill does that conversion. The output is *drafts* — a tracker write happens only at step 6, only with explicit approval.

A well-formed issue states an outcome, carries the context to act on cold, and ends on criteria that prove it is done. See [the anatomy of a great issue](references/issue-anatomy.md) for the full standard, the splitting heuristic, the labeling taxonomy, and a worked example.

Climb the determinism ladder: the spec validation and the exact creation command live in `scripts/to-issues.py`, never in prose. The judgment — what work, what criteria, what split — is the last rung, and the agent keeps only that.

## Steps

1. **Gather the source.** Collect the conversation, plan, spec, or notes the issues come from into one place. Name the tracker (GitHub or Linear) and read its existing labels and priorities so drafts match the house taxonomy. Done when the source text and the target tracker are both fixed.

2. **Identify the discrete work.** List each separable unit of work the source implies as a one-line candidate. Merge duplicates; drop anything already shipped or out of scope. Done when every candidate names one outcome and no two candidates overlap.

3. **Draft each issue into the spec.** Per candidate, write title-as-outcome, context (the why), acceptance criteria, scope and non-goals, dependencies, and a size estimate into a JSON spec entry (`title`, `body`, `acceptance`, `labels`, `assignee`), following [issue-anatomy.md](references/issue-anatomy.md). Done when no drafted issue is missing acceptance criteria.

4. **Split the oversized.** A draft that cannot ship in one focused pass gets cut into vertical slices, each independently shippable per the splitting heuristic in [issue-anatomy.md](references/issue-anatomy.md). Done when no remaining draft fails the "finishable in one sitting" bar.

5. **Label and link.** Apply type, priority, and area labels from the taxonomy read at step 1, then record dependency and parent-child links between the drafts. Done when every draft carries a type label, a priority, and its stated links.

6. **Validate the spec deterministically.** Run `scripts/to-issues.py check <spec.json>`. The script rejects any issue missing a title or acceptance criteria, so a malformed draft never reaches the tracker. Done when the check exits zero.

7. **Confirm, then create through the script.** Present the numbered drafts and ask the user to approve, edit, or reject. Preview the exact commands with `scripts/to-issues.py create <spec.json> --dry-run`. On explicit approval, create them with `scripts/to-issues.py create <spec.json>` — the script renders each body and acceptance checklist identically every run and shells to `gh` only for the approved set. Done when the script reports each issue created, or the user declined and no write ran.

## Scripts

`scripts/to-issues.py` owns the deterministic remainder. The script runs `--selftest` to assert its validation and command-building, and the repo's selftest gate covers it.

- `check <spec.json>` — validate the spec against the issue anatomy (boundary check).
- `create <spec.json> [--dry-run]` — build the exact `gh issue create` argv and run it (or print it under `--dry-run`).

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
