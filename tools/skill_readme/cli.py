"""skill-readme — generate (or check) a README.md per skill from its SKILL.md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skill_readme.core import render_readme
from skillkit import atomic_write


def discover(paths: list[str]) -> list[Path]:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-readme",
        description="Generate a README.md per skill from its SKILL.md (deterministic).",
    )
    parser.add_argument("paths", nargs="*", help="Skill dirs or roots (default: skills/).")
    parser.add_argument(
        "--check", action="store_true", help="Fail if any README is missing or stale."
    )
    args = parser.parse_args(argv)

    dirs = discover(args.paths or ["skills"])
    stale: list[Path] = []
    for d in dirs:
        readme = d / "README.md"
        content = render_readme(d)
        current = readme.read_text(encoding="utf-8") if readme.is_file() else None
        if current == content:
            continue
        if args.check:
            stale.append(readme)
        else:
            atomic_write(readme, content)
            print(f"wrote {readme}")

    if args.check and stale:
        print(f"skill-readme: {len(stale)} README(s) missing or stale:", file=sys.stderr)
        for s in stale:
            print(f"  {s}", file=sys.stderr)
        return 1
    if not args.check:
        print(f"skill-readme: {len(dirs)} skill(s) processed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
