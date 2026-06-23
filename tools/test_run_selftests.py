"""The selftest gate discovers self-testing scripts and branches on exit codes."""

from __future__ import annotations

from pathlib import Path

from run_selftests import discover, run


def _script(dir_: Path, name: str, body: str) -> Path:
    scripts = dir_ / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    p = scripts / name
    p.write_text(body, encoding="utf-8")
    return p


def test_discover_only_finds_selftesting_scripts(tmp_path):
    _script(tmp_path / "a", "has.sh", "#!/usr/bin/env bash\n# --selftest supported\n")
    _script(tmp_path / "b", "none.sh", "#!/usr/bin/env bash\necho hi\n")
    found = discover([tmp_path])
    assert [p.name for p in found] == ["has.sh"]


def test_run_passes_when_script_exits_zero(tmp_path):
    _script(tmp_path / "a", "ok.sh", 'case "$1" in --selftest) exit 0;; esac\n')
    assert run([tmp_path]) == 0


def test_run_fails_when_script_exits_nonzero(tmp_path):
    _script(tmp_path / "a", "bad.sh", 'case "$1" in --selftest) exit 1;; esac\n')
    assert run([tmp_path]) == 1
