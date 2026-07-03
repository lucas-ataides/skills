# Linear through the MCP

The depth behind [the skill](../SKILL.md). Every Linear read and write goes through the
Linear MCP — an OAuth-authorized server exposing typed tools — never a raw HTTP call and
never an API key. The MCP owns auth, retries, and the schema; the agent owns the judgment;
the rules below keep the judgment deterministic.

## Connecting and authorizing

- The server connects once per environment: in Claude Code via `/mcp` (OAuth flow) or
  `claude mcp add`, in claude.ai via the connector settings. A non-interactive session
  cannot run the OAuth flow — the skill stops and hands the user that instruction.
- Tool names vary by server (an official Linear MCP, a workspace plugin, or a gateway), so
  the agent discovers the tools with a ToolSearch for `linear` and maps them by operation,
  never by memorized name.

## The operation map

| Need | MCP operation (discover the exact tool) |
|---|---|
| Find work by label | list/search issues, filtered by label and state |
| Read one task | get issue (title, description, state, priority, comments, URL) |
| Claim / close | update issue state |
| Record the outcome | create comment on the issue |
| File new work | create issue (title, team, label) |
| Board overview | list issues, then render the dashboard shape below |
| Team's state names | list the team's workflow states |

Deletion is out of scope by policy: the agent never deletes a Linear issue, comment, or
label through the MCP, whatever tools the server exposes. Deletion stays in the Linear UI,
done by a human.

## The deterministic selection rule

The same board must yield the same "next task" every run:

1. Candidates: issues carrying the pickup label, in unstarted or started workflow states.
2. Order by priority — Urgent, then High, then Medium, then Low, with priority-less issues
   last. (Linear encodes priority as 1=Urgent, 2=High, 3=Medium, 4=Low, 0=None: ascending
   numeric order with 0 moved to the end.)
3. Ties break to the oldest `createdAt`.
4. The first issue wins. An empty candidate list is reported plainly — never invent a task.

## State names

Workflow states are per-team and renameable, so "In Progress" and "Done" are conventions,
not constants. Read the team's states through the MCP first, then use the exact name from
the started category to claim, and the completed category to close, or the review state
where the team gates on review.

## The dashboard shape

Render the overview in one fixed shape so every run reads the same:

```markdown
# Linear dashboard (label: <label>)
**Total:** <n>
**By state:** <state>: <n> · <state>: <n> · …
**By priority:** Urgent: <n> · High: <n> · Medium: <n> · Low: <n> · None: <n>

| ID | Title | State | Priority | Assignee |
|---|---|---|---|---|
```

Issues sort by the selection rule above, so the table order is stable between runs.

## The vault mirror

A worked issue is mirrored into the second brain through the vault helper — the
deterministic write path — never by hand-writing a note:

```sh
skills/obsidian/second-brain/scripts/vault.sh capture task "<ID>: <title>" \
  status=<state> url=<issue-url>
```

The capture lands in `Commitments/`, keyed by the identifier in the title, with the URL
back to the live issue as the source of truth. Re-working the same issue appends to the
existing note with `vault.sh append` rather than capturing a duplicate.

## Failure modes

- **No Linear MCP connected** — stop with the authorize instruction; never fall back to a
  raw API call or ask for an API key.
- **Label matches nothing** — report the empty board; do not widen the filter silently.
- **State name rejected** — the team renamed its states; re-read the workflow states and
  retry with the exact name.
- **Two agents, one board** — claim (move to started) before working, so a second agent's
  selection rule skips the issue.
