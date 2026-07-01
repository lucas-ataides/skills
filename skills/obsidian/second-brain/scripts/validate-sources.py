#!/usr/bin/env python3
"""Verify provenance: every canonical note is source-backed and every ref resolves.

A memory vault is only trustworthy if each promoted fact traces to where it came
from. This validator enforces two invariants over the canonical folders:

  1. Every canonical note carries provenance -- a non-empty ``sources:`` (or
     ``provenance:``) frontmatter list, or an inline ``Sources`` section that
     names at least one reference.
  2. Every source reference resolves -- a ``[[Sources/...]]`` wikilink to a real
     note under ``Sources/``, or a ``manifest:ID`` token present in
     SOURCE-MANIFEST.md. A placeholder ref (``[[Source: TODO]]``, ``source: ???``,
     ``<source>``) is reported so it can be filled in.

Canonical folders: People, Companies, Projects, Products, Topics, Decisions,
Commitments, Procedures, Preferences. Folders that are not promoted knowledge
(Sources, Maps, Reports, Context Packs, _tools) are skipped.

  validate-sources.py --vault PATH   -> scan, exit 1 on any violation
  validate-sources.py --selftest     -> assert against fixtures, exit 0

Read-only. Exit code is the verdict.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


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


_CANONICAL_FOLDERS = (
    "People",
    "Companies",
    "Projects",
    "Products",
    "Topics",
    "Decisions",
    "Commitments",
    "Procedures",
    "Preferences",
)
# Placeholder markers. TODO/TBD/FIXME match case-SENSITIVELY (uppercase only): lowercased,
# "todo"/"tbd" are ordinary words in other languages (Portuguese "todo" = "all") and must not
# trip the gate. Only the multi-word "unknown source" stays case-insensitive.
_PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|\?\?\?|<source>|(?i:\bunknown source\b)")
_SOURCES_WIKILINK = re.compile(r"\[\[\s*(Sources/[^\]|#]+?)\s*(?:[|#][^\]]*)?\]\]")
_MANIFEST_REF = re.compile(r"\bmanifest:([A-Za-z0-9._\-]+)\b")
_FRONT_SOURCES = re.compile(r"^\s*(?:sources?|provenance)\s*:\s*(.*)$", re.IGNORECASE)


def _frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def _has_frontmatter_provenance(front: str) -> bool:
    """True if frontmatter declares a non-empty sources/provenance value or list."""
    lines = front.splitlines()
    for i, line in enumerate(lines):
        m = _FRONT_SOURCES.match(line)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline and inline not in ("[]", "~", "null"):
            return True
        # Block list: a following ``- item`` line means non-empty.
        for follow in lines[i + 1 :]:
            stripped = follow.strip()
            if stripped.startswith("- ") and len(stripped) > 2:
                return True
            if stripped and not stripped.startswith("#"):
                break
        return False
    return False


def _has_inline_sources_section(body: str) -> bool:
    """True if the body has a ``## Sources``/``## Provenance`` heading with a ref."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^\s*#+\s*(?:sources?|provenance)\b", line, re.IGNORECASE):
            for follow in lines[i + 1 :]:
                if _SOURCES_WIKILINK.search(follow) or _MANIFEST_REF.search(follow):
                    return True
                if re.match(r"^\s*#+\s", follow):
                    break
    return False


def _collect_refs(text: str) -> tuple[list[str], list[str], bool]:
    """Return (sources_wikilinks, manifest_ids, has_placeholder) found in the text."""
    wikilinks = [m.group(1).strip() for m in _SOURCES_WIKILINK.finditer(text)]
    manifest_ids = [m.group(1) for m in _MANIFEST_REF.finditer(text)]
    has_placeholder = _PLACEHOLDER.search(text) is not None
    return wikilinks, manifest_ids, has_placeholder


def _source_targets(vault: Path) -> set[str]:
    """Set of resolvable ``Sources/<name>`` targets (without the .md extension)."""
    targets: set[str] = set()
    src_dir = vault / "Sources"
    if not src_dir.is_dir():
        return targets
    for md in src_dir.rglob("*.md"):
        rel = md.relative_to(vault).as_posix()
        targets.add(rel[:-3] if rel.endswith(".md") else rel)
        targets.add(f"Sources/{md.stem}")
    return targets


def _manifest_ids(vault: Path) -> set[str]:
    manifest = vault / "SOURCE-MANIFEST.md"
    if not manifest.is_file():
        return set()
    text = manifest.read_text(encoding="utf-8")
    return set(_MANIFEST_REF.findall(text)) | set(re.findall(r"\bid:\s*([A-Za-z0-9._\-]+)", text))


