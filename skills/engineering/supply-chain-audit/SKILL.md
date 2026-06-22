---
name: supply-chain-audit
description: Audit dependencies for known vulnerabilities, generate an SBOM, and assess supply-chain risk via the SCA and secrets gates. Use when the user wants to scan for CVEs, audit dependencies, check for vulnerable or malicious packages, produce or update an SBOM, review a lockfile, hunt leaked credentials, or judge supply-chain risk before a release or merge.
---

A modern build ships more code from its dependency tree than from its own repository, so the dependency tree is the attack surface. Treat every package as untrusted input that runs with your privileges until an audit clears it. The gates run the scanners; the leverage is in pinning the tree, triaging each finding for reachability, and recording a defensible decision — work no scanner can do for you.

The threat model, the pinning discipline, the SBOM formats, and a worked CVE triage live in [supply-chain risk](references/supply-chain.md).

## Steps

1. **Scope the audit.** Run `skill-gate --list` at the repo root to name the detected stacks. The dependency manifests and lockfiles for those stacks are the audit scope. The step is complete when the named scope matches the stacks the project actually ships.

2. **Confirm the tree is pinned.** A scan of a floating manifest describes a build no one can reproduce, so verify a committed lockfile (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`, or hashed `requirements.txt`) exists per detected stack. The step is complete when every stack in scope has a committed lockfile, or each unpinned stack is recorded as a finding against [the pinning discipline](references/supply-chain.md).

3. **Scan dependencies for vulnerabilities.** Run `skill-gate --category sca` to scan the locked tree against the vulnerability databases. Record each finding with its package, version, CVSS band, and whether the dependency is direct or transitive. The step is complete when every reported CVE has a recorded row.

4. **Scan for leaked credentials.** Run `skill-gate --category secrets` to scan the tree and history. A leaked credential is a blocker whose blast radius equals whatever the credential controls, so route the exposed secret to rotation before the audit proceeds. The step is complete when the secrets gate exits clean, or every detected secret is logged with rotation already requested.

5. **Triage each finding.** Walk every recorded CVE through [the triage method](references/supply-chain.md): trace the path from a root dependency to the vulnerable package, judge reachability against the band, and locate a fixed version. The step is complete when each finding carries a path, a reachability verdict, and a fix status.

6. **Decide and record a response per finding.** Assign one outcome to each triaged finding — upgrade, pin/override, patch, or accept-with-justification — following [the response options](references/supply-chain.md); a silent dismissal is itself the defect. The step is complete when every finding has exactly one recorded outcome and a stated reason.

7. **Attest the build.** Generate the SBOM through `skill-gate` (CycloneDX for the security pipeline, SPDX when a contract names it), built from the same locked tree the build ships. Write the report: the SBOM path, vulnerability counts by severity, the per-finding outcomes, and the secrets result. The audit is done when every stack in scope has a scan result and an attached SBOM.

See also: [supply-chain risk](references/supply-chain.md).
