---
name: linear
description: Track and work tasks on Linear — work, personal, and projects — deterministically, with every API call made by a script rather than hand-built GraphQL. Use when the user wants to check Linear, grab or pick up a task by label, start, comment on, or close a Linear issue, file a ticket, see what is on their plate, render a task dashboard, or sync Linear into the Obsidian second brain; or when an agent should autonomously pull a labeled task and work it.
---

Linear is the task layer across work, personal, and projects. The model's job is the judgment — which labeled task to pick up, what the comment should say, when the task is truly done. Every read and write to Linear is mechanical, so it runs through `scripts/linear.py`; the agent never hand-builds GraphQL. The label is the control surface: the agent only touches tasks the user marked for it.

Climb the determinism ladder — the API call, the issue selection, the dashboard, and the second-brain mirror all live in the script; the script's exit code is the verdict. Reads are safe; the writes (comment, state, create) are scoped to the task at hand, and deletion is not supported. The auth, the GraphQL, the state-name resolution, and the config keys live in [the Linear API reference](references/linear-api.md).

## Steps

1. **Resolve the pickup label and the key.** Name the label that marks a task for the agent; the default lives in `skill.linear.label`, read through `skill-config`. Export `LINEAR_API_KEY` (a personal API key, never committed) before any call. This step is done once the label is named and the key is present in the environment.

2. **Grab the next task.** Run `scripts/linear.py next --label <label>` to select the next actionable issue, or `scripts/linear.py list --label <label>` to see the whole set. The script orders by priority and actionable state, so the same board yields the same choice every run. This step is done once one task is selected, or the script reports none.

3. **Claim it.** Run `scripts/linear.py state <ID> "In Progress"` so the board shows the work has started. This step is done once the command confirms the new state.

4. **Do the work, then prove it.** Carry out the task — the judgment the model owns — and route a code change through [appsec](../../engineering/appsec/SKILL.md) before it ships. This step is done once the task's acceptance is met and verified against real output.

5. **Comment the outcome.** Run `scripts/linear.py comment <ID> "<what changed and why>"` to record the result on the issue. This step is done once the command prints the comment URL.

6. **Close or hand off.** Run `scripts/linear.py state <ID> "Done"`, or the review state the team uses. This step is done once the command confirms the state.

7. **Visualize and feed the brain.** Run `scripts/linear.py dashboard` for a Markdown view of what is open across work, personal, and projects, then `scripts/linear.py sync` to mirror the issues into the second brain's `Commitments/` for the Obsidian graph. This step is done once the dashboard renders and sync reports the synced count.

8. **Capture new work anywhere.** Run `scripts/linear.py create "<title>" --team <KEY>` to file a task from a meeting, an idea, or a bug the moment it surfaces. This step is done once the new identifier and its URL print.

## Scripts

`scripts/linear.py` owns every Linear operation. The script runs `--selftest` to assert its parsing, selection, dashboard, and mirror rendering offline, and the repo's selftest gate covers it.

- `list` / `next` / `get` — read issues by label and state (selection is deterministic).
- `comment` / `state` / `create` — the scoped writes (no delete).
- `dashboard` — render a Markdown life/work dashboard.
- `sync` — upsert one mirror note per issue into the vault's `Commitments/`, keyed by identifier (idempotent).

## Configuration

- `LINEAR_API_KEY` — a personal API key, in the environment or a secret manager, never in `skills.toml`.
- `skill.linear.label`, `skill.linear.team` — defaults for `--label` and `--team`, in `skills.toml`.
- `vault.path` — where `sync` writes, shared with the [second brain](../../obsidian/second-brain/SKILL.md).

See also [the determinism doctrine](../../meta/foundation/SKILL.md).

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
