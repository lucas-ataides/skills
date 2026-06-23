"""skill-config — read the layered skills configuration and seed the global default."""

from __future__ import annotations

import argparse
import json

from skillkit import atomic_write
from skillkit.config import get, global_config_path, load_config, vault

DEFAULT_TOML = """\
# ldatb skills configuration.
# Global: ~/.config/skills/skills.toml    Per-project: ./skills.toml (overrides global).

[vault]
# Absolute path to your Obsidian second-brain vault. Leave empty to disable the feed.
path = ""
enabled = false

[second_brain]
# Opt-out: skills record salient outcomes to the vault when one is configured.
feed = true
# When unsure whether something is worth recording, ask before writing.
ask_when_unsure = true

[gates]
# strict = warnings block too (matches `skill-lint --strict`).
strict = true

# Per-skill settings live under [skill.<name>], e.g.
# [skill.brandkit]
# primary = "#1a1b1e"
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-config", description="Read the layered skills configuration."
    )
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("show", help="Print the merged config as JSON.")
    g = sub.add_parser("get", help="Print one dotted key (e.g. vault.path).")
    g.add_argument("key")
    sub.add_parser("path", help="Print the vault path if the second brain is enabled.")
    sub.add_parser("init", help="Seed the global config if absent.")
    args = parser.parse_args(argv)

    cfg = load_config()

    if args.cmd == "show":
        print(json.dumps(cfg, indent=2))
        return 0
    if args.cmd == "get":
        value = get(cfg, args.key)
        if value is None:
            return 1
        print(value if not isinstance(value, dict | list) else json.dumps(value))
        return 0
    if args.cmd == "path":
        v = vault(cfg)
        if v is None:
            return 1
        print(v)
        return 0
    if args.cmd == "init":
        path = global_config_path()
        if path.exists():
            print(f"kept existing {path}")
            return 0
        atomic_write(path, DEFAULT_TOML)
        print(f"created {path}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
