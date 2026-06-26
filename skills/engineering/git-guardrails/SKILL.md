---
name: git-guardrails
description: Keep git operations safe and deterministic — conventional commits via a script, no destructive history rewrites, branch before committing — and cut a release, generating a deterministic CHANGELOG from conventional commits with the SemVer bump. Use when the user commits, pushes, rebases, resets, asks about git workflow, updates the changelog, cuts release notes, or drafts a version.
---

Treat git history as shared state: a wrong push is felt by everyone. Commit through a deterministic helper, never rewrite published history, and confirm before any destructive operation. When cutting a release, the changelog is generated from the commits, never hand-written, so the same history always renders the same notes.

## Steps

1. **Check the branch.** Run `git status` and `git branch --show-current`. On a shared branch (main, master, develop), create a feature branch before committing. The step is done once the working branch is unshared, or the user has approved committing directly.

2. **Stage with intent.** Stage only the files the change touches, then read `git diff --staged`. The step is done once the staged set matches the change and nothing unrelated is included.

3. **Commit deterministically.** Run `skills/engineering/git-guardrails/scripts/git-commit.sh <type> <scope> <subject>` so the message is a validated conventional commit. The step is done once the command prints the committed header.

4. **Guard destruction.** A history rewrite or a working-tree discard runs only with explicit approval, and only on an unshared branch. See [the git rules](references/git-rules.md) for the operations that demand a stop.

5. **Push with care.** Push a feature branch with `--set-upstream` on its first push, and never force-push a shared branch. The step is done once the push succeeds and the branch tracks its remote.

6. **Decide the release version.** To cut a release, read the commit subjects since the previous tag (`previous-tag..HEAD`), then climb the [SemVer ladder](references/conventional-commits.md) to the highest bump any single commit forces: a breaking `!` forces a major, a `feat` forces a minor, a `fix` forces a patch. The step is done once the new version is written down with the one commit that justifies it.

7. **Generate and write the CHANGELOG.** Run `skill-changelog --version <version> --date <YYYY-MM-DD> --from <previous-tag> --to HEAD --write CHANGELOG.md` to prepend a Keep-a-Changelog section — grouped by type with breaking changes first, written atomically above the prior history — then read the rendered section against the raw range to catch a dropped or mis-grouped commit. The step is done once `wrote CHANGELOG.md` prints and the new version sits at the top of the file.

See also [the determinism doctrine](../../meta/foundation/SKILL.md).
