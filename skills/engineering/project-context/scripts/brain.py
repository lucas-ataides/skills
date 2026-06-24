#!/usr/bin/env python3
"""The project brain — deterministic, CLI-only project memory committed beside the code.

A brain is a `./brain/` directory of Markdown pages. Each page holds a rewritable **Truth**
(the current understanding) and an append-only **Timeline** (what happened, in order). The
agent supplies the judgment — what to record and the why — and this script performs every
write, atomically and identically. Brain files are never hand-edited: the CLI is the only
writer, so the structure is correct by construction. (Model inspired by brain.md; this is
our own self-contained implementation, no external dependency.)

    brain.py init   [--root .]                         scaffold ./brain/ + index
    brain.py list   [--root .]                         list pages (id · category · title)
    brain.py read   <id> [--root .]                    print a page
    brain.py create --id <id> --title "<t>" [--category <c>] [--root .]
    brain.py truth  <id> --text "<truth>" [--why "<reason>"] [--root .]
    brain.py timeline <id> --kind <type> --text "<msg>" [--root .]
    brain.py reindex [--root .]                        rebuild the index from the pages
    brain.py --selftest

Run it at the project root; the brain lives in `./brain/`.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# --- pure helpers (no filesystem; the selftest covers these) ----------------

def valid_id(page_id: str) -> bool:
    """A page id is a lowercase slug — safe as a filename and a wikilink target."""
    return bool(_ID.match(page_id))


def render_page(page_id: str, title: str, category: str, today: str, stamp: str) -> str:
    """Render a fresh page: frontmatter, an empty Truth, and a Timeline seeded with creation."""
    return (
        "---\n"
        f"id: {page_id}\n"
        f'title: "{title}"\n'
        f"category: {category}\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Truth\n\n"
        "_Not yet established._\n\n"
        "## Timeline\n\n"
        f"- {stamp} [created] page created\n"
    )


def replace_section(text: str, name: str, body: str) -> str:
    """Replace the body of `## name` (up to the next `## ` or EOF). Raises if absent."""
    lines = text.splitlines(keepends=True)
    start = end = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == f"## {name}":
            start = i
        elif start is not None and i > start and line.startswith("## "):
            end = i
            break
    if start is None:
        raise ValueError(f"section not found: {name}")
    if end is None:
        end = len(lines)
    new = [lines[start]] + ["\n", body.rstrip("\n") + "\n", "\n"]
    return "".join(lines[:start] + new + lines[end:])


def append_to_section(text: str, name: str, line: str) -> str:
    """Append a line at the end of `## name` (before the next `## ` or EOF). Raises if absent."""
    lines = text.splitlines(keepends=True)
    start = end = None
    for i, ln in enumerate(lines):
        if ln.rstrip("\n") == f"## {name}":
            start = i
        elif start is not None and i > start and ln.startswith("## "):
            end = i
            break
    if start is None:
        raise ValueError(f"section not found: {name}")
    if end is None:
        end = len(lines)
    insert = line if line.endswith("\n") else line + "\n"
    # drop trailing blank lines inside the section, then append the bullet
    block = end
    while block - 1 > start and lines[block - 1].strip() == "":
        block -= 1
    return "".join(lines[:block] + [insert] + lines[block:])


def set_frontmatter(text: str, key: str, value: str) -> str:
    """Set a frontmatter key (assumes a leading --- block). Replaces the first match."""
    pat = re.compile(rf"^{re.escape(key)}: .*$", re.MULTILINE)
    return pat.sub(f"{key}: {value}", text, count=1)


def parse_meta(text: str) -> dict[str, str]:
    """Read id/title/category from a page's frontmatter — enough to index and list."""
    meta: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip() == "---" and meta:
            break
        m = re.match(r"^(id|title|category): (.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    return meta


def render_index(pages: list[dict[str, str]]) -> str:
    """Render the brain hub: the protocol note plus a wikilinked list of every page."""
    head = (
        "---\n"
        "id: index\n"
        "category: hub\n"
        "---\n\n"
        "# Project brain\n\n"
        "CLI-only project memory. Never hand-edit a page — drive every change through\n"
        "`scripts/brain.py` so the brain stays correct by construction. Each page carries a\n"
        "rewritable **Truth** and an append-only **Timeline**.\n\n"
        "## Pages\n\n"
    )
    if not pages:
        return head + "_none yet_\n"
    rows = [
        f"- [[{p['id']}]] — {p.get('category', '?')} — {p.get('title', '')}"
        for p in sorted(pages, key=lambda x: x["id"])
    ]
    return head + "\n".join(rows) + "\n"


# --- filesystem I/O ---------------------------------------------------------

def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def _brain(root: str) -> Path:
    return Path(root) / "brain"


def _page(root: str, page_id: str) -> Path:
    return _brain(root) / f"{page_id}.md"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _stamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def _pages(root: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    brain = _brain(root)
    if not brain.is_dir():
        return out
    for md in sorted(brain.glob("*.md")):
        if md.name == "index.md":
            continue
        out.append(parse_meta(md.read_text(encoding="utf-8")))
    return out


def cmd_init(root: str) -> int:
    idx = _brain(root) / "index.md"
    if idx.exists():
        print(f"kept {idx}")
    else:
        _atomic_write(idx, render_index([]))
        print(f"created {idx}")
    return 0


def cmd_create(root: str, page_id: str, title: str, category: str) -> int:
    if not valid_id(page_id):
        print(f"brain: invalid id (use a lowercase slug): {page_id}", file=sys.stderr)
        return 2
    path = _page(root, page_id)
    if path.exists():
        print(f"kept existing {path}")
        return 0
    _atomic_write(path, render_page(page_id, title, category, _today(), _stamp()))
    _atomic_write(_brain(root) / "index.md", render_index(_pages(root)))
    print(f"created {path}")
    return 0


def _require_page(root: str, page_id: str) -> Path:
    path = _page(root, page_id)
    if not path.is_file():
        print(f"brain: no page {page_id} (create it first)", file=sys.stderr)
        raise SystemExit(6)
    return path


def cmd_truth(root: str, page_id: str, text: str, why: str | None) -> int:
    path = _require_page(root, page_id)
    content = path.read_text(encoding="utf-8")
    content = replace_section(content, "Truth", text)
    content = set_frontmatter(content, "updated", _today())
    reason = why or "truth updated"
    content = append_to_section(content, "Timeline", f"- {_stamp()} [truth] {reason}")
    _atomic_write(path, content)
    print(f"updated truth: {path}")
    return 0


def cmd_timeline(root: str, page_id: str, kind: str, text: str) -> int:
    path = _require_page(root, page_id)
    content = path.read_text(encoding="utf-8")
    content = append_to_section(content, "Timeline", f"- {_stamp()} [{kind}] {text}")
    _atomic_write(path, content)
    print(f"appended timeline: {path}")
    return 0


def cmd_list(root: str) -> int:
    pages = _pages(root)
    if not pages:
        print("brain: no pages")
        return 0
    for p in sorted(pages, key=lambda x: x.get("id", "")):
        print(f"{p.get('id', '?'):24} {p.get('category', '?'):12} {p.get('title', '')}")
    return 0


def cmd_read(root: str, page_id: str) -> int:
    print(_require_page(root, page_id).read_text(encoding="utf-8"), end="")
    return 0


def cmd_reindex(root: str) -> int:
    _atomic_write(_brain(root) / "index.md", render_index(_pages(root)))
    print(f"reindexed {_brain(root) / 'index.md'}")
    return 0


def selftest() -> int:
    # pure helpers
    assert valid_id("auth-flow") and not valid_id("Auth Flow") and not valid_id("-x")
    page = render_page("p", "Title", "topic", "2026-06-24", "2026-06-24T10:00")
    assert "## Truth" in page and "[created]" in page and parse_meta(page)["id"] == "p"

    swapped = replace_section(page, "Truth", "We use OAuth.")
    assert "We use OAuth." in swapped and "_Not yet established._" not in swapped
    assert "## Timeline" in swapped, "replace_section ate the next section"

    appended = append_to_section(swapped, "Timeline", "- t [note] hello")
    assert appended.rstrip().endswith("[note] hello"), appended

    idx = render_index([{"id": "b", "title": "B", "category": "x"}, {"id": "a", "title": "A", "category": "y"}])
    assert idx.index("[[a]]") < idx.index("[[b]]"), "index not sorted"

    # filesystem round-trip in a temp project
    with tempfile.TemporaryDirectory(prefix="brain-selftest.") as tmp:
        assert cmd_init(tmp) == 0
        assert (_brain(tmp) / "index.md").is_file()
        assert cmd_create(tmp, "auth-flow", "Auth flow", "topic") == 0
        assert cmd_create(tmp, "auth-flow", "Auth flow", "topic") == 0  # idempotent: kept
        assert cmd_truth(tmp, "auth-flow", "Sessions are JWT.", why="ADR-3") == 0
        assert cmd_timeline(tmp, "auth-flow", "decision", "switched to JWT") == 0
        body = _page(tmp, "auth-flow").read_text(encoding="utf-8")
        assert "Sessions are JWT." in body, "truth not written"
        assert "[truth] ADR-3" in body and "[decision] switched to JWT" in body, "timeline missing"
        assert body.count("## Truth") == 1 and body.count("## Timeline") == 1, "sections duplicated"
        assert "[[auth-flow]]" in (_brain(tmp) / "index.md").read_text(encoding="utf-8"), "not indexed"
        try:  # a missing page must be refused, not silently created
            cmd_truth(tmp, "missing", "x", None)
            raise AssertionError("truth on a missing page should have exited")
        except SystemExit:
            pass
    print("brain selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="brain", description=__doc__.splitlines()[0])
    p.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd")

    def add_root(sp):
        sp.add_argument("--root", default=".")

    add_root(sub.add_parser("init"))
    add_root(sub.add_parser("list"))
    sp = sub.add_parser("read")
    sp.add_argument("id")
    add_root(sp)
    sp = sub.add_parser("create")
    sp.add_argument("--id", required=True)
    sp.add_argument("--title", required=True)
    sp.add_argument("--category", default="topic")
    add_root(sp)
    sp = sub.add_parser("truth")
    sp.add_argument("id")
    sp.add_argument("--text", required=True)
    sp.add_argument("--why")
    add_root(sp)
    sp = sub.add_parser("timeline")
    sp.add_argument("id")
    sp.add_argument("--kind", required=True)
    sp.add_argument("--text", required=True)
    add_root(sp)
    add_root(sub.add_parser("reindex"))

    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "init":
        return cmd_init(args.root)
    if args.cmd == "list":
        return cmd_list(args.root)
    if args.cmd == "read":
        return cmd_read(args.root, args.id)
    if args.cmd == "create":
        return cmd_create(args.root, args.id, args.title, args.category)
    if args.cmd == "truth":
        return cmd_truth(args.root, args.id, args.text, args.why)
    if args.cmd == "timeline":
        return cmd_timeline(args.root, args.id, args.kind, args.text)
    if args.cmd == "reindex":
        return cmd_reindex(args.root)
    p.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
