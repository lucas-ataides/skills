"""skill-cursor — generate Cursor project rules (.mdc) from skills' SKILL.md.

    skill-cursor <out-dir> [paths ...]   # default paths: skills/
    skill-cursor <out-dir> --prune       # also delete stale generated rules
    skill-cursor --selftest

Point ``<out-dir>`` at a project's ``.cursor/rules`` to install the skills as Cursor rules.
The output is local (machine-specific source paths), so it is generated, never committed.
``--prune`` removes a previously generated rule whose skill no longer exists — only files
carrying the generated-rule marker are touched, so hand-written rules are never deleted.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from skill_cursor.core import render_mdc
from skillkit import atomic_write, safe_remove

_MARKER = "ported from a Claude Code skill"


def discover(paths: list[str]) -> list[Path]:
    """Return skill directories under the given paths, de-duplicated, in stable order."""
    dirs: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if (p / "SKILL.md").is_file():
            dirs.append(p)
        elif p.is_dir():
            dirs.extend(sorted(sk.parent for sk in p.rglob("SKILL.md")))
    seen: set[Path] = set()
    out: list[Path] = []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def prune_stale(out_dir: Path, current: set[str]) -> list[Path]:
    """Delete generated rules whose skill no longer exists; hand-written files are kept.

    Only a file carrying the generated-rule marker is ever removed, and the removal goes
    through ``skillkit.safe_remove`` so nothing outside ``out_dir`` can be touched.
    """
    removed: list[Path] = []
    for f in sorted(out_dir.glob("*.mdc")):
        if f.stem in current:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if _MARKER in text:
            safe_remove(f, root=out_dir)
            removed.append(f)
    return removed


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "demo"
        d.mkdir()
        (d / "SKILL.md").write_text(
            '---\nname: demo\ndescription: "A demo skill: with a colon, for YAML safety."\n---\n\n'
            "Run `scripts/x.sh`, then read [refs](references/x.md).\n",
            encoding="utf-8",
        )
        out = render_mdc(d)
        assert out.startswith("---\n"), "missing frontmatter open"
        assert "alwaysApply: false" in out, "missing alwaysApply"
        assert '"A demo skill: with a colon, for YAML safety."' in out, "description not YAML-safe"
        assert "Run `scripts/x.sh`" in out and "references/x.md" in out, "body dropped"
        assert str(d.resolve()) in out, "source path missing"
        assert out.count("\n---\n") == 1 and out.startswith("---\n"), "frontmatter block malformed"

        rules = Path(tmp) / "rules"
        rules.mkdir()
        (rules / "demo.mdc").write_text(out, encoding="utf-8")
        (rules / "stale.mdc").write_text(f"---\n---\n\n> x {_MARKER}.\n", encoding="utf-8")
        (rules / "hand.mdc").write_text("---\n---\n\nhand-written rule\n", encoding="utf-8")
        removed = prune_stale(rules, {"demo"})
        assert [r.name for r in removed] == ["stale.mdc"], "prune removed the wrong set"
        assert (rules / "demo.mdc").is_file(), "prune deleted a current rule"
        assert (rules / "hand.mdc").is_file(), "prune deleted a hand-written rule"
    print("skill-cursor selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-cursor",
        description="Generate Cursor project rules (.mdc) from skills' SKILL.md.",
    )
    parser.add_argument("out", nargs="?", help="Output dir, e.g. <project>/.cursor/rules.")
    parser.add_argument("paths", nargs="*", help="Skill dirs or roots (default: skills/).")
    parser.add_argument(
        "--prune", action="store_true", help="Delete stale generated rules (marker-guarded)."
    )
    parser.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.out:
        parser.error("an output directory is required, e.g. <project>/.cursor/rules")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    dirs = discover(args.paths or ["skills"])
    for d in dirs:
        atomic_write(out_dir / f"{d.name}.mdc", render_mdc(d))
    pruned: list[Path] = []
    if args.prune:
        pruned = prune_stale(out_dir, {d.name for d in dirs})
        for r in pruned:
            print(f"pruned stale rule {r.name}")
    print(
        f"skill-cursor: wrote {len(dirs)} rule(s) to {out_dir}"
        + (f", pruned {len(pruned)}" if args.prune else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
