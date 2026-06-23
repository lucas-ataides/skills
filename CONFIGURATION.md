# Configuring ldatb skills

Everything configurable lives in one layered TOML file, read by every tool and skill
through `skillkit.config`. This guide is the practical path to set it up locally.

## TL;DR — the one thing most people set

Point the skills at your Obsidian vault so the **second-brain feed** turns on:

```bash
skill-config init                 # seeds ~/.config/skills/skills.toml (if absent)
$EDITOR ~/.config/skills/skills.toml
```

```toml
[vault]
path = "/Users/you/Obsidian/Brain"   # absolute path to your vault
enabled = true                       # turn the feed on
```

```bash
skill-config path                 # prints the vault path -> confirms it is live
```

That is the whole minimum. Everything below is optional refinement.

## The config file

| Layer | Path | Purpose |
|-------|------|---------|
| Global | `~/.config/skills/skills.toml` (or `$XDG_CONFIG_HOME/skills/skills.toml`) | your machine-wide defaults |
| Project | `./skills.toml` (repo root) | per-project overrides, committed with the repo |
| Built-in | — | the defaults below, used when a key is unset |

**Precedence:** project `skills.toml` overrides global, which overrides the built-in
defaults. The merge is per-key (a project file setting only `vault.path` still inherits
everything else).

**Inspect it** (never guess — read the merged result):

```bash
skill-config show            # the full merged config as JSON
skill-config get vault.path  # one dotted key
skill-config path            # the vault path, only if vault.enabled is true
skill-config init            # write the default global file if it does not exist
```

## Keys

The built-in defaults, and what each does:

```toml
[vault]
path = ""          # absolute path to your Obsidian vault
enabled = false    # set true (with a path) to enable the second-brain feed

[second_brain]
feed = true            # opt-out: skills record salient outcomes to the vault
ask_when_unsure = true # ask before recording when relevance is unclear

[gates]
strict = true          # warnings block too (matches `skill-lint --strict`)
```

| Key | Default | Meaning |
|-----|---------|---------|
| `vault.path` | `""` | Absolute path to the vault the second brain reads and writes. |
| `vault.enabled` | `false` | Master switch; the feed is inert until this is `true` and `path` is set. |
| `second_brain.feed` | `true` | Opt-out. With a vault configured, skills append a note for a decision made, a fact learned, a task closed. Set `false` to never write. |
| `second_brain.ask_when_unsure` | `true` | When the value of recording is unclear, the agent asks first instead of writing silently. |
| `gates.strict` | `true` | Treat lint warnings as failures, repo-wide. |

These three sections are honored everywhere: the foundation doctrine routes the
second-brain feed through `vault` + `second_brain`, and the gates read `gates.strict`.

## Enable the second brain

1. Set `vault.path` to your Obsidian vault and `vault.enabled = true` (above). The path is absolute; the folder need not exist yet.
2. Confirm: `skill-config path` prints the path (exit 0). A silent exit 1 means the feed is still off.
3. Bridge the config to the script. The [second-brain](skills/obsidian/second-brain/SKILL.md) skill writes through `scripts/vault.sh`, which reads the `$VAULT` environment variable. The skill exports it for you; for direct CLI use, export it yourself: `export VAULT="$(skill-config path)"` (add that line to your shell profile to make it stick).
4. Make the first note. No scaffold step exists — `vault.sh` creates the vault and its type folders on demand:

   ```bash
   VAULT_SH=skills/obsidian/second-brain/scripts/vault.sh
   bash "$VAULT_SH" capture project "Q3 Roadmap" owner=you   # prints the new note path
   bash "$VAULT_SH" daily                                     # today's daily note
   bash "$VAULT_SH" find "Q3"                                 # locate it again
   ```

   Note types: `person project meeting idea task decision daily client feedback 1on1 company`.
5. From then on, skills record salient outcomes there (opt out with `second_brain.feed = false`), and the simplest path is to just ask Claude — the skill resolves the script and the vault for you.
6. No vault set? Nothing breaks — the feed is skipped silently.

> Building a vault from existing chats, emails, or exports (rather than capturing fresh) is the second brain's **compile** capability — a guarded pipeline with two approval checkpoints and a validator suite. Start it by invoking the [second-brain](skills/obsidian/second-brain/SKILL.md) skill and asking to compile from your sources.

## Per-skill configuration

A skill reads its own settings from a `[skill.<name>]` section via
`skillkit.config.get(cfg, "skill.<name>.<key>")`. Set only what you use; unset keys
fall back to the skill's own default. Common surfaces:

```toml
[skill.brandkit]
primary = "#1a1b1e"      # your brand tokens, reused by design + documents skills
accent  = "#3b5bdb"

[skill.agent-loop]
mode = "checkpointed"    # "checkpointed" (pause for approval) or "autonomous"

[skill.appsec]
block_severity = "high"  # the CVE/finding severity that blocks a merge

[skill.soc-siem]
grafana_url = "https://grafana.internal"   # endpoints, NOT secrets (those stay in a secret manager / env)
```

Secrets never go in `skills.toml` (the secret-scanning gate exists precisely to stop
that) — keep credentials in your OS keychain, a secret manager, or environment
variables, and put only non-secret endpoints/paths here.

## Optional: automation & hooks

These make skills run deterministically without relying on the model to remember.

- **Repo gates (developing this repo):** `make install` registers the pre-commit hooks
  (`skill-lint`, `skill-docs`, `skill-readme`, tests, `ruff`). A violation blocks the commit.
- **autoguardrails in your own project:** add a `POLICY.md` with `DENY <regex> -- <message>`
  rules, then wire the checker into that project's pre-commit:
  `bash <path-to>/skills/engineering/autoguardrails/scripts/check-policy.sh`. No LLM in the path.
- **documentation on every code change:** add a Claude Code `PostToolUse` hook in
  `~/.claude/settings.json` that runs `skill-docs .` after `Edit`/`Write`, so stale links
  surface immediately.
- **deterministic commits:** `skills/engineering/git-guardrails/scripts/git-commit.sh <type> <scope> <subject>`
  validates the conventional-commit format before committing.

## Verify your config

```bash
skill-config show            # the merged result is what tools actually see
skill-config path            # non-empty => the second brain is live
```
