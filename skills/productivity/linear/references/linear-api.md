# Linear API reference

The depth behind [the linear skill](../SKILL.md). Every Linear operation is mechanical
and lives in `scripts/linear.py`, so the agent calls a subcommand and branches on the
exit code — it never composes GraphQL by hand. This page documents the auth, the config,
each operation's query, the agent-label workflow, the second-brain mirror, and the
failure modes.

## Authentication

- **Endpoint**: `https://api.linear.app/graphql` (POST, `Content-Type: application/json`).
- **Header**: a personal API key goes in the `Authorization` header **directly** —
  `Authorization: <key>`, with **no `Bearer` prefix** (that prefix is for OAuth tokens
  only). This is the most common Linear integration mistake.
- The script reads the key from `LINEAR_API_KEY`. It is a credential: keep it in the
  environment or a secret manager, never in `skills.toml` or a note. The repo's
  secret-scan gate is the backstop, not the first line.

## Configuration

`scripts/linear.py` resolves defaults through `skill-config` when a flag is omitted, so an
agent can run `linear.py next` with no arguments once these are set:

```toml
# skills.toml
[skill.linear]
label = "agent"      # the pickup label for autonomous work
team  = "ENG"        # default team key for `create`

[vault]
path = "/path/to/Obsidian/Second Brain"   # where `sync` writes
```

Resolution order for each value: the explicit flag, then the `skill-config` key, then an
error. Same pattern the second brain's `vault.sh` uses, so configuration lives in one file.

## The agent-label workflow

The label is the control surface. The user marks a task for the agent by adding the
pickup label (default `agent`) in Linear; the agent only ever touches labeled tasks. A
typical autonomous loop:

1. `linear.py next --label agent` — pick the next actionable issue (priority-ordered).
2. `linear.py state ENG-123 "In Progress"` — claim it on the board.
3. do the work; for code, pass [appsec](../../../engineering/appsec/SKILL.md).
4. `linear.py comment ENG-123 "Shipped X; see PR #45."` — record the outcome.
5. `linear.py state ENG-123 "Done"` — close or move to review.

Because selection (`next`) is deterministic — actionable state, then priority, then
identifier — the same board always yields the same pick, so two runs never fight over
which task is "next."

## Operations and their GraphQL

| Subcommand | GraphQL | Notes |
| --- | --- | --- |
| `list` / `next` | `issues(filter: {labels:{name:{eq}}, state:{name:{eq}}})` | `next` filters to actionable states (unstarted/backlog/triage) and sorts by priority |
| `get <ID>` | `issues(filter: {team:{key:{eq}}, number:{eq}})` | resolves the human identifier `ENG-123` to the issue |
| `comment <ID>` | `commentCreate(input: {issueId, body})` | `issueId` is the resolved UUID |
| `state <ID> <name>` | `workflowStates(filter:{team:{key:{eq}}})` → `issueUpdate(id, input:{stateId})` | resolves the state **name** to its id within the issue's team |
| `create <title>` | `teams(filter:{key:{eq}})` → `issueCreate(input:{teamId,title,labelIds})` | resolves the team key and label name to ids |

Identifiers like `ENG-123` are split into a team key and a number, then resolved to the
UUID through a `team.key` + `number` filter — robust regardless of how Linear's `issue(id)`
convenience behaves.

## State names

`state` matches the workflow-state **name** case-insensitively against the issue's team
(e.g. `"In Progress"`, `"Done"`, `"In Review"`, `"Todo"`, `"Backlog"`). Names vary per
team; when a name does not match, the script prints the team's available state names so the
caller can correct it. The actionable set `next` draws from is the state **type**
(`unstarted`, `backlog`, `triage`), which is stable across teams.

## Visualization and the second brain

- **Dashboard** — `linear.py dashboard [--label L]` renders a deterministic Markdown
  summary: totals, a breakdown by state and by priority, and a table of open items.
  Redirect it into a vault note to read the live picture inside Obsidian.
- **Sync** — `linear.py sync [--label L]` writes one mirror note per issue into the vault's
  `Commitments/`, named by identifier (`eng-123.md`) so re-syncing updates in place rather
  than duplicating. Each note carries `type: task`, `linear:`, `state`, `priority`, and a
  `## Sources` link back to the live issue, so the issues join the Obsidian graph and the
  [second brain](../../../obsidian/second-brain/SKILL.md) reads Linear as part of one memory.

The split is the doctrine: Linear is the source of truth for task state; the vault is the
durable, linkable memory; the dashboard is the at-a-glance view. The script keeps all three
consistent without the model transcribing anything by hand.

## Failure modes

| Failure | Symptom | Guard |
| --- | --- | --- |
| Bearer-prefixed key | every call returns 401 | personal keys use the raw `Authorization: <key>` header |
| Key in a note or `skills.toml` | a credential is committed | `LINEAR_API_KEY` env only; the secret-scan gate is the backstop |
| Wrong team's state name | `state` reports "no state '<name>'" | the script lists the team's real state names |
| Re-sync duplicates notes | two notes for one issue | mirror filename is keyed by identifier; the upsert is idempotent |
| Agent works an unlabeled task | scope creep | `next`/`list` filter by the pickup label; the agent only sees labeled work |
| Hand-built GraphQL drift | inconsistent reads | the field selection and filters live in one script, identical every run |