def scan(vault: Path) -> dict[str, list[str]]:
    """Return violation classes: missing-provenance, placeholder-ref, unresolved-ref."""
    report: dict[str, list[str]] = {
        "missing-provenance": [],
        "placeholder-ref": [],
        "unresolved-ref": [],
    }
    valid_sources = _source_targets(vault)
    valid_manifest = _manifest_ids(vault)
    for folder in _CANONICAL_FOLDERS:
        base = vault / folder
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            rel = md.relative_to(vault).as_posix()
            try:
                text = md.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            front = _frontmatter(text)
            # The inline-section check runs over the whole note: a Markdown
            # ``## Sources`` heading cannot occur inside the YAML frontmatter, so
            # no fragile body-offset slicing is needed.
            has_prov = _has_frontmatter_provenance(front) or _has_inline_sources_section(text)
            wikilinks, manifest_ids, placeholder = _collect_refs(text)
            if not has_prov:
                report["missing-provenance"].append(rel)
            if placeholder:
                report["placeholder-ref"].append(rel)
            for link in wikilinks:
                normalized = link[:-3] if link.endswith(".md") else link
                if normalized not in valid_sources:
                    report["unresolved-ref"].append(f"{rel}: [[{link}]]")
            for mid in manifest_ids:
                if mid not in valid_manifest:
                    report["unresolved-ref"].append(f"{rel}: manifest:{mid}")
    return report


def run(vault: str, report_path: str | None) -> int:
    root = Path(vault)
    if not root.is_dir():
        print(f"error: vault is not a directory: {vault}", file=sys.stderr)
        return 2
    report = scan(root)
    total = sum(len(v) for v in report.values())
    lines = [f"# Source/provenance validation: {root}", ""]
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


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def selftest() -> int:
    with tempfile.TemporaryDirectory(prefix="sources-selftest.") as tmp:
        vault = Path(tmp)
        # A real source note + a manifest entry to resolve against.
        _write(vault / "Sources" / "chat-2026-06-ada.md", "Source capture.\n")
        _write(
            vault / "SOURCE-MANIFEST.md",
            "# Sources\n\n- id: gmail-thread-42 | account: a@b.com\n",
        )
        # Good note: frontmatter provenance + a resolvable wikilink + manifest id.
        _write(
            vault / "People" / "Ada Lovelace.md",
            "---\nsources:\n  - [[Sources/chat-2026-06-ada]]\n---\n"
            "Async preference. See manifest:gmail-thread-42.\n",
        )
        # Missing provenance: no sources frontmatter and no Sources section.
        _write(vault / "People" / "Bob.md", "---\ntype: person\n---\nNo sources here.\n")
        # Placeholder ref.
        _write(
            vault / "Companies" / "Acme.md",
            "---\nsources:\n  - TODO find source\n---\nSource: ??? to fill.\n",
        )
        # Unresolved refs: a Sources link to a missing file, a missing manifest id.
        _write(
            vault / "Projects" / "Atlas.md",
            "---\nsources:\n  - [[Sources/does-not-exist]]\n---\nPer manifest:no-such-id.\n",
        )
        # A note using the Portuguese word "todo" (= "all") with valid provenance must stay
        # clean — the case-sensitive TODO marker must not false-positive on other languages.
        _write(
            vault / "Topics" / "Multilingual.md",
            "---\nsources:\n  - [[Sources/chat-2026-06-ada]]\n---\ntodo conteúdo é válido.\n",
        )

        report = scan(vault)
        assert any("People/Bob.md" in p for p in report["missing-provenance"]), report
        assert any("Companies/Acme.md" in p for p in report["placeholder-ref"]), report
        assert any("does-not-exist" in p for p in report["unresolved-ref"]), report
        assert any("no-such-id" in p for p in report["unresolved-ref"]), report
        # The good note must be clean across every class.
        assert all("Ada Lovelace.md" not in p for p in report["missing-provenance"]), report
        assert all("Ada Lovelace.md" not in p for p in report["unresolved-ref"]), report
        # Portuguese "todo" (= "all") is not a placeholder: the multilingual note is clean.
        assert all("Multilingual.md" not in p for p in report["placeholder-ref"]), report
        assert all("Multilingual.md" not in p for p in report["missing-provenance"]), report

    print("validate-sources selftest: ok")
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
