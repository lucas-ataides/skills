---
name: linear
description: Track and work tasks on Linear through the Linear MCP — always the MCP, never a hand-built API call or a stored key — check the board, grab the next labeled task, claim it, work it, comment the outcome, move its state, and mirror a dashboard into the vault. Use when the user wants to check Linear, grab or work a Linear task or ticket, comment on or close an issue, file a task, see what is next or in flight, or sync Linear into the second brain. Requires a connected Linear MCP (OAuth).
---

Linear is the task layer across work, personal, and projects. The model's job is the judgment — which labeled task to pick up, what the comment should say, when the task is truly done. Every read and write to Linear goes through **the Linear MCP, always**: OAuth-authorized, tool-typed, no API key in any environment, no hand-built GraphQL. The label is the control surface — the agent only touches tasks the user marked for it — and deletion is never performed through the MCP, whatever tools the server exposes.

The exact tool names vary by server, so the agent discovers them rather than hardcoding: the operation map, the deterministic selection rule, the state-name resolution, and the vault-mirror format live in [the Linear MCP reference](references/linear-mcp.md).

## Steps

1. **Confirm the MCP is connected.** Search the session's tools for the Linear MCP (a ToolSearch for `linear` — issue list/get/update and comment operations). When no Linear MCP is connected or the server still needs OAuth, stop and hand the user the fix — authorize it via `/mcp` in an interactive session, or the claude.ai connector settings — then resume on the next run. This step is done once the Linear tools are callable, or the run has stopped with that instruction.

2. **Resolve the pickup label.** Name the label that marks a task for the agent; the default lives in `skill.linear.label`, read through `skill-config`. This step is done once the label is named.

3. **Select the next task deterministically.** List the issues carrying the label in unstarted or started states, then apply the fixed rule from [the reference](references/linear-mcp.md) — Urgent before High before Medium before Low with priority-less last, ties to the oldest created — so the same board yields the same choice every run. This step is done once one issue is named, or the empty result is reported plainly rather than filled by invention.

4. **Claim it.** Read the team's exact state names through the MCP (teams rename their workflow states), then update the issue to its started state (commonly "In Progress"). This step is done once the MCP confirms the new state.

5. **Do the work, then prove it.** Carry out the task — the judgment the model owns — and route a code change through [appsec](../../engineering/appsec/SKILL.md) before it ships. This step is done once the task's acceptance is met and verified against real output per [verification-before-completion](../../quality/verification-before-completion/SKILL.md).

6. **Comment the outcome, then close.** Record what changed and why as an issue comment through the MCP, then move the issue to the team's done state, or its review state where the team gates on review. This step is done once the comment exists on the issue and the MCP confirms the final state.

7. **Visualize and feed the brain.** For a dashboard, list the open issues and render counts by state and priority in the fixed shape the reference names. Mirror the worked issue into the vault with the second brain's `vault.sh capture task "<ID>: <title>" status=<state> url=<issue-url>`, so the Obsidian graph carries the commitment. This step is done once the capture prints the note path, or the user declined the mirror.

8. **Capture new work anywhere.** File a task from a meeting, an idea, or a bug the moment it surfaces by creating the issue through the MCP with a title, the team, and the label. This step is done once the new identifier and its URL come back from the MCP.

## Configuration

- **Auth is the MCP's OAuth** — owned by the connected server. No `LINEAR_API_KEY`, nothing in the environment, nothing in `skills.toml`.
- `skill.linear.label`, `skill.linear.team` — defaults for the pickup label and the team, in `skills.toml`.
- `vault.path` — where the mirror lands, shared with the [second brain](../../obsidian/second-brain/SKILL.md).

See also [the determinism doctrine](../../meta/foundation/SKILL.md).

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
