---
name: autoguardrails
description: Define and enforce a repository policy with a deterministic scanner — no LLM in the enforcement path. Forbidden patterns (secrets, dangerous calls, banned deps) live as data in POLICY.md; a shell script scans git-tracked files and fails the build on a match. Use when the user wants a policy guardrail, a pre-commit or CI gate for banned patterns, secret-leak prevention, a custom lint rule expressed as a regex, or to block a specific string or API across the repo.
---

Enforce policy with a deterministic scanner, never with model judgment. A policy is a list of forbidden patterns held as data in `POLICY.md`; the scanner reads that data and fails on a match. The same regex yields the same verdict on every run, in pre-commit and in CI alike — the model defines rules, the script enforces them.

The rule syntax, the global-vs-repo layering, the failure modes, and a worked example live in [the policy model](references/policy-model.md). Read that reference before adding a rule.

## Steps

1. **Confirm the scanner is sound.** Run `scripts/check-policy.sh --selftest`. The selftest builds a throwaway policy plus a known-bad and a known-good file, then asserts the match and the miss without touching the real repo. The step is done once the command prints `check-policy selftest: ok` and exits 0.

2. **State what the policy must forbid.** Name the concrete hazard before writing a rule: a leaked secret shape, a dangerous call, a banned dependency or license, a missing required header. A rule without a named hazard guards nothing — so write the hazard down first. The step is done once each intended rule maps to one named hazard.

3. **Express each rule as data.** Add one `DENY <regex> -- <message>` line per hazard to the global `POLICY.md`, or to a repo-local `./POLICY.md` that extends it. The regex is the test; the message tells the author what to fix. The step is done once each named hazard has exactly one DENY line and the file holds no other rule syntax.

4. **Calibrate the regex against real text.** Run the scanner and read every reported violation. A regex that flags a safe line is too broad; a hazard that slips through is too narrow. The step is done once a known violation is caught and no safe line is flagged.

5. **Run the scan.** Run `scripts/check-policy.sh` at the repo root. The scanner reads the policy files, scans the git-tracked files via `git ls-files`, and prints each hit as `path:line: <message>`. The step is done once the command exits 0 (clean) or every printed violation is triaged.

6. **Wire the gate into the pipeline.** Register the scanner as a pre-commit hook and a CI step, both invoking `scripts/check-policy.sh` at the repo root. A policy nobody runs enforces nothing — so a non-zero exit must block the commit and the build. The step is done once a deliberate known-bad line turns the gate red.
