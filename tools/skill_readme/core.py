"""Generate a human-facing README.md for a skill from its SKILL.md.

Deterministic: the same SKILL.md always renders the same README. The README explains
what the skill is, how it is invoked, when it fires, and what it does — for a human
browsing the repo, separate from the agent-facing SKILL.md.
"""

from __future__ import annotations

import re
from pathlib import Path

from skill_lint.core import SkillDoc

_STEP = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*")
_SENTENCE = re.compile(r"(?<=[.!?])\s")


def parse_triggers(description: str) -> list[str]:
    """Pull the 'Use when …' clause from a description into discrete trigger phrases."""
    m = re.search(r"(?i)\buse (?:this )?when\s+", description)
    if not m:
        return []
    tail = description[m.end() :]
    tail = _SENTENCE.split(tail)[0].rstrip(". ")
    tail = re.sub(r"(?i)^the user (?:wants to |asks to |wants |)", "", tail)
    parts = re.split(r",\s*|\s+or\s+", tail)
    return [p.strip().removeprefix("or ").strip().rstrip(".") for p in parts if p.strip()]


def step_titles(doc: SkillDoc) -> list[str]:
    out: list[str] = []
    for ln in doc.body_lines:
        m = _STEP.match(ln.text.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def list_scripts(skill_dir: Path) -> list[str]:
    sd = skill_dir / "scripts"
    if not sd.is_dir():
        return []
    return sorted(p.name for p in sd.iterdir() if p.is_file())


def render_readme(skill_dir: Path) -> str:
    doc = SkillDoc.load(skill_dir / "SKILL.md")
    fm = doc.frontmatter or {}
    name = str(fm.get("name", skill_dir.name))
    desc = str(fm.get("description", "")).strip()
    user_invoked = bool(fm.get("disable-model-invocation"))

    if user_invoked:
        invocation = "**User-invoked** — invoke it by typing its name."
    else:
        invocation = (
            "**Model-invoked** — the agent runs it automatically when your request matches "
            "the triggers below. You can also invoke it by name."
        )

    lines = [f"# {name}", "", f"> {desc}", "", invocation, ""]

    triggers = parse_triggers(desc)
    lines += ["## When to use", ""]
    if triggers:
        lines += [f"- {t}" for t in triggers]
    else:
        lines.append("Invoke it by name when you need its task.")
    lines.append("")

    steps = step_titles(doc)
    if steps:
        lines += ["## What it does", ""]
        lines += [f"{i}. {title}" for i, title in enumerate(steps, start=1)]
        lines.append("")

    scripts = list_scripts(skill_dir)
    if scripts:
        lines += ["## Scripts", ""]
        lines += [f"- `scripts/{s}`" for s in scripts]
        lines.append("")

    lines += [
        "## Learn more",
        "",
        "- [SKILL.md](SKILL.md) — the full procedure the agent follows.",
        "",
        "---",
        "",
        "*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*",
    ]
    return "\n".join(lines) + "\n"
