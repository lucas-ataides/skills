"""Layered skills configuration.

A global config (`~/.config/skills/skills.toml`) is overlaid by a per-project
`./skills.toml`, which is overlaid on built-in defaults. Skills read configurable
values (the vault path, the second-brain feed, gate strictness, per-skill settings)
through this loader instead of hardcoding them.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "vault": {"path": "", "enabled": False},
    "second_brain": {"feed": True, "ask_when_unsure": True},
    "gates": {"strict": True},
}


def global_config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "skills" / "skills.toml"


def _read(path: Path) -> dict:
    try:
        if path.is_file():
            return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return {}


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(*, global_path: Path | None = None, project_path: Path | None = None) -> dict:
    """Return defaults overlaid by the global config overlaid by the project config."""
    g = _read(global_path if global_path is not None else global_config_path())
    p = _read(project_path if project_path is not None else Path("skills.toml"))
    return _merge(_merge(DEFAULTS, g), p)


def get(cfg: dict, dotted: str, default: Any = None) -> Any:
    """Read a dotted key (e.g. 'vault.path') from a loaded config."""
    cur: Any = cfg
    for key in dotted.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def vault(cfg: dict) -> Path | None:
    """The vault path if the second brain is enabled and set, else None (feed skipped)."""
    if not get(cfg, "vault.enabled", False):
        return None
    raw = str(get(cfg, "vault.path", "") or "").strip()
    return Path(raw).expanduser() if raw else None
