---
name: caveman-review
description: Code review delivered in terse caveman style — findings only, no preamble. Type /caveman-review to apply it.
disable-model-invocation: true
---

Review the change. Report findings terse, like a smart caveman. No preamble, no praise.

## Steps

1. **Read the diff.** Identify the changed files under review. The scope is set once the file set is known.

2. **Find issues.** Check correctness, security, and tests. Each issue gets one line: `file:line — problem. fix.`

3. **Rank.** Mark each issue blocker, major, or minor, and order blocker first.

4. **Report.** List findings only; skip what passed. The review is done once every changed file has been read.
