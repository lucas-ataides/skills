#!/usr/bin/env python3
"""Turn an approved issues spec (JSON) into tracker issues, deterministically.

The agent's job is the judgment: deciding the discrete work, writing acceptance
criteria, splitting the oversized. That judgment lands in a JSON spec. This script
owns the deterministic remainder — validating the spec against the issue anatomy and
building the exact creation command — so the same spec always yields the same issues,
and a malformed draft is rejected before any external write.

    to-issues.py check  <spec.json>              validate against the anatomy
    to-issues.py create <spec.json> [--dry-run]  create via `gh` (or print the commands)
    to-issues.py --selftest

Spec shape:
    {"tracker": "github",
     "issues": [{"title": "...", "body": "...", "acceptance": ["..."],
                 "labels": ["type:feat"], "assignee": "octocat"}]}
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SUPPORTED_TRACKERS = ("github",)


def validate(spec: dict) -> list[str]:
    """Return a list of human-readable errors; an empty list means the spec is valid."""
    errors: list[str] = []
    tracker = spec.get("tracker", "github")
    if tracker not in SUPPORTED_TRACKERS:
        errors.append(
            f"tracker {tracker!r} unsupported; this script writes only {SUPPORTED_TRACKERS}"
        )
    issues = spec.get("issues")
    if not isinstance(issues, list) or not issues:
        errors.append("'issues' must be a non-empty list")
        return errors
    for i, issue in enumerate(issues):
        where = f"issue[{i}]"
        if not isinstance(issue, dict):
            errors.append(f"{where} must be an object")
            continue
        title = issue.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{where} has no title")
        acceptance = issue.get("acceptance")
        if not isinstance(acceptance, list) or not [a for a in acceptance if str(a).strip()]:
            errors.append(f"{where} ({title!r}) is missing acceptance criteria")
        labels = issue.get("labels", [])
        if not isinstance(labels, list):
            errors.append(f"{where} ({title!r}) labels must be a list")
    return errors


def render_body(issue: dict) -> str:
    """Render the issue body deterministically: context, then a checklist of criteria."""
    parts = [str(issue.get("body", "")).strip()]
    criteria = [str(a).strip() for a in issue.get("acceptance", []) if str(a).strip()]
    if criteria:
        parts.append("## Acceptance criteria\n" + "\n".join(f"- [ ] {a}" for a in criteria))
    return "\n\n".join(p for p in parts if p)


def build_command(issue: dict) -> list[str]:
    """Build the exact `gh issue create` argv for one issue. Pure and deterministic."""
    cmd = [
        "gh",
        "issue",
        "create",
        "--title",
        str(issue["title"]).strip(),
        "--body",
        render_body(issue),
    ]
    for label in issue.get("labels", []):
        cmd += ["--label", str(label)]
    assignee = issue.get("assignee")
    if assignee:
        cmd += ["--assignee", str(assignee)]
    return cmd


def load(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"to-issues: cannot read spec {path!r}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def cmd_check(path: str) -> int:
    errors = validate(load(path))
    for e in errors:
        print(f"  invalid: {e}", file=sys.stderr)
    print(f"to-issues: {'OK' if not errors else f'{len(errors)} error(s)'}")
    return 1 if errors else 0


def cmd_create(path: str, dry_run: bool) -> int:
    spec = load(path)
    errors = validate(spec)
    if errors:
        for e in errors:
            print(f"  invalid: {e}", file=sys.stderr)
        return 1
    for issue in spec["issues"]:
        cmd = build_command(issue)
        if dry_run:
            print(" ".join(_shell_quote(c) for c in cmd))
            continue
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"to-issues: gh failed on {issue['title']!r}", file=sys.stderr)
            return result.returncode
    return 0


def _shell_quote(s: str) -> str:
    return (
        s
        if s and all(c.isalnum() or c in "-_/=:." for c in s)
        else "'" + s.replace("'", "'\\''") + "'"
    )


def selftest() -> int:
    good = {
        "tracker": "github",
        "issues": [
            {
                "title": "Add login",
                "body": "Users need auth.",
                "acceptance": ["POST /login returns 200", "bad creds return 401"],
                "labels": ["type:feat"],
                "assignee": "octocat",
            }
        ],
    }
    assert validate(good) == [], validate(good)
    assert validate({"issues": []}) == ["'issues' must be a non-empty list"]
    assert any("acceptance" in e for e in validate({"issues": [{"title": "x", "acceptance": []}]}))
    cmd = build_command(good["issues"][0])
    assert cmd[:5] == ["gh", "issue", "create", "--title", "Add login"], cmd
    assert "--label" in cmd and "type:feat" in cmd and "octocat" in cmd
    assert "- [ ] POST /login returns 200" in render_body(good["issues"][0])
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(good), encoding="utf-8")
        assert cmd_check(str(p)) == 0
        assert cmd_create(str(p), dry_run=True) == 0
    print("to-issues selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create tracker issues from an approved JSON spec."
    )
    sub = parser.add_subparsers(dest="cmd")
    p_check = sub.add_parser("check", help="Validate the spec against the issue anatomy.")
    p_check.add_argument("spec")
    p_create = sub.add_parser(
        "create", help="Create the issues (or --dry-run to print the commands)."
    )
    p_create.add_argument("spec")
    p_create.add_argument("--dry-run", action="store_true")
    parser.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.cmd == "check":
        return cmd_check(args.spec)
    if args.cmd == "create":
        return cmd_create(args.spec, args.dry_run)
    parser.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
