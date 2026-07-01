#!/usr/bin/env python3
"""Resolve every [[wikilink]] in an Obsidian vault; report unresolved and ambiguous targets.

Obsidian resolves a wikilink target by note *filename* (without the ``.md``
extension), matched anywhere in the vault, and also by an ``aliases`` frontmatter
entry. A link may address a heading (``[[Note#Heading]]``) or a block
(``[[Note#^block-id]]``); the part before the ``#`` or ``^`` is what selects the
note. This validator builds the note/alias index, then reports any link whose
note part resolves to zero notes (unresolved) or more than one (ambiguous).

  validate-wikilinks.py --vault PATH   -> scan the vault, exit 1 on any problem
  validate-wikilinks.py --selftest     -> build a temp fixture, assert, exit 0

Read-only: the scanner never writes or deletes. Exit code is the verdict.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


# Bootstrap the repo's deterministic primitives whether run under `uv run`
# (tools/ already on sys.path) or standalone (insert it from the repo root).
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


# [[target]] or [[target|alias]] or [[target#heading]] or [[target#^block]].
# Embeds (![[...]]) share the target grammar, so the same pattern catches them.
_WIKILINK = re.compile(r"!?\[\[([^\]]+?)\]\]")
_ALIAS_LINE = re.compile(r"^\s*aliases?\s*:\s*(.*)$", re.IGNORECASE)


def _note_key(filename_stem: str) -> str:
    """Normalize a note name for case-insensitive, whitespace-trimmed matching."""
    return filename_stem.strip().casefold()


def _target_note_part(raw_target: str) -> str:
    """Strip the display alias and any heading/block fragment from a link target."""
    note = raw_target.split("|", 1)[0]  # drop |display
    note = note.split("#", 1)[0]  # drop #heading or #^block
    return note.strip()


def _parse_aliases(text: str) -> list[str]:
    """Extract YAML frontmatter aliases (inline ``[a, b]`` or block ``- a`` list)."""
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    front = text[3:end]
    aliases: list[str] = []
    lines = front.splitlines()
    for i, line in enumerate(lines):
        m = _ALIAS_LINE.match(line)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline.startswith("[") and inline.endswith("]"):
            for part in inline[1:-1].split(","):
                cleaned = part.strip().strip("'\"")
                if cleaned:
                    aliases.append(cleaned)
        elif inline and not inline.startswith("#"):
            aliases.append(inline.strip("'\""))
        # Block-style list items on the following lines.
        for follow in lines[i + 1 :]:
            stripped = follow.strip()
            if stripped.startswith("- "):
                item = stripped[2:].strip().strip("'\"")
                if item:
                    aliases.append(item)
            elif stripped and not stripped.startswith("#"):
                break
        break
    return aliases


def build_index(vault: Path) -> dict[str, set[str]]:
    """Map every note key to the files providing it.

    A note is addressable three ways, matching Obsidian: by bare filename stem
    (``[[Acme]]``), by vault-relative path without the extension
    (``[[Companies/Acme]]``), and by any frontmatter alias. All three keys point
    at the same file, so a path-qualified link resolves as readily as a bare one.
    """
    index: dict[str, set[str]] = {}
    for md in sorted(vault.rglob("*.md")):
        rel_posix = md.relative_to(vault).as_posix()
        rel = str(md.relative_to(vault))
        name = md.name
        stem = name[:-3] if name.endswith(".md") else name
        path_key = rel_posix[:-3] if rel_posix.endswith(".md") else rel_posix
        index.setdefault(_note_key(stem), set()).add(rel)
        index.setdefault(_note_key(path_key), set()).add(rel)
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for alias in _parse_aliases(text):
            index.setdefault(_note_key(alias), set()).add(rel)
    return index


def scan_links(vault: Path, index: dict[str, set[str]]) -> tuple[list[str], list[str]]:
    """Return (unresolved, ambiguous) link reports, each as ``file:line: [[target]]``."""
    unresolved: list[str] = []
    ambiguous: list[str] = []
    for md in sorted(vault.rglob("*.md")):
        rel = str(md.relative_to(vault))
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in _WIKILINK.finditer(line):
                note_part = _target_note_part(m.group(1))
                if not note_part:
                    continue  # pure ``#heading`` self-link, nothing to resolve
                providers = index.get(_note_key(note_part), set())
                if len(providers) == 0:
                    unresolved.append(f"{rel}:{lineno}: [[{m.group(1)}]]")
                elif len(providers) > 1:
                    joined = ", ".join(sorted(providers))
                    ambiguous.append(f"{rel}:{lineno}: [[{m.group(1)}]] -> {joined}")
    return unresolved, ambiguous


def run(vault: str, report_path: str | None) -> int:
    root = Path(vault)
    if not root.is_dir():
        print(f"error: vault is not a directory: {vault}", file=sys.stderr)
        return 2
    index = build_index(root)
    unresolved, ambiguous = scan_links(root, index)
    lines = [f"# Wikilink validation: {root}", ""]
    lines.append(f"unresolved: {len(unresolved)}")
    lines.append(f"ambiguous: {len(ambiguous)}")
    lines.append("")
    if unresolved:
        lines.append("## Unresolved")
        lines.extend(unresolved)
        lines.append("")
    if ambiguous:
        lines.append("## Ambiguous")
        lines.extend(ambiguous)
        lines.append("")
    report = "\n".join(lines) + "\n"
    if report_path:
        _atomic_write(report_path, report)
    print(report, end="")
    return 1 if (unresolved or ambiguous) else 0


def selftest() -> int:
    with tempfile.TemporaryDirectory(prefix="wikilinks-selftest.") as tmp:
        vault = Path(tmp)
        (vault / "People").mkdir()
        (vault / "Companies").mkdir()
        # Resolvable by filename.
        (vault / "People" / "Ada Lovelace.md").write_text(
            "---\naliases: [Ada, Countess Lovelace]\n---\nSee [[Analytical Engine]].\n",
            encoding="utf-8",
        )
        # The link target above is unresolved (no such note).
        # Resolvable by alias and by heading fragment.
        (vault / "Companies" / "Acme.md").write_text(
            "Founded by [[Ada]] and documented in [[Ada Lovelace#Career]].\n",
            encoding="utf-8",
        )
        # Two notes share a stem -> ambiguous target.
        (vault / "People" / "Acme.md").write_text("Duplicate stem note.\n", encoding="utf-8")
        (vault / "Index.md").write_text("Link to [[Acme]] is ambiguous.\n", encoding="utf-8")

        # A path-qualified link disambiguates the shared 'Acme' stem and resolves.
        (vault / "People" / "Bob.md").write_text(
            "Reports to [[Companies/Acme]] specifically.\n", encoding="utf-8"
        )

        index = build_index(vault)
        assert "ada" in index, "alias 'Ada' should index"
        assert "countess lovelace" in index, "inline alias should index"
        assert "companies/acme" in index, "path-qualified key should index"
        unresolved, ambiguous = scan_links(vault, index)

        assert any("Analytical Engine" in u for u in unresolved), (
            f"missing unresolved: {unresolved}"
        )
        assert all("[[Ada]]" not in u for u in unresolved), "alias link wrongly unresolved"
        assert all("Ada Lovelace#Career" not in u for u in unresolved), (
            "heading-fragment link wrongly unresolved"
        )
        assert all("[[Companies/Acme]]" not in u for u in unresolved), (
            "path-qualified link wrongly unresolved"
        )
        assert all("[[Companies/Acme]]" not in a for a in ambiguous), (
            "path-qualified link wrongly ambiguous"
        )
        assert any("[[Acme]]" in a for a in ambiguous), f"missing ambiguous: {ambiguous}"

        # A clean vault yields exit 0.
        clean = Path(tmp) / "clean"
        clean.mkdir()
        (clean / "A.md").write_text("Link to [[B]].\n", encoding="utf-8")
        (clean / "B.md").write_text("Back to [[A]].\n", encoding="utf-8")
        c_unresolved, c_ambiguous = scan_links(clean, build_index(clean))
        assert not c_unresolved and not c_ambiguous, "clean vault should have no problems"

    print("validate-wikilinks selftest: ok")
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
