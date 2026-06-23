#!/usr/bin/env python3
"""Zero-install runner for pre-commit: regenerates per-skill READMEs from SKILL.md."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skill_readme.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
