"""Render a Cursor project rule (.mdc) from a skill's SKILL.md.

Cursor's "Agent Requested" rule — `description` set, `alwaysApply: false`, no globs — is the
same shape as a Claude Code skill: the agent reads the description and decides whether to pull
the rule in. So each SKILL.md maps to exactly one .mdc the Cursor agent invokes by description.

The scripts and references stay in the repo, not copied into `.cursor/rules`; the rule names
their absolute source directory so the Cursor agent can run a script or open a reference.
Deterministic: the same SKILL.md always renders the same .mdc.
"""

from __future__ import annotations

import json
from pathlib import Path

from skill_lint.core import SkillDoc


def strip_frontmatter(raw: str) -> str:
    """Return the SKILL.md body — everything after the leading ``---`` … ``---`` block."""
    lines = raw.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "".join(lines[i + 1 :]).lstrip("\n")
    return raw


def render_mdc(skill_dir: Path) -> str:
    """Render the Cursor .mdc rule for one skill directory."""
    skill_path = skill_dir / "SKILL.md"
    doc = SkillDoc.load(skill_path)
    fm = doc.frontmatter or {}
    name = str(fm.get("name", skill_dir.name))
    desc = str(fm.get("description", "")).strip()
    source = skill_dir.resolve()
    body = strip_frontmatter(skill_path.read_text(encoding="utf-8")).rstrip()

    front = "\n".join(
        [
            "---",
            # json.dumps yields a YAML-safe double-quoted scalar: colons, quotes, and
            # unicode in a description never break the frontmatter.
            f"description: {json.dumps(desc, ensure_ascii=False)}",
            "alwaysApply: false",
            "---",
        ]
    )
    header = (
        f"> **`ataides-skills:{name}`** — ported from a Claude Code skill. Its `scripts/` and "
        f"`references/` live at `{source}`; run a script as `{source}/scripts/<file>`, and the "
        f"relative links below resolve against that directory."
    )
    return f"{front}\n\n{header}\n\n{body}\n"
