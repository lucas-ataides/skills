"""Command-line entry point for skill-new."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from skillkit import atomic_write

_TEMPLATE = (Path(__file__).parent / "templates" / "SKILL.md.tmpl").read_text(encoding="utf-8")
_KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def find_root(start: Path) -> Path:
    """Walk up from ``start`` to the repo root (the dir holding pyproject.toml)."""
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return start


def _yaml_safe(value: str) -> str:
    """Return a YAML-safe scalar — quoted only when the plain form would mis-parse."""
    stripped = value.lstrip()
    unsafe = (
        bool(re.search(r":(\s|$)", value)) or " #" in value or stripped[:1] in "#&*!|>%@`\"'[]{},"
    )
    return json.dumps(value, ensure_ascii=False) if unsafe else value


def render(name: str, description: str, invocation: str) -> str:
    disable_line = "disable-model-invocation: true\n" if invocation == "user" else ""
    return _TEMPLATE.format(
        name=name, description=_yaml_safe(description), disable_line=disable_line
    )


def default_description(name: str, invocation: str) -> str:
    if invocation == "user":
        return f"{name} - replace this one-line summary."
    spoken = name.replace("-", " ")
    return f"Run the {name} task. Use when the user asks to {spoken}."


def register(root: Path, rel: str) -> bool:
    """Add ``rel`` to .claude-plugin/plugin.json. Returns True if it changed."""
    manifest = root / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
    else:
        data = {"name": "ataides-skills", "skills": []}
    skills = set(data.get("skills", []))
    if rel in skills:
        return False
    data["skills"] = sorted(skills | {rel})
    atomic_write(manifest, json.dumps(data, indent=2) + "\n")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-new", description="Scaffold a lint-clean, registered skill."
    )
    parser.add_argument("--category", required=True, help="Domain folder, e.g. engineering.")
    parser.add_argument("--name", required=True, help="Skill name (kebab-case).")
    parser.add_argument(
        "--invocation",
        choices=["user", "model"],
        default="user",
        help="user = typed by you (default); model = the agent can fire it.",
    )
    parser.add_argument("--description", default=None)
    parser.add_argument("--root", default=".", help="Repo root (default: discovered upward).")
    parser.add_argument("--no-register", action="store_true", help="Skip plugin.json registration.")
    args = parser.parse_args(argv)

    for label, value in (("category", args.category), ("name", args.name)):
        if not _KEBAB.match(value):
            parser.error(f"{label} must be kebab-case: {value!r}")

    root = find_root(Path(args.root).resolve())
    dest_dir = root / "skills" / args.category / args.name
    if dest_dir.exists():
        parser.error(f"refusing to overwrite existing skill: {dest_dir}")

    description = args.description or default_description(args.name, args.invocation)
    skill_md = dest_dir / "SKILL.md"
    atomic_write(skill_md, render(args.name, description, args.invocation))

    rel = f"./skills/{args.category}/{args.name}"
    registered = register(root, rel) if not args.no_register else False

    print(f"created {skill_md.relative_to(root)}")
    if registered:
        print(f"registered {rel} in .claude-plugin/plugin.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
