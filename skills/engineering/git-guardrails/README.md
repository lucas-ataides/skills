# git-guardrails

> Keep git operations safe and deterministic — conventional commits via a script, no destructive history rewrites, branch before committing — and cut a release, generating a deterministic CHANGELOG from conventional commits with the SemVer bump. Use when the user commits, pushes, rebases, resets, asks about git workflow, updates the changelog, cuts release notes, or drafts a version.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- commits
- pushes
- rebases
- resets
- asks about git workflow
- updates the changelog
- cuts release notes
- drafts a version

## What it does

1. Check the branch.
2. Stage with intent.
3. Commit deterministically.
4. Guard destruction.
5. Push with care.
6. Decide the release version.
7. Generate and write the CHANGELOG.

## Scripts

- `scripts/git-commit.sh`

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
