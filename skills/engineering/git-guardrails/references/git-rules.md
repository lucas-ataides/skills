# Git rules

Git history is shared state. These rules keep a change from corrupting it. The
deterministic commit helper (`scripts/git-commit.sh`) handles message format; this page
covers the operations a human must approve and how to recover when one goes wrong.

## Operations that demand a stop

Each of these rewrites history or destroys uncommitted work. Run only with explicit
approval, only on an unshared branch, never on `main`/`master`/`develop`:

| Operation | Why it is dangerous | Safer default |
|-----------|---------------------|---------------|
| `git push --force` | Overwrites remote history others have pulled | `--force-with-lease`, and only on your own branch |
| `git reset --hard` | Discards uncommitted work irrecoverably | `git stash` first; commit a WIP instead |
| `git clean -fd` | Deletes untracked files with no undo | `git clean -nd` (dry run) first |
| `git rebase` of pushed commits | Rewrites shared history | rebase only local, unpushed commits |
| `git branch -D` | Force-deletes an unmerged branch | `git branch -d` (refuses if unmerged) |
| `git commit --amend` of a pushed commit | Diverges from the remote | amend only local, unpushed commits |
| `git filter-branch` / history surgery | Rewrites the whole history | a dedicated, reviewed, announced operation |

Red flags: a force-push to a protected branch; a reset that throws away a colleague's
work; a rebase that rewrites commits already on the remote; "let me just clean the tree"
without a dry run.

## Commit discipline

- One logical change per commit. A commit that does two things cannot be reverted cleanly.
- Conventional format via `scripts/git-commit.sh <type> <scope> <subject>` — the script
  validates the type, rejects an empty or period-terminated subject, and caps the subject
  at 72 characters. Run `git-commit.sh --selftest` to confirm the validator.
- The body explains *why*, not *what* — the diff already shows what changed.
- Never commit secrets; the secrets gate (`skill-gate --category secrets`) is the backstop, not the first line.

## Branch discipline

- Branch off the default branch before work; do not commit straight to a shared branch.
- Name the branch for the change (`feat/token-refresh`, `fix/off-by-one`).
- First push sets upstream: `git push --set-upstream origin <branch>`.
- Open a PR for review; the gates run in CI before merge.

## Recovery

Almost nothing is truly lost while the commit is in the reflog.

- Recover a lost commit: `git reflog`, find the hash, `git checkout -b rescue <hash>`.
- Undo a bad merge not yet pushed: `git reset --hard ORIG_HEAD` (with approval, on your branch).
- Restore a file from the last commit: `git restore --source=HEAD -- <path>`.

Worked example — a force-push was about to overwrite a teammate's commits: the operation
stops at the guard, the user fetches and rebases the local branch onto the remote
instead, resolves the divergence, and pushes with `--force-with-lease` on the feature
branch only. The shared branch is never force-pushed.
