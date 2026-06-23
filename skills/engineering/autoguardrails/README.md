# autoguardrails

> Define and enforce a repository policy with a deterministic scanner — no LLM in the enforcement path. Forbidden patterns (secrets, dangerous calls, banned deps) live as data in POLICY.md; a shell script scans git-tracked files and fails the build on a match. Use when the user wants a policy guardrail, a pre-commit or CI gate for banned patterns, secret-leak prevention, a custom lint rule expressed as a regex, or to block a specific string or API across the repo.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- a policy guardrail
- a pre-commit
- CI gate for banned patterns
- secret-leak prevention
- a custom lint rule expressed as a regex
- to block a specific string
- API across the repo

## What it does

1. Confirm the scanner is sound.
2. State what the policy must forbid.
3. Express each rule as data.
4. Calibrate the regex against real text.
5. Run the scan.
6. Wire the gate into the pipeline.

## Scripts

- `scripts/check-policy.sh`

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
