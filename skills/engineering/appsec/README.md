# appsec

> The security gate every code change passes before it ships — runs the deterministic quality and security gates in a fixed order plus a custom repository-policy scanner (POLICY.md), then attests the result. Use whenever code changes — backend, frontend, infrastructure, Terraform, Kubernetes, Docker, or CI — before merging or shipping; to harden a change, run the gates, enforce a banned-pattern or secret-leak rule, produce an SBOM or attestation, or prove a build is clean.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

Invoke it by name when you need its task.

## What it does

1. Scope the gates.
2. Pass the quality gates.
3. Pass the security gates.
4. Enforce the repository policy.
5. Pass the test gate.
6. Seal the merge gate.
7. Produce the attestation.

## Scripts

- `scripts/check-policy.sh`

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
