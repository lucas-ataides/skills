# Policy

A policy is a list of forbidden patterns, held as data. The scanner
(`scripts/check-policy.sh`) reads this file, scans the repository's git-tracked
files, and fails the build on any match. No model judgment sits in that path: the
same regex produces the same verdict on every run.

## Rule syntax

One rule per line. Two line kinds carry meaning; the rest is ignored.

```
DENY <regex> -- <message>
# comment
```

- `DENY <regex> -- <message>` — a forbidden pattern. The `<regex>` is an extended
  regular expression (`grep -E`); the `<message>` (everything after the ` -- `
  separator) is what the author sees on a hit.
- A line whose first non-blank character is `#` is a comment.
- A blank line is ignored.

The separator is a literal ` -- ` (space, two hyphens, space). The regex is
everything between `DENY ` and that separator; the message is everything after
it. Keep the regex on one line — a rule does not span lines.

## Layering: global plus repo-local

This file is the **global** policy: the baseline every repository inherits. A
repository may add its own `./POLICY.md` at its root to **extend** the baseline
with project-specific rules (a banned internal module, a deprecated client, a
required license header). The scanner reads both files and applies the union of
their rules. The repo-local file never weakens the global one; it only adds.

Precedence is irrelevant because rules only ever forbid: a pattern denied by
either file is denied. To retire a global rule, edit this file — not the
repo-local one.

## Example rules

These are illustrative starting points. Tune each regex to the repository before
trusting it (see [the policy model](references/policy-model.md) on calibration).

```
# Hardcoded AWS access key id (AKIA + 16 uppercase alphanumerics)
DENY AKIA[0-9A-Z]{16} -- Hardcoded AWS access key id; move it to a secret store.

# Dynamic code execution from a string
DENY eval\( -- Dynamic eval of a string is an injection sink; use a safe parser.

# Inline password assignment
DENY password\s*=\s*['"] -- Inline password literal; read it from the environment.

# Private key material committed to the tree
DENY -----BEGIN[ A-Z]*PRIVATE KEY----- -- Private key in the repo; rotate and remove it.
```

An optional rule some teams enable, to keep authoring markers out of shipped
code:

```
# Authoring marker left in shipped code (optional; noisy in early-stage repos)
DENY \bTODO\b -- Authoring marker in shipped code; resolve or file an issue.
```

## What belongs here

- **Secrets** — key shapes, token prefixes, private-key headers.
- **Dangerous calls** — eval, shelling out with interpolation, unsafe deserialization.
- **Banned dependencies or licenses** — an import or license string the org forbids.
- **Required headers** — express the *absence* via a rule the CI runs separately, or
  keep these as a positive check outside this DENY-only file.

Anything whose verdict needs human judgment does **not** belong here. This file
is for patterns a regex can decide.
