---
title: "Architecture map"
type: system
updated: 2026-07-01
sources: [Makefile, .pre-commit-config.yaml, ".github/workflows/ci.yml", .claude-plugin/plugin.json]
---

# Architecture map

The system at a glance. One pipeline: skills are **authored** against a doctrine, **gated**
deterministically, **distributed** as a plugin (and as Cursor rules), and **consumed** at
runtime by agents that read/write memory in both directions.

```mermaid
graph TD
  subgraph authoring [Authoring]
    NEW["skill-new (make new-skill)"] --> SK["skills/&lt;domain&gt;/&lt;name&gt;/<br/>SKILL.md + references/ + scripts/"]
    NEW -->|registers| MAN[".claude-plugin/plugin.json"]
    FOUND["meta/foundation<br/>(determinism doctrine)"] -.inherited by.-> SK
  end

  subgraph gates [Gates — pre-commit AND CI, identical]
    LINT["skill-lint --strict"]
    DOCS["skill-docs (links)"]
    RDME["skill-readme --check"]
    PYT["pytest tools/ (incl. manifest-drift)"]
    SELF["run_selftests (every script --selftest, skills/ + hooks/)"]
  end
  SK --> gates
  MAN --> PYT

  subgraph distribution [Distribution]
    GH["github.com/lucas-ataides/skills"] -->|"SHA-versioned (no version pin)"| PLUG["Claude Code plugin<br/>ataides-skills"]
    SK -->|"skill-cursor (--prune)"| CUR["Cursor .cursor/rules/*.mdc"]
    PCTX["project-context.sh bootstrap"] --> REPO["any repo: AGENTS.md + TODO.md + .brain/"]
  end
  gates -->|green| GH

  subgraph runtime [Runtime]
    ROUTER["hooks/skill-router.sh<br/>(UserPromptSubmit)"] -->|"nudge: invoke skill + prime"| AGENT["agent session<br/>(Claude Code / Cursor)"]
    AGENT -->|"prime: vault.sh find"| VAULT[("Obsidian second brain<br/>(personal)")]
    AGENT -->|"feed: vault.sh capture"| VAULT
    AGENT -->|read/update| BRAIN[(".brain/ per repo<br/>(project)")]
  end
  PLUG --> ROUTER
```

## Entry points
- `make lint|docs|readme|test|sca` — the gate targets; `make new-skill CATEGORY=x NAME=y`.
- `skill-*` CLIs on PATH via `uv tool install` (`scripts/install.sh`).
- `hooks/skill-router.sh` — fires on every prompt once the plugin is installed.
- Per-skill scripts under `skills/*/*/scripts/` — every one exposes `--selftest`.

## Boundaries
- **Prose never mutates.** A SKILL.md describes; a script executes. Destruction only through
  guarded helpers (`skillkit.safe_remove`, `vault.sh rm`, `check-policy.sh`).
- **Secrets live in env only** (`LINEAR_API_KEY`), never in `skills.toml` — the secret-scan
  gate is the backstop.
- **plugin.json is written by the scaffolder** and pruned by hand; the drift test makes
  manifest ≡ disk ≡ README count a hard gate.
- **The vault path resolves through `skill-config`** (`~/.config/skills/skills.toml`), never
  hardcoded.

## How to work here
- New skill: `make new-skill …`, then follow `meta/creating-skills`. Never author by hand.
- Any edit: `make lint && make test` must be green before done (Jidoka — red gate = not done).
- Push: after every push, refresh the installed plugin (`claude plugin marketplace update
  ataides-skills && claude plugin update ataides-skills@ataides-skills`) — updates apply on
  restart.
- Commit subjects ≤ 72 chars via `git-commit.sh` (it rejects longer).
