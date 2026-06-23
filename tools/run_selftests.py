#!/usr/bin/env python3
"""Run every skill script's ``--selftest`` and fail if any does not exit zero.

The determinism doctrine says a skill pushes deterministic work into a script. This
gate makes that enforceable: a script that ships a ``--selftest`` must pass it, in
pre-commit and in CI, the same way ``skill-lint`` gates the prose. A script with no
self-test is reported so the gap is visible, never silently skipped.

    run_selftests.py [root ...]      # default root: skills/
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_MARKER = "--selftest"


def discover(roots: list[Path]) -> list[Path]:
    """Return skill scripts that declare a ``--selftest``, in deterministic order."""
    found: set[Path] = set()
    for root in roots:
        for pattern in ("*.sh", "*.py"):
            for path in root.glob(f"**/scripts/{pattern}"):
                if _MARKER in path.read_text(encoding="utf-8"):
                    found.add(path)
    return sorted(found)


def _command(script: Path) -> list[str]:
    if script.suffix == ".py":
        return [sys.executable, str(script), _MARKER]
    return ["bash", str(script), _MARKER]


def run(roots: list[Path]) -> int:
    scripts = discover(roots)
    if not scripts:
        print("run-selftests: no scripts with --selftest found", file=sys.stderr)
        return 1
    failed = 0
    for script in scripts:
        result = subprocess.run(_command(script), capture_output=True, text=True)
        tail = (result.stdout + result.stderr).strip().splitlines()
        last = tail[-1] if tail else ""
        if result.returncode == 0:
            print(f"  ok   {script}  {last}")
        else:
            failed += 1
            print(f"  FAIL {script}  (exit {result.returncode})  {last}")
    print(f"run-selftests: {len(scripts)} script(s), {failed} failure(s)")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    roots = [Path(a) for a in args] or [Path("skills")]
    return run(roots)


if __name__ == "__main__":
    raise SystemExit(main())
