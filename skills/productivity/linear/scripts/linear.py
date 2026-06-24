#!/usr/bin/env python3
"""Deterministic Linear client — the agent decides, this script does every API call.

The model's job is judgment: which labeled task to pick up, what to write in a comment,
when a task is done. Every Linear read and write is mechanical, so it lives here behind
a fixed interface — the agent never hand-builds GraphQL. Reads are safe; writes (comment,
state, create) are scoped to the task at hand. The GraphQL, the auth, and the parsing are
identical every run.

    linear.py list   [--label L] [--state S] [--json]   issues with a label (and state)
    linear.py next   [--label L]                         the next actionable labeled issue
    linear.py get    <ID>                                one issue, full detail
    linear.py comment <ID> "<body>"                      add a comment
    linear.py state  <ID> "<state name>"                 move to a workflow state
    linear.py create "<title>" --team KEY [--label L] [--desc D]
    linear.py dashboard [--label L]                      a Markdown life/work dashboard
    linear.py sync   [--label L] [--vault PATH]          mirror issues into the second brain
    linear.py --selftest

Auth: export LINEAR_API_KEY (a personal API key). Defaults for --label / --team / --vault
come from `skill-config` (skill.linear.label, skill.linear.team, vault.path) when omitted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.linear.app/graphql"

PRIORITY_NAMES = {0: "None", 1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}

# The field selection used for every issue read, so a parsed issue has a stable shape.
ISSUE_FIELDS = """
  id identifier title description url priority
  state { name type }
  labels { nodes { name } }
  assignee { displayName }
"""

_IDENTIFIER = re.compile(r"^([A-Za-z0-9]+)-(\d+)$")


# --- pure helpers (no network; the selftest covers these) -------------------


def parse_identifier(identifier: str) -> tuple[str, int] | None:
    """Split a human identifier like 'ENG-123' into ('ENG', 123); None if malformed."""
    m = _IDENTIFIER.match(identifier.strip())
    if not m:
        return None
    return m.group(1).upper(), int(m.group(2))


def build_issue_filter(label: str | None, state: str | None) -> dict:
    """Build the GraphQL IssueFilter for a label and/or workflow-state name."""
    f: dict = {}
    if label:
        f["labels"] = {"name": {"eq": label}}
    if state:
        f["state"] = {"name": {"eq": state}}
    return f


def parse_issues(data: dict) -> list[dict]:
    """Normalize the GraphQL issues payload into flat dicts with a stable shape."""
    nodes = (data.get("issues") or {}).get("nodes") or []
    out: list[dict] = []
    for n in nodes:
        out.append(
            {
                "id": n.get("id"),
                "identifier": n.get("identifier"),
                "title": n.get("title") or "",
                "description": n.get("description") or "",
                "url": n.get("url") or "",
                "priority": n.get("priority") or 0,
                "state": (n.get("state") or {}).get("name") or "",
                "state_type": (n.get("state") or {}).get("type") or "",
                "labels": [x["name"] for x in ((n.get("labels") or {}).get("nodes") or [])],
                "assignee": (n.get("assignee") or {}).get("displayName") or "",
            }
        )
    return out


def select_next(issues: list[dict]) -> dict | None:
    """Pick the next actionable issue: an unstarted/backlog/triage state, highest priority.

    Linear priority 1=Urgent … 4=Low, 0=None. A 0 sorts last. Ties break on identifier so
    the choice is deterministic for a given board state.
    """
    actionable = [i for i in issues if i["state_type"] in ("unstarted", "backlog", "triage")]

    def key(i: dict) -> tuple[int, str]:
        p = i["priority"]
        return (p if p and p > 0 else 5, i["identifier"] or "")

    return sorted(actionable, key=key)[0] if actionable else None


def render_table(issues: list[dict]) -> str:
    """Render issues as a Markdown table, deterministically ordered."""
    if not issues:
        return "_no issues_\n"
    rows = ["| ID | Title | State | Priority | Assignee |", "| --- | --- | --- | --- | --- |"]
    for i in sorted(issues, key=lambda x: x["identifier"] or ""):
        title = i["title"].replace("|", "\\|")
        rows.append(
            f"| {i['identifier']} | {title} | {i['state']} | "
            f"{PRIORITY_NAMES.get(i['priority'], '?')} | {i['assignee'] or '—'} |"
        )
    return "\n".join(rows) + "\n"


def render_dashboard(issues: list[dict], label: str | None) -> str:
    """Render a deterministic Markdown dashboard: counts by state and priority, then a table."""

    def tally(field: str) -> str:
        counts: dict[str, int] = {}
        for i in issues:
            counts[i[field]] = counts.get(i[field], 0) + 1
        return " · ".join(f"{k or '—'}: {counts[k]}" for k in sorted(counts)) or "—"

    prio = {}
    for i in issues:
        name = PRIORITY_NAMES.get(i["priority"], "?")
        prio[name] = prio.get(name, 0) + 1

    scope = f" (label: {label})" if label else ""
    lines = [
        f"# Linear dashboard{scope}",
        "",
        f"**Total:** {len(issues)}",
        "",
        f"**By state:** {tally('state')}",
        "",
        "**By priority:** " + (" · ".join(f"{k}: {prio[k]}" for k in sorted(prio)) or "—"),
        "",
        "## Open items",
        "",
        render_table([i for i in issues if i["state_type"] != "completed"]),
    ]
    return "\n".join(lines)


def mirror_filename(identifier: str) -> str:
    """Stable filename for an issue's mirror note, keyed by its identifier (idempotent)."""
    return identifier.lower().replace("/", "-") + ".md"


