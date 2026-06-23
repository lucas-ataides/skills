# secure-sdlc

> Run every deterministic quality and security gate before a change ships, then attest the result. Use when the user wants to ship securely, run all the gates, harden a change before merge, produce a security attestation or SBOM, or prove a build is clean.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- ship securely
- run all the gates
- harden a change before merge
- produce a security attestation
- SBOM
- prove a build is clean

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
