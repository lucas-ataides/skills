#!/usr/bin/env python3
"""Check that every note filename in a vault is a valid, unambiguous Obsidian slug.

A note whose filename is empty (``People/.md``), carries a character Obsidian or a
filesystem rejects, or collides with another note of the same name in the same
folder, breaks linking and sync. This validator reports four failure classes:

  empty        - a note with no name (``.md`` only, e.g. ``People/.md``)
  unsafe-char  - a name holding one of ``< > : " \\ | ? *`` or a control char
  reserved     - a name that is a reserved device word (CON, PRN, NUL, ...)
  duplicate    - two notes sharing a name (case-insensitively) in one directory

  validate-slugs.py --vault PATH   -> scan the vault, exit 1 on any problem
  validate-slugs.py --selftest     -> assert against fixtures, exit 0

Read-only. Exit code is the verdict.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath


def _atomic_write(path: str, data: str) -> None:
    """Write atomically (temp + rename); stdlib-only so this runs from a vault's _tools/."""
    import contextlib
    import os
    import tempfile

    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


# Characters illegal in Windows filenames and/or meaningful to Obsidian linking.
_UNSAFE = re.compile(r'[<>:"\\|?*\x00-\x1f]')
_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def _note_name(filename: str) -> str:
    """The note name is the filename with a single trailing ``.md`` removed.

    ``Path.stem`` mishandles a dotfile (``.md`` -> stem ``.md``), so the name is
    sliced directly: ``.md`` yields an empty note name, the empty-slug signal.
    """
    return filename[:-3] if filename.endswith(".md") else filename


def classify(rel_paths: list[str]) -> dict[str, list[str]]:
    """Classify a list of vault-relative ``.md`` paths into slug failure classes.

    Pure over its input so the verdict is reproducible and testable without a
    filesystem -- the case-insensitive duplicate class in particular cannot be
    provoked with real files on a case-folding filesystem like macOS APFS.
    """
    report: dict[str, list[str]] = {
        "empty": [],
        "unsafe-char": [],
        "reserved": [],
        "duplicate": [],
    }
    seen: dict[tuple[str, str], str] = {}
    for rel in sorted(rel_paths):
        p = PurePosixPath(rel.replace("\\", "/"))
        parent = str(p.parent)
        note_name = _note_name(p.name)
        stripped = note_name.strip()
        if stripped == "":
            report["empty"].append(rel)
            continue
        unsafe = _UNSAFE.search(note_name) is not None
        if unsafe or note_name != stripped:
            report["unsafe-char"].append(rel)
        if note_name.split(".")[0].casefold() in _RESERVED:
            report["reserved"].append(rel)
        key = (parent, note_name.casefold())
        prior = seen.get(key)
        if prior is not None:
            report["duplicate"].append(f"{rel} (collides with {prior})")
        else:
            seen[key] = rel
    return report


def scan(vault: Path) -> dict[str, list[str]]:
    """Return a report dict mapping each failure class to a list of offending paths."""
    rel_paths = [str(md.relative_to(vault)) for md in vault.rglob("*.md")]
    return classify(rel_paths)


def run(vault: str, report_path: str | None) -> int:
    root = Path(vault)
    if not root.is_dir():
        print(f"error: vault is not a directory: {vault}", file=sys.stderr)
        return 2
    report = scan(root)
    total = sum(len(v) for v in report.values())
    lines = [f"# Slug validation: {root}", ""]
    for cls, items in report.items():
        lines.append(f"{cls}: {len(items)}")
    lines.append("")
    for cls, items in report.items():
        if items:
            lines.append(f"## {cls}")
            lines.extend(items)
            lines.append("")
    rendered = "\n".join(lines) + "\n"
    if report_path:
        _atomic_write(report_path, rendered)
    print(rendered, end="")
    return 1 if total else 0


def selftest() -> int:
    # Filesystem-backed pass: empty/unsafe/reserved classes from real files.
    with tempfile.TemporaryDirectory(prefix="slugs-selftest.") as tmp:
        vault = Path(tmp)
        people = vault / "People"
        people.mkdir()
        (people / ".md").write_text("orphan\n", encoding="utf-8")
        (people / "Bad:Name.md").write_text("x\n", encoding="utf-8")
        (people / "CON.md").write_text("x\n", encoding="utf-8")

        report = scan(vault)
        assert any("People/.md" in p for p in report["empty"]), f"empty miss: {report['empty']}"
        assert report["unsafe-char"], "unsafe char not caught"
        assert any("CON" in p for p in report["reserved"]), f"reserved miss: {report['reserved']}"

    # Pure-classifier pass: a case-folding collision (Acme vs acme) cannot exist
    # as two real files on a case-insensitive filesystem, so the duplicate class
    # is asserted against ``classify`` directly -- the honest, portable test.
    dup = classify(["Companies/Acme.md", "Companies/acme.md", "Companies/Other.md"])
    assert dup["duplicate"], f"duplicate not caught: {dup}"
    assert not dup["empty"], f"false empty: {dup}"

    empty = classify(["People/.md", "Projects/.md"])
    assert len(empty["empty"]) == 2, f"empty-path miss: {empty}"

    unsafe = classify(["People/Bad:Name.md", 'Topics/Quote".md', "Maps/pipe|name.md"])
    assert len(unsafe["unsafe-char"]) == 3, f"unsafe miss: {unsafe}"

    clean = classify(["People/Ada Lovelace.md", "Companies/Acme Corp.md", "Topics/RAG.md"])
    assert sum(len(v) for v in clean.values()) == 0, f"clean failed: {clean}"

    print("validate-slugs selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vault", help="Path to the Obsidian vault root.")
    parser.add_argument("--report", help="Optional path to write the report (atomic).")
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.vault:
        parser.error("--vault is required unless --selftest is given")
    return run(args.vault, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
