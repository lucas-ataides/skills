"""The layered config merges global < project over defaults, and resolves the vault."""

from __future__ import annotations

from pathlib import Path

from skillkit.config import get, load_config, vault


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_defaults_when_no_files(tmp_path):
    cfg = load_config(global_path=tmp_path / "none.toml", project_path=tmp_path / "none2.toml")
    assert get(cfg, "second_brain.feed") is True
    assert get(cfg, "vault.enabled") is False


def test_global_overrides_defaults(tmp_path):
    g = _write(tmp_path / "g.toml", '[vault]\npath = "/vault"\nenabled = true\n')
    cfg = load_config(global_path=g, project_path=tmp_path / "none.toml")
    assert get(cfg, "vault.path") == "/vault"
    assert get(cfg, "vault.enabled") is True
    # untouched keys keep their defaults
    assert get(cfg, "second_brain.feed") is True


def test_project_overrides_global(tmp_path):
    g = _write(tmp_path / "g.toml", '[vault]\npath = "/global"\nenabled = true\n')
    p = _write(tmp_path / "skills.toml", '[vault]\npath = "/project"\n')
    cfg = load_config(global_path=g, project_path=p)
    assert get(cfg, "vault.path") == "/project"
    assert get(cfg, "vault.enabled") is True  # inherited from global


def test_get_missing_returns_default(tmp_path):
    cfg = load_config(global_path=tmp_path / "n.toml", project_path=tmp_path / "n2.toml")
    assert get(cfg, "nope.missing", "fallback") == "fallback"


def test_malformed_toml_falls_back(tmp_path):
    g = _write(tmp_path / "bad.toml", "this is = = not valid toml [[[")
    cfg = load_config(global_path=g, project_path=tmp_path / "n.toml")
    assert get(cfg, "second_brain.feed") is True  # defaults intact


def test_vault_none_when_disabled(tmp_path):
    g = _write(tmp_path / "g.toml", '[vault]\npath = "/vault"\nenabled = false\n')
    cfg = load_config(global_path=g, project_path=tmp_path / "n.toml")
    assert vault(cfg) is None


def test_vault_path_when_enabled(tmp_path):
    g = _write(tmp_path / "g.toml", '[vault]\npath = "~/vault"\nenabled = true\n')
    cfg = load_config(global_path=g, project_path=tmp_path / "n.toml")
    v = vault(cfg)
    assert v is not None and v.name == "vault"
