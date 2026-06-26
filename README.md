# Agent Skills

**Deterministic Claude skills, built to a manufacturing standard.**

[![ci](https://github.com/lucas-ataides/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-ataides/skills/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A skill exists to wring **determinism** out of a stochastic system: the agent takes
the *same process* every run. This repository treats that as an engineering problem,
not a prompting one, and solves it the way a factory solves defects, by building
quality in rather than inspecting it afterward.

## The thesis

An agent follows a process written in human language, and human language is full of
ambiguity. "Clean up the old files and make sure there are no collisions" can mean
three different things, including *delete everything first*. The agent's quality does
not fix this; the **language** is the problem.

So we move work out of the model and into deterministic tools:

- **Scripts** do the work the model would otherwise improvise.
- **Linters** enforce the rules the model would otherwise forget.
- **Guarded primitives** make the dangerous interpretation *impossible*, not merely
  discouraged.

You use the model once, to *author* these tools, then run them deterministically
forever. Cheaper, faster, and identical every time.

This is **Poka-yoke** (mistake-proofing) and **Jidoka** (stop the line on a defect)
applied to agent skills. The full doctrine lives in
[`skills/meta/foundation`](skills/meta/foundation/SKILL.md).

## Install

1. the CLIs the skills call (skill-lint, skill-new, skill-gate, skill-changelog, skill-docs, skill-update, skill-config, skill-readme, skill-cursor)

  ```bash
  git clone https://github.com/lucas-ataides/skills.git && cd skills
  ./scripts/install.sh                       # uv tool install from the clone; re-run to update
  ```

2. the skills, as a Claude Code plugin

  ```bash
  /plugin marketplace add lucas-ataides/skills
  /plugin install ataides-skills@ataides-skills
  ```

`skill-update` reports when a newer tagged release exists.

## Configure

Point the skills at your Obsidian vault (and tune the rest) in `~/.config/skills/skills.toml`:

```bash
skill-config init      # seed the global config (~/.config/skills/skills.toml)
skill-config path      # prints the vault path once it is enabled
```

The full guide — every key, the second-brain feed, per-skill `[skill.<name>]` settings,
and the optional hooks — is in [CONFIGURATION.md](CONFIGURATION.md).

## Develop

```bash
make install        # uv sync + pre-commit hooks
make lint           # skill-lint --strict over every skill
make docs           # skill-docs — every Markdown link resolves
make readme         # skill-readme — regenerate the per-skill READMEs
make test           # the toolchain's own test suite
```

Skills are standard `SKILL.md` files under `skills/`, organized by domain.

## How it works

### The determinism ladder

Climb until a rung holds, then stop — the model is the last resort, not the first:

1. **Script / existing tool** can do it → call it.
2. **Validator** can check it → gate on it.
3. **Primitive** exists for the hazard → use `skillkit`.
4. **Model** gets only the irreducibly creative remainder.

### skill-lint — a deterministic reviewer for skills

Instead of asking an agent to re-read a skill for ambiguity (slow, nondeterministic,
expensive), a linter checks it identically every time. It flags unanchored pronouns,
unbounded "for-each" scope (context explosion), compound conditionals, inlined
destructive commands, collision-prone file creation, and uncheckable completion
criteria. Rules are **data** in
[`tools/skill_lint/rules.yaml`](tools/skill_lint/rules.yaml) — adding a case is a
data edit plus a test, never a rewrite (**Kaizen**).

```bash
skill-lint --strict skills/      # the gate; runs in pre-commit and CI
```

### skillkit — guarded primitives

Skills call these instead of describing file operations in prose:

| Primitive | Guarantee |
| --------- | --------- |
| `unique_path` | Collision-free name, atomic `O_CREAT\|O_EXCL`, safe under concurrency |
| `atomic_write` | A reader never sees a half-written file |
| `safe_remove` | Refuses anything outside its root, refuses the root, never recurses |

### skill-new — born conformant

```bash
make new-skill CATEGORY=engineering NAME=my-skill
```

Generates a lint-clean `SKILL.md` and registers it in the manifest, so a malformed
skill cannot be created by hand (**Poka-yoke** at authoring time).

## Repository layout

```bash
skills/                 # 47 skills, by domain (each with a generated README.md)
  meta/                 # foundation, creating-skills, setup, cavecrew
  engineering/          # appsec, tdd, code-review, engineering (app+infra+qa),
                        # software-architecture, git-guardrails, autoguardrails, agent-loop,
                        # subagent-driven-development, project-context, changelog-gen, documentation, to-issues
  quality/              # verification-before-completion, polish, overdrive, full-output-enforcement
  marketing/            # copywriting, content, growth, outreach
  design/               # frontend-design (Swiss-editorial × brutalism), brandkit
  documents/            # docx, pdf, pptx, xlsx (beautiful, deterministic generation)
  cloud/                # aws-toolkit, azure-toolkit, gcp-toolkit, cloud-best-practices, soc-siem
  obsidian/             # second-brain (capture · compile · retrieve · maintain)
  management/           # project-management, client-satisfaction, employee-management
  productivity/         # brainstorm, caveman, grill-me, handoff, linear, teach
tools/                  # the deterministic toolchain (Python): skill_lint, skill_new, skill_gate,
                        # skill_changelog, skill_docs, skill_update, skill_config, skill_readme, skillkit
scripts/                # install.sh
.claude-plugin/         # marketplace.json + plugin.json
.github/workflows/      # CI: determinism gate, docs, READMEs, tests, ruff, Semgrep
```

## Categories

47 skills across 10 domains, every one lint-gated and carrying a generated README.md. The taxonomy grows as skills land — no empty folders.

| Domain | What lives here |
| ------ | --------------- |
| `meta` | Foundation doctrine, skill-authoring, install/setup, the cavecrew subagent protocol |
| `engineering` | AppSec (the gate every code change passes), TDD, code review, full-stack engineering, software + cloud architecture, git/auto guardrails, the agent loop, project-context, changelog, documentation, to-issues |
| `quality` | Verification-before-completion, polish, overdrive, full-output enforcement |
| `marketing` | copywriting, content, growth, outreach |
| `design` | frontend-design (Swiss-editorial × brutalism) + brandkit |
| `documents` | Beautiful deterministic pptx, pdf, docx, xlsx generation |
| `cloud` | AWS / Azure / GCP toolkits (each to its own framework), cloud-best-practices (SOC2), soc-siem (Wazuh/Suricata/Grafana) |
| `obsidian` | second-brain: source-backed vault compiler + fast CRUD + retrieval |
| `management` | Project management, client satisfaction, people management |
| `productivity` | brainstorm, caveman, grill-me, handoff, linear, teach |

## Authoring a skill

Read [the foundation doctrine](skills/meta/foundation/SKILL.md), then follow
[`creating-skills`](skills/meta/creating-skills/SKILL.md): scaffold → write to the
doctrine → `make lint` green → `make test` green → commit. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Quality gates

Every change passes the same gates locally (pre-commit) and in CI (**Jidoka** — a
violation is a red build, not a warning):

- `skill-lint --strict` — the determinism gate
- `skill-docs` — every Markdown link resolves
- `skill-readme --check` — the per-skill READMEs are current
- `pytest` — the toolchain test suite
- `ruff` — Python lint/format
- `semgrep` — static analysis (SCA) on the toolchain

## License

[MIT](LICENSE).
