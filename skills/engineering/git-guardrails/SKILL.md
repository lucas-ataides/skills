---
name: git-guardrails
description: Keep git operations safe and deterministic — conventional commits via a script, no destructive history rewrites, branch before committing on a shared branch. Use when the user commits, pushes, rebases, resets, or asks about git workflow.
---

Treat git history as shared state: a wrong push is felt by everyone. Commit through a deterministic helper, never rewrite published history, and confirm before any destructive operation.

## Steps

1. **Check the branch.** Run `git status` and `git branch --show-current`. On a shared branch (main, master, develop), create a feature branch before committing. The step is done once the working branch is unshared, or the user has approved committing directly.

2. **Stage with intent.** Stage only the files the change touches, then read `git diff --staged`. The step is done once the staged set matches the change and nothing unrelated is included.

3. **Commit deterministically.** Run `scripts/git-commit.sh <type> <scope> <subject>` so the message is a validated conventional commit. The step is done once the command prints the committed header.

4. **Guard destruction.** A history rewrite or a working-tree discard runs only with explicit approval, and only on an unshared branch. See [the git rules](references/git-rules.md) for the operations that demand a stop.

5. **Push with care.** Push a feature branch with `--set-upstream` on its first push, and never force-push a shared branch. The step is done once the push succeeds and the branch tracks its remote.