def render_mirror_note(issue: dict) -> str:
    """Render the second-brain mirror note for one issue: frontmatter + body + back-link."""
    labels = ", ".join(issue["labels"]) if issue["labels"] else ""
    fm = [
        "---",
        "type: task",
        f"linear: {issue['identifier']}",
        f"state: {issue['state']}",
        f"priority: {PRIORITY_NAMES.get(issue['priority'], '?')}",
        "tags: [task, linear]",
    ]
    if labels:
        fm.append(f'labels: "{labels}"')
    fm += ["source_status: source-backed", "---", ""]
    body = [
        f"# {issue['identifier']}: {issue['title']}",
        "",
        issue["description"] or "_no description_",
        "",
        "## Sources",
        f"- [Linear]({issue['url']}) — the live issue (source of truth).",
        "",
    ]
    return "\n".join(fm + body)


# --- network I/O (isolated; the selftest never reaches here) -----------------


def _config(dotted: str) -> str | None:
    try:
        out = subprocess.run(
            ["skill-config", "get", dotted], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return None
    val = out.stdout.strip()
    return val if out.returncode == 0 and val else None


def _api(query: str, variables: dict | None = None) -> dict:
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        print("linear: set LINEAR_API_KEY (a personal API key) in the environment", file=sys.stderr)
        raise SystemExit(3)
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Authorization": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(
            f"linear: HTTP {exc.code} from the API: {exc.read().decode('utf-8', 'replace')[:300]}",
            file=sys.stderr,
        )
        raise SystemExit(4) from exc
    except urllib.error.URLError as exc:
        print(f"linear: cannot reach the Linear API: {exc.reason}", file=sys.stderr)
        raise SystemExit(4) from exc
    if body.get("errors"):
        print(f"linear: GraphQL error: {json.dumps(body['errors'])[:400]}", file=sys.stderr)
        raise SystemExit(5)
    return body["data"]


def resolve_uuid(identifier: str) -> str:
    """Resolve a human identifier (ENG-123) to its UUID via a team-key + number filter."""
    parsed = parse_identifier(identifier)
    if not parsed:
        print(
            f"linear: not a valid identifier (expected like ENG-123): {identifier}", file=sys.stderr
        )
        raise SystemExit(2)
    key, number = parsed
    q = "query($k:String!,$n:Float!){issues(filter:{team:{key:{eq:$k}},number:{eq:$n}},first:1){nodes{id}}}"
    nodes = (_api(q, {"k": key, "n": number}).get("issues") or {}).get("nodes") or []
    if not nodes:
        print(f"linear: no issue {identifier}", file=sys.stderr)
        raise SystemExit(6)
    return nodes[0]["id"]


def fetch_issues(label: str | None, state: str | None) -> list[dict]:
    q = f"query($f:IssueFilter,$n:Int){{issues(filter:$f,first:$n){{nodes{{{ISSUE_FIELDS}}}}}}}"
    data = _api(q, {"f": build_issue_filter(label, state), "n": 100})
    return parse_issues(data)


def fetch_issue(identifier: str) -> dict:
    parsed = parse_identifier(identifier)
    if not parsed:
        print(f"linear: not a valid identifier: {identifier}", file=sys.stderr)
        raise SystemExit(2)
    key, number = parsed
    q = (
        f"query($k:String!,$n:Float!){{issues(filter:{{team:{{key:{{eq:$k}}}},"
        f"number:{{eq:$n}}}},first:1){{nodes{{{ISSUE_FIELDS}}}}}}}"
    )
    issues = parse_issues(_api(q, {"k": key, "n": number}))
    if not issues:
        print(f"linear: no issue {identifier}", file=sys.stderr)
        raise SystemExit(6)
    return issues[0]


