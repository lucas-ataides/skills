# appsec

> The security gate every code change passes before it ships — runs the deterministic quality and security gates in a fixed order, then attests the result. Use whenever code changes — backend, frontend, infrastructure, Terraform, Kubernetes, Docker, CI config, or any other code — before merging or shipping; to harden a change, run all the gates, produce an SBOM or attestation, or prove a build is clean.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

Invoke it by name when you need its task.

## What it does

1. Scope the gates.
2. Pass the quality gates.
3. Pass the security gates.
4. Pass the test gate.
5. Seal the merge gate.
6. Produce the attestation.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
