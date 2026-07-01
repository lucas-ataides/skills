---
name: setup
description: Install or update the lucas-ataides skills and their toolchain. Use when the user says "install lucas-ataides skills", wants to set up or update the skills, or install the CLIs.
---

Install the lucas-ataides skills and the CLI toolchain they call. The skills install as a Claude Code plugin; the CLIs install through a script. Both come from the same repository.

## Steps

1. **Locate the repository.** Confirm a clone of `github.com/lucas-ataides/skills` on disk, or clone it. The step is done once the repo path is known.

2. **Install the CLIs.** Run `./scripts/install.sh` from the repo root. The script installs the full `skill-*` command toolchain onto PATH through uv. The step is done once `skill-lint --version` prints a version.

3. **Add the skills marketplace.** The user runs `/plugin marketplace add lucas-ataides/skills`, then `/plugin install ataides-skills@ataides-skills`. These two commands are interactive, so the user runs them once. The step is done once the plugin shows as installed.

4. **Verify.** Run `skill-lint --version`, then `skill-update`. The setup is done once the CLIs resolve and `skill-update` reports the installed version against the latest tag.
