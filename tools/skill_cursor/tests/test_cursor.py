from skill_cursor.cli import discover, main, selftest
from skill_cursor.core import render_mdc, strip_frontmatter


def test_selftest_passes():
    assert selftest() == 0


def test_strip_frontmatter():
    assert strip_frontmatter("---\nname: x\n---\n\nbody here\n") == "body here\n"
    assert strip_frontmatter("no frontmatter\n") == "no frontmatter\n"


def test_render_is_agent_requested(tmp_path):
    d = tmp_path / "alpha"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: Build things. Use when the user builds.\n---\n\nDo the work.\n",
        encoding="utf-8",
    )
    out = render_mdc(d)
    assert out.startswith("---\n")
    assert "alwaysApply: false" in out
    assert "description: " in out
    assert "Do the work." in out
    assert str(d.resolve()) in out  # source dir for scripts/references


def test_description_with_colon_is_quoted(tmp_path):
    d = tmp_path / "beta"
    d.mkdir()
    (d / "SKILL.md").write_text(
        '---\nname: beta\ndescription: "Memory: capture and recall."\n---\n\nBody.\n',
        encoding="utf-8",
    )
    out = render_mdc(d)
    assert 'description: "Memory: capture and recall."' in out


def test_cli_writes_one_mdc_per_skill(tmp_path):
    root = tmp_path / "skills" / "dom"
    for n in ("beta", "gamma"):
        (root / n).mkdir(parents=True)
        (root / n / "SKILL.md").write_text(
            f"---\nname: {n}\ndescription: {n} skill.\n---\n\nBody.\n", encoding="utf-8"
        )
    out = tmp_path / "rules"
    assert main([str(out), str(tmp_path / "skills")]) == 0
    assert (out / "beta.mdc").is_file() and (out / "gamma.mdc").is_file()
    assert "alwaysApply: false" in (out / "beta.mdc").read_text(encoding="utf-8")


def test_prune_removes_only_stale_generated_rules(tmp_path):
    root = tmp_path / "skills" / "dom" / "keep"
    root.mkdir(parents=True)
    (root / "SKILL.md").write_text(
        "---\nname: keep\ndescription: keep skill.\n---\n\nBody.\n", encoding="utf-8"
    )
    out = tmp_path / "rules"
    out.mkdir()
    (out / "stale.mdc").write_text(
        "---\n---\n\n> old rule, ported from a Claude Code skill.\n", encoding="utf-8"
    )
    (out / "hand.mdc").write_text("---\n---\n\nmine, keep out\n", encoding="utf-8")
    assert main([str(out), str(tmp_path / "skills"), "--prune"]) == 0
    assert not (out / "stale.mdc").exists()
    assert (out / "hand.mdc").is_file()
    assert (out / "keep.mdc").is_file()


def test_discover_dedupes(tmp_path):
    d = tmp_path / "skills" / "x" / "one"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: one\ndescription: d\n---\n\nb\n", encoding="utf-8")
    assert discover([str(tmp_path / "skills"), str(d)]).count(d) == 1