def add_comment(identifier: str, body: str) -> str:
    uuid = resolve_uuid(identifier)
    q = (
        "mutation($id:String!,$b:String!){commentCreate(input:{issueId:$id,body:$b})"
        "{success comment{url}}}"
    )
    data = _api(q, {"id": uuid, "b": body})
    if not data["commentCreate"]["success"]:
        print("linear: comment failed", file=sys.stderr)
        raise SystemExit(7)
    return data["commentCreate"]["comment"]["url"]


def set_state(identifier: str, state_name: str) -> str:
    parsed = parse_identifier(identifier)
    if not parsed:
        print(f"linear: not a valid identifier: {identifier}", file=sys.stderr)
        raise SystemExit(2)
    key, _ = parsed
    sq = "query($k:String!){workflowStates(filter:{team:{key:{eq:$k}}}){nodes{id name}}}"
    states = (_api(sq, {"k": key}).get("workflowStates") or {}).get("nodes") or []
    match = next((s for s in states if s["name"].casefold() == state_name.casefold()), None)
    if not match:
        names = ", ".join(s["name"] for s in states)
        print(f"linear: no state '{state_name}' in team {key}. States: {names}", file=sys.stderr)
        raise SystemExit(6)
    uuid = resolve_uuid(identifier)
    mq = "mutation($id:String!,$s:String!){issueUpdate(id:$id,input:{stateId:$s}){success}}"
    if not _api(mq, {"id": uuid, "s": match["id"]})["issueUpdate"]["success"]:
        print("linear: state change failed", file=sys.stderr)
        raise SystemExit(7)
    return match["name"]


def create_issue(title: str, team_key: str, desc: str | None, label: str | None) -> dict:
    tq = "query($k:String!){teams(filter:{key:{eq:$k}}){nodes{id}}}"
    teams = (_api(tq, {"k": team_key}).get("teams") or {}).get("nodes") or []
    if not teams:
        print(f"linear: no team with key {team_key}", file=sys.stderr)
        raise SystemExit(6)
    inp: dict = {"teamId": teams[0]["id"], "title": title}
    if desc:
        inp["description"] = desc
    if label:
        lq = "query($n:String!){issueLabels(filter:{name:{eq:$n}}){nodes{id}}}"
        labels = (_api(lq, {"n": label}).get("issueLabels") or {}).get("nodes") or []
        if labels:
            inp["labelIds"] = [labels[0]["id"]]
    mq = "mutation($i:IssueCreateInput!){issueCreate(input:$i){success issue{identifier url}}}"
    data = _api(mq, {"i": inp})
    if not data["issueCreate"]["success"]:
        print("linear: create failed", file=sys.stderr)
        raise SystemExit(7)
    return data["issueCreate"]["issue"]


