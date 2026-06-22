---
name: secure-sdlc
description: Run every deterministic quality and security gate before a change ships, then attest the result. Use when the user wants to ship securely, run all the gates, harden a change before merge, produce a security attestation or SBOM, or prove a build is clean.
---

Ship a change only after every deterministic gate is green, then record what "green" covered. This skill orchestrates the gates in a fixed order so each run is identical; the commands live in `skill-gate`, never in prose, and the per-gate rationale lives in [the pipeline reference](references/pipeline.md). Mechanical scanning is the floor — the attestation is the artifact that proves the floor was met.

## Steps

1. **Scope the gates.** Run `skill-gate --list` at the repo root to enumerate the gates the detected stacks activate. Confirm the printed list names a gate per supported category across the seven the stack covers (format, lint, types, sast, sca, secrets, test). The step is done when the scope is confirmed against [the pipeline reference](references/pipeline.md).

2. **Pass the quality gates.** Run `skill-gate --category format`, then `--category lint`, then `--category types`, in that order. A non-zero exit blocks the pipeline; fix the source, then rerun the failing category until its exit code is zero. The step is done when format, lint, and types each exit zero.

3. **Pass the security gates.** Run `skill-gate --category sast` (Semgrep), then `--category sca` (trivy or pip-audit), then `--category secrets` (gitleaks), in that order. Record each finding with its severity, rule id, and location. A critical or high finding blocks the merge until the finding is fixed or a waiver is recorded per [the pipeline reference](references/pipeline.md). The step is done when each security category exits zero or carries a recorded waiver.

4. **Pass the test gate.** Run `skill-gate --category test`. A failing suite blocks the change; fix the source, then rerun until the suite exits zero. The step is done when the test category exits zero.

5. **Seal the merge gate.** Run `skill-gate --strict` for the final pass, where a missing tool counts as a failure rather than a silent skip. A red result stops the line (Jidoka); a green result means every category ran on a present tool. The step is done when `skill-gate --strict` exits zero.

6. **Produce the attestation.** Capture the machine-readable gate record with `skill-gate --strict --format json`, generate the SBOM through [supply-chain-audit](../supply-chain-audit/SKILL.md), and record any waiver beside them. Confirm the record names a result per category from step 1. The step is done when the gate record and the SBOM both exist for this change.

See also: [the determinism doctrine](../../meta/foundation/SKILL.md).
