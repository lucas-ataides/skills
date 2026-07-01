---
title: "Toolchain and gates"
type: system
updated: 2026-07-01
sources: [pyproject.toml, Makefile, .pre-commit-config.yaml, ".github/workflows/ci.yml"]
---

# Toolchain and gates

Python (uv, ≥3.11), all under `tools/`, exposed as `skill-*` CLIs via `uv tool install`.

| CLI | Job |
|---|---|
| `skill-lint` | the determinism gate — rules as data in `rules.yaml` (SK001–SK080) |
| `skill-new` | scaffold + register a lint-clean skill (never author by hand) |
| `skill-gate` | per-stack quality/security gates (format→lint→types→sast→sca→secrets→test) |
| `skill-docs` | every Markdown link resolves |
| `skill-readme` | generated per-skill READMEs, `--check` gate |
| `skill-cursor` | export skills as Cursor `.mdc` rules; `--prune` removes stale generated ones |
| `skill-changelog` | Keep-a-Changelog section from conventional commits |
| `skill-config` | layered config (`~/.config/skills/skills.toml` + `./skills.toml`) — vault path |
| `skill-update` | installed-vs-latest-tag check |

`skillkit` is the primitive layer: `unique_path`, `atomic_write`, `safe_remove` (refuses
outside-root, refuses root, never recurses).

**Where the gates run — pre-commit and CI, identical:** `skill-lint --strict skills/`,
`skill-docs .`, `skill-readme --check`, `pytest` (tools tests + the manifest-drift gate),
`run_selftests.py skills/ hooks/` (every script's `--selftest`, including the router hook),
`ruff` + `ruff format`. A script without a selftest is reported, never silently skipped.

**Gotcha:** a machine-level hook (trailofbits modern-python) shims `python3` — everything
runs as `uv run python3`, and hooks in settings.json must use absolute interpreter paths.

## Related
- [[determinism-doctrine]] · [[architecture]] · [[plugin-distribution]]