def _vault(flag: str | None) -> Path:
    root = flag or _config("vault.path")
    if not root:
        print(
            "linear: no vault path (pass --vault or set vault.path via skill-config)",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return Path(root)


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def sync(label: str | None, vault_flag: str | None) -> int:
    """Mirror labeled issues into the vault's Commitments/ as idempotent task notes."""
    vault = _vault(vault_flag)
    issues = fetch_issues(label, None)
    folder = vault / "Commitments"
    for issue in issues:
        _atomic_write(folder / mirror_filename(issue["identifier"]), render_mirror_note(issue))
    print(f"linear: synced {len(issues)} issue(s) into {folder}")
    return 0


# --- subcommands ------------------------------------------------------------


def cmd_list(args) -> int:
    label = args.label or _config("skill.linear.label")
    issues = fetch_issues(label, args.state)
    print(json.dumps(issues, indent=2) if args.json else render_table(issues), end="")
    return 0


def cmd_next(args) -> int:
    label = args.label or _config("skill.linear.label")
    chosen = select_next(fetch_issues(label, None))
    if not chosen:
        print("linear: no actionable issue for that label")
        return 0
    print(json.dumps(chosen, indent=2))
    return 0


def cmd_get(args) -> int:
    print(json.dumps(fetch_issue(args.id), indent=2))
    return 0


def cmd_comment(args) -> int:
    print(f"commented: {add_comment(args.id, args.body)}")
    return 0


def cmd_state(args) -> int:
    print(f"moved {args.id} -> {set_state(args.id, args.state)}")
    return 0


def cmd_create(args) -> int:
    team = args.team or _config("skill.linear.team")
    if not team:
        print("linear: --team KEY is required (or set skill.linear.team)", file=sys.stderr)
        return 2
    issue = create_issue(args.title, team, args.desc, args.label)
    print(f"created {issue['identifier']}: {issue['url']}")
    return 0


def cmd_dashboard(args) -> int:
    label = args.label or _config("skill.linear.label")
    print(render_dashboard(fetch_issues(label, None), label), end="")
    return 0


def cmd_sync(args) -> int:
    return sync(args.label or _config("skill.linear.label"), args.vault)


def selftest() -> int:
    fixture = {
        "issues": {
            "nodes": [
                {
                    "id": "u1",
                    "identifier": "ENG-9",
                    "title": "Ship auth",
                    "description": "do it",
                    "url": "https://linear.app/x/ENG-9",
                    "priority": 2,
                    "state": {"name": "Todo", "type": "unstarted"},
                    "labels": {"nodes": [{"name": "agent"}]},
                    "assignee": {"displayName": "Lucas"},
                },
                {
                    "id": "u2",
                    "identifier": "ENG-3",
                    "title": "Urgent bug",
                    "description": "",
                    "url": "https://linear.app/x/ENG-3",
                    "priority": 1,
                    "state": {"name": "Backlog", "type": "backlog"},
                    "labels": {"nodes": []},
                    "assignee": {},
                },
                {
                    "id": "u3",
                    "identifier": "ENG-1",
                    "title": "Done thing",
                    "description": "",
                    "url": "https://linear.app/x/ENG-1",
                    "priority": 0,
                    "state": {"name": "Done", "type": "completed"},
                    "labels": {"nodes": []},
                    "assignee": {},
                },
            ]
        }
    }
    issues = parse_issues(fixture)
    assert len(issues) == 3 and issues[0]["identifier"] == "ENG-9", issues
    assert issues[0]["labels"] == ["agent"], issues[0]

    # next = highest priority among actionable (Urgent ENG-3 beats High ENG-9; Done excluded)
    nxt = select_next(issues)
    assert nxt and nxt["identifier"] == "ENG-3", nxt

    assert parse_identifier("ENG-123") == ("ENG", 123)
    assert parse_identifier("bad") is None and parse_identifier("ENG123") is None

    assert build_issue_filter("agent", "Todo") == {
        "labels": {"name": {"eq": "agent"}},
        "state": {"name": {"eq": "Todo"}},
    }
    assert build_issue_filter(None, None) == {}

    assert mirror_filename("ENG-9") == "eng-9.md"
    note = render_mirror_note(issues[0])
    assert "linear: ENG-9" in note and "## Sources" in note and "Ship auth" in note

    table = render_table(issues)
    assert "ENG-1" in table and table.index("ENG-1") < table.index("ENG-3"), "table not sorted"

    dash = render_dashboard(issues, "agent")
    assert "Total:** 3" in dash and "Urgent: 1" in dash and "Open items" in dash
    assert "ENG-1" not in dash.split("Open items")[1], "completed leaked into open items"

    print("linear selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="linear", description=__doc__.splitlines()[0])
    p.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd")

    pl = sub.add_parser("list")
    pl.add_argument("--label")
    pl.add_argument("--state")
    pl.add_argument("--json", action="store_true")
    pn = sub.add_parser("next")
    pn.add_argument("--label")
    pg = sub.add_parser("get")
    pg.add_argument("id")
    pc = sub.add_parser("comment")
    pc.add_argument("id")
    pc.add_argument("body")
    ps = sub.add_parser("state")
    ps.add_argument("id")
    ps.add_argument("state")
    pcr = sub.add_parser("create")
    pcr.add_argument("title")
    pcr.add_argument("--team")
    pcr.add_argument("--label")
    pcr.add_argument("--desc")
    pd = sub.add_parser("dashboard")
    pd.add_argument("--label")
    psy = sub.add_parser("sync")
    psy.add_argument("--label")
    psy.add_argument("--vault")

    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    handlers = {
        "list": cmd_list,
        "next": cmd_next,
        "get": cmd_get,
        "comment": cmd_comment,
        "state": cmd_state,
        "create": cmd_create,
        "dashboard": cmd_dashboard,
        "sync": cmd_sync,
    }
    if args.cmd in handlers:
        return handlers[args.cmd](args)
    p.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
