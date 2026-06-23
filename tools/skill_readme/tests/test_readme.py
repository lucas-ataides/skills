"""README generation is deterministic and reflects the SKILL.md."""

from __future__ import annotations

from pathlib import Path

from skill_lint.core import SkillDoc
from skill_readme.cli import main
from skill_readme.core import parse_triggers, render_readme, step_titles


def write_skill(tmp_path: Path, name: str, *, user: bool = False) -> Path:
    folder = tmp_path / name
    folder.mkdir()
    dmi = "disable-model-invocation: true\n" if user else ""
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Does the thing. Use when the user wants to alpha, beta, or gamma.\n{dmi}---\n\n"
        "Intro line.\n\n## Steps\n\n1. **First move.** Do it.\n2. **Second move.** Then stop.\n"
    )
    return folder


def test_parse_triggers():
    t = parse_triggers("Does X. Use when the user wants to add a feature, fix a bug, or refactor.")
    assert t == ["add a feature", "fix a bug", "refactor"]


def test_step_titles(tmp_path):
    folder = write_skill(tmp_path, "demo")
    titles = step_titles(SkillDoc.load(folder / "SKILL.md"))
    assert titles == ["First move.", "Second move."]


def test_render_model_invoked(tmp_path):
    folder = write_skill(tmp_path, "demo")
    out = render_readme(folder)
    assert out.startswith("# demo")
    assert "Model-invoked" in out
    assert "- alpha" in out and "- beta" in out and "- gamma" in out
    assert "1. First move." in out


def test_render_user_invoked(tmp_path):
    folder = write_skill(tmp_path, "demo", user=True)
    assert "User-invoked" in render_readme(folder)


def test_render_is_deterministic(tmp_path):
    folder = write_skill(tmp_path, "demo")
    assert render_readme(folder) == render_readme(folder)


def test_cli_writes_and_check(tmp_path):
    write_skill(tmp_path, "demo")
    assert main([str(tmp_path / "demo")]) == 0
    assert (tmp_path / "demo" / "README.md").is_file()
    # now current -> --check passes
    assert main([str(tmp_path / "demo"), "--check"]) == 0
    # mutate -> --check fails
    (tmp_path / "demo" / "README.md").write_text("stale")
    assert main([str(tmp_path / "demo"), "--check"]) == 1
