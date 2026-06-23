---
name: appsec
description: The security gate every code change passes before it ships — runs the deterministic quality and security gates in a fixed order, then attests the result. Use whenever code changes — backend, frontend, infrastructure, Terraform, Kubernetes, Docker, CI config, or any other code — before merging or shipping; to harden a change, run all the gates, produce an SBOM or attestation, or prove a build is clean.
---

Every code change passes this gate before it ships — application code, frontend, infrastructure, Terraform, Kubernetes manifests, Dockerfiles, CI config, all of it. A change is shippable only after every deterministic gate is green, and the run then records what "green" covered. This skill orchestrates the gates in a fixed order so each run is identical; the commands live in `skill-gate`, never in prose, and the per-gate rationale lives in [the pipeline reference](references/pipeline.md). Mechanical scanning is the floor — the attestation is the artifact that proves the floor was met. The pipeline subsumes the dependency supply-chain audit: the sca and secrets gates and the `syft` SBOM cover dependency vulnerabilities, pinning, and CVE triage, with the depth in [supply-chain risk](references/supply-chain.md).

## Steps

1. **Scope the gates.** Run `skill-gate --list` at the repo root to enumerate the gates the detected stacks activate. Confirm the printed list names a gate per supported category across the seven the stack covers (format, lint, types, sast, sca, secrets, test). The step is done when the scope is confirmed against [the pipeline reference](references/pipeline.md).

2. **Pass the quality gates.** Run `skill-gate --category format`, then `--category lint`, then `--category types`, in that order. A non-zero exit blocks the pipeline; fix the source, then rerun the failing category until its exit code is zero. The step is done when format, lint, and types each exit zero.

3. **Pass the security gates.** Run `skill-gate --category sast` (Semgrep), then `--category sca` (trivy or pip-audit), then `--category secrets` (gitleaks), in that order. The sca and secrets gates are the dependency supply-chain audit: sca scans the locked tree for known-vulnerable packages, secrets hunts leaked credentials, and both depend on a committed lockfile so the scanned tree is reproducible — the threat model, the pinning discipline, and the CVE triage method live in [supply-chain risk](references/supply-chain.md). Record each finding with its severity, rule id, and location; triage each dependency CVE for reachability and a fixed version, then assign one of the four responses (upgrade, pin, patch, accept) from the same reference. A critical or high finding blocks the merge until the finding is fixed or a waiver-log entry is recorded per [the pipeline reference](references/pipeline.md). The step is done when each security category exits zero or carries a recorded waiver-log entry that a reviewer has checked.

4. **Pass the test gate.** Run `skill-gate --category test`. A failing suite blocks the change; fix the source, then rerun until the suite exits zero. The step is done when the test category exits zero.

5. **Seal the merge gate.** Run `skill-gate --strict` for the final pass, where a missing tool counts as a failure rather than a silent skip. A red result stops the line (Jidoka); a green result means every category ran on a present tool. The step is done when `skill-gate --strict` exits zero.

6. **Produce the attestation.** Capture the machine-readable gate record with `skill-gate --strict --format json`, generate the SBOM with `syft` (`skill-gate` has no SBOM capability; the format choice lives in [supply-chain risk](references/supply-chain.md)), and record any waiver-log entry beside them. The SBOM command reads the locked tree:

   ```sh
   syft . -o cyclonedx-json
   ```

   Confirm the record names a result per category from step 1. The step is done when the gate record and the SBOM file both exist for this change.

See also: [the determinism doctrine](../../meta/foundation/SKILL.md).

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md and task list current.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
