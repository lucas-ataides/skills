---
name: cloud-best-practices
description: Map a cloud workload to a compliance baseline (SOC2 and friends), implement the controls as code across AWS/Azure/GCP, and produce audit evidence. Use when the user wants cloud best practices, a SOC2 (or ISO 27001 / HIPAA) control mapping, a security baseline review, compliance-as-code, policy-as-code or IaC scanning, evidence for an auditor, a Well-Architected review, or hardening a cloud account before an audit.
---

Make a cloud workload defensible and provable at once: pick the criteria in scope, map each to a concrete control, implement the control through infrastructure-as-code, and collect the evidence the control produces. A control with no evidence is compliance theater; a click-ops change with no audit trail cannot be proven later. The leverage is the trail from criterion to control to evidence, not the cloud features themselves.

The controls, the SOC2 Trust Services Criteria mapping, the evidence each control yields, the shared-responsibility split, and the failure modes live in [the cloud controls reference](references/cloud-controls.md).

## Steps

1. **Scope the criteria.** Name the compliance regime in scope (SOC2, ISO 27001, HIPAA) and the exact Trust Services Criteria categories it requires from [the cloud controls reference](references/cloud-controls.md): Security/Common Criteria always, plus the subset of Availability, Confidentiality, Processing Integrity, and Privacy the engagement names. The step is done when every in-scope criterion is listed and every out-of-scope criterion carries a recorded reason.

2. **Draw the responsibility line.** State, per criterion, which side of the shared-responsibility model owns the control, so the provider's SOC2 report covers the provider's half and the workload covers the rest. The step is done when each in-scope criterion names an owner: the cloud provider, the workload, or both.

3. **Map criteria to controls.** Translate each in-scope criterion into a concrete control from [the cloud controls reference](references/cloud-controls.md) — least-privilege IAM, encryption at-rest and in-transit, centralized audit logging, backups and DR, change management. The step is done when every workload-owned criterion maps to at least one named control and every control names the evidence it produces.

4. **Implement controls as code.** Express each control in infrastructure-as-code (Terraform, CloudFormation, Bicep) rather than the console, so the control is versioned, reviewed, and reproducible. Click-ops applied by hand leaves no diff and no trail. The step is done when each mapped control exists as committed IaC and the plan for a destructive or stateful change is read per [infra-safety](../../engineering/engineering/references/infra-safety.md).

5. **Gate the controls in CI.** Add policy-as-code and IaC scanning to the pipeline through [autoguardrails](../../engineering/autoguardrails/SKILL.md) and the gates in [appsec](../../engineering/appsec/SKILL.md), so a non-compliant change fails the build instead of reaching the account. Configure drift detection to flag any resource changed outside IaC. The step is done when a deliberately non-compliant fixture fails the gate and a drift event raises an alert.

6. **Collect the evidence.** Capture the artifact each control produces — IAM policy exports, encryption-config snapshots, audit-log retention settings, backup-restore test records, CI policy-scan results — and store each with a timestamp and the control it proves. The step is done when every in-scope criterion has a dated evidence artifact a reader can open.

7. **Review against the red flags.** Check the assembled mapping against the failure modes in [the cloud controls reference](references/cloud-controls.md): compliance theater, no audit trail, no evidence, secrets in code, over-permissive IAM. The step is done when each red flag is absent or carries a recorded, signed-off exception with a review date.

See also: [the determinism doctrine](../../meta/foundation/SKILL.md).

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
