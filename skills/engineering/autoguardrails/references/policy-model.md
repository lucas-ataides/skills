# The policy model

This is the deep reference for autoguardrails. The skill procedure lives in
[../SKILL.md](../SKILL.md); the global rule list lives in
[../POLICY.md](../POLICY.md). Read this before adding or changing a rule.

The governing principle is the determinism doctrine: **no model judgment sits in
the enforcement path**. A policy is data; the scanner is a deterministic function
of that data and the repository's files. The model may *write* a rule, but a
regex — not a model — decides every verdict. The same inputs yield the same
result in pre-commit, in CI, and on a laptop offline.

## Rule syntax

One rule per line. The scanner (`scripts/check-policy.sh`) recognizes exactly
three line kinds:

```
DENY <regex> -- <message>
# comment
<blank>
```

- **DENY rule.** `DENY ` (literal, with the trailing space), then an extended
  regular expression, then the literal separator ` -- ` (space, two hyphens,
  space), then a free-text message.
- **Comment.** A line whose first non-blank character is `#`.
- **Blank.** Ignored.

A line that is none of these is ignored by design, so prose around the rules does
no harm. A line that starts with `DENY ` but lacks the ` -- ` separator is a
hard error — the scanner exits non-zero rather than guess where the regex ends.

### Parsing semantics

The regex is the text **before the first** ` -- `; the message is everything
**after the first** ` -- `. A message may itself contain ` -- `; the regex may
not, because the split is on the first occurrence. The regex is passed verbatim
to `grep -nIE` (extended regex, line numbers, binary files skipped). Escaping is
the author's responsibility: a literal `(` is written `\(`, a literal `.` is
written `\.`.

## What belongs in policy

A rule earns its place only when a regex can decide the verdict without context:

| Category | Example hazard | Example DENY regex |
|----------|----------------|--------------------|
| Secrets | Hardcoded cloud key | `AKIA[0-9A-Z]{16}` |
| Secrets | Private key in tree | `-----BEGIN[ A-Z]*PRIVATE KEY-----` |
| Dangerous calls | Dynamic eval | `eval\(` |
| Dangerous calls | Shell with interpolation | `os\.system\(` |
| Banned deps | Forbidden import | `import\s+requests_unsafe` |
| Banned licenses | Copyleft string | `GNU GENERAL PUBLIC LICENSE` |
| Authoring markers | Marker in shipped code | `\bTODO\b` (optional, noisy) |

What does **not** belong: anything whose verdict needs judgment — "is this
abstraction right", "is this name good", "is this the correct algorithm". Those
are review questions for [the code-review skill](../../code-review/SKILL.md), not
regex questions. A policy that tries to encode judgment produces false positives
and trains the team to ignore it.

## Global vs repo-local layering

Two files, unioned:

- **Global `POLICY.md`** — shipped beside this skill; the baseline every
  repository inherits. Owns the org-wide hazards: secret shapes, banned licenses,
  universally dangerous calls.
- **Repo-local `./POLICY.md`** — optional, at a repository's root. **Extends** the
  baseline with project-specific rules: a deprecated internal client, a banned
  module, a required-header check.

The scanner reads both and applies every rule from either. A repo-local file
**cannot weaken** the global one, because the syntax only ever forbids — there is
no ALLOW that subtracts. To retire a global rule, edit the global file. This is
the same data-edit discipline the foundation calls **Kaizen**: a policy change is
a one-line edit to data, reviewed in a normal diff, never a code change to the
scanner.

## How to add a rule

1. **Name the hazard.** Write down the concrete thing being forbidden and why a
   regex can decide it. A rule without a named hazard is noise.
2. **Write one DENY line.** Add `DENY <regex> -- <message>` to the global
   `POLICY.md` (org-wide) or the repo-local `./POLICY.md` (project-specific). The
   message must tell the author what to do, not merely that they erred.
3. **Calibrate.** Run `scripts/check-policy.sh` and read every hit. Widen or
   narrow the regex until a known-bad line is caught and no safe line is flagged.
4. **Prove it red, then green.** Add a deliberate known-bad line, confirm a
   non-zero exit, remove the line, confirm a zero exit.

## Failure modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Regex too broad | Safe lines flagged; team adds blanket suppressions | Anchor the pattern; add boundaries (`\b`), require more context |
| Regex too narrow | Real hazard slips through | Generalize the shape; test against a real positive sample |
| Policy nobody runs | Green build, leaked secret in prod | Wire the scanner into pre-commit **and** CI; a local-only gate is theater |
| Message unactionable | Author sees a hit, does not know the fix | Rewrite the message as an instruction |
| Binary / generated noise | Hits in vendored or build output | `grep -I` already skips binaries; exclude generated paths from `git ls-files` via `.gitattributes` or a path filter |
| Suppression sprawl | Many inline opt-outs | A flood of suppressions means the rule is wrong — fix the regex, not the call sites |

### Red flags

- A rule whose message is "fix this" with no instruction.
- A regex with no anchor or boundary that matches a common substring.
- A repo-local file that tries to *disable* a global rule (impossible by design,
  but a sign someone wants to weaken the baseline — discuss the global rule
  instead).
- A policy that has never failed a build — either nothing hazardous has been
  written, or the gate is not actually wired in. Verify the latter.
- A rule encoding judgment ("ban ugly names") rather than a decidable pattern.

## Wiring into pre-commit and CI

The scanner is a single command with a meaningful exit code, so it drops into any
runner. Invoke it at the repository root so `git ls-files` sees the whole tree.

Pre-commit (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: local
    hooks:
      - id: autoguardrails
        name: policy scan
        entry: skills/engineering/autoguardrails/scripts/check-policy.sh
        language: system
        pass_filenames: false
```

CI (GitHub Actions step):

```yaml
- name: Policy scan
  run: skills/engineering/autoguardrails/scripts/check-policy.sh
```

Both fail the job on a non-zero exit. This is **Jidoka**: the line stops on a
defect rather than passing it downstream.

## Worked example: adding a rule and catching a violation

A team bans the synchronous `child_process.execSync` call because it blocks the
event loop and is a common shell-injection sink.

1. **Add the rule** to the repo-local `./POLICY.md`:

   ```
   DENY child_process\.execSync\( -- execSync blocks and is an injection sink; use execFile with an argv array.
   ```

2. **Introduce a violation** in a tracked file, `src/deploy.js`:

   ```js
   const { execSync } = require("child_process");
   execSync(`tar -czf ${name}.tgz ${dir}`);
   ```

3. **Run the scanner** at the repo root:

   ```sh
   skills/engineering/autoguardrails/scripts/check-policy.sh
   ```

   It prints the hit and exits non-zero:

   ```
   src/deploy.js:2: execSync blocks and is an injection sink; use execFile with an argv array.
   ```

4. **Fix the call** to use an argv array, re-run, and the scanner prints
   `check-policy: clean` and exits 0. The gate that blocked the commit now passes
   — no model was consulted at any point.
