---
name: gcp-toolkit
description: Design and operate Google Cloud like a GCP architect — serverless-first, managed-first, least-privilege, judged against the Architecture Framework's five categories. Use when designing, provisioning, reviewing, or hardening GCP; picking compute (Cloud Run, GKE Autopilot, Functions, GCE) or data (Firestore, Spanner, Cloud SQL, BigQuery); writing Terraform; auditing IAM, projects, VPC, CMEK, or audit logs; setting SLOs; mapping to SOC2. IaC and advisory; a live-project provision is approval-gated.
---

Design and operate Google Cloud the way a GCP architect does. The default move is **serverless-first, then managed-first**: prefer the service that scales to zero and removes undifferentiated work, so owning a VM is the last resort, not the first reach. The hard part is rarely the resource — the hard part is choosing the most managed option that still meets the constraint, scoping the IAM binding, placing the project so the blast radius stays small, and proving the control before an auditor or an attacker finds it.

This skill is advisory and authors IaC by default. A provision against a live project is an external mutation that runs only behind a reviewed plan and explicit, recorded approval, never freehand from a step here.

Climb the determinism ladder: a `gcloud` command, an org policy constraint, or a policy-as-code rule beats prose; a lint or `terraform validate` gate beats a checklist; judgment is the last rung.

## Steps

1. **State the workload and its bar.** Write what the workload must do, its traffic and state shape, its data classification, the environment (production carries the higher bar), and the compliance regime in scope. The constraints recorded here are the bar that every later managed-service choice is measured against. This step is done once the workload, its data classification, and its environment are written down.

2. **Choose the most managed service that meets the constraint.** Walk the compute and data decisions through the [managed-first reference](references/managed-first.md): Cloud Run before GKE Autopilot before Compute Engine for compute, Cloud Functions for event glue; Firestore or Cloud SQL before Spanner, BigQuery for analytics. Descend to a self-run VM only against a recorded constraint from step 1. This step is done once each compute and data component names its chosen service, and each self-managed choice names the constraint that forced it.

3. **Apply the five Architecture Framework categories.** Take a named stance on operational excellence, security and privacy and compliance, reliability, cost optimization, and performance optimization, per the [Architecture Framework reference](references/architecture-framework.md). A category with no stance is a gap, not a default. This step is done once each of the five categories carries a written stance for this workload.

4. **Place the project and lay the identity and security baseline.** Site the workload in its own project under the right folder, grant access through service accounts bound to predefined or custom roles via Workload Identity, encrypt at rest with CMEK and in transit with TLS, close the VPC, and enable Cloud Audit Logs, per the [IAM and SRE reference](references/iam-and-sre.md). This step is done once no binding grants Owner or Editor, no JSON service-account key is introduced where Workload Identity reaches, every data store names its CMEK key, and Data Access logs are on for the project.

5. **Set the SLO and error budget.** Define a service-level objective for the workload's critical journey, derive the error budget from it, and wire the alerting that fires before the budget is spent, per the [SRE section](references/iam-and-sre.md#sre-slos-and-error-budgets). An unreliable target nobody measures is a reliability gap, not a default. This step is done once the SLO, its error budget, and a burn-rate alert are written down.

6. **Author as IaC and attach cost controls.** Express every resource in Terraform (or Config Connector) with pinned providers and remote, locked state — no console click-ops, since click-ops leaves no diff and no review. Set a billing budget with an alert, apply the mandatory label set, and pull the cost levers (committed-use discounts on steady load, the Recommender's right-sizing, autoscaling to zero) named in the [cost section](references/architecture-framework.md#4-cost-optimization). This step is done once `terraform validate` and `terraform fmt -check` both pass, the budget alert exists, and every billable resource carries the required labels.

7. **Review against the five categories and the red flags, then gate the mutation on a reviewed plan.** Check the design against each category's failure modes and the security red flags: a public bucket, a primitive role, a downloaded service-account key, absent audit logs, a VM where Cloud Run fits, click-ops. Then produce `terraform plan` and route any create, change, or destroy on a stateful resource through the human-approval gate in the [infra-safety discipline](../../engineering/engineering/references/infra-safety.md), where a plan showing replace or destroy on stateful data stops the line until the data path is confirmed. The apply against a live project is the approval-gated external mutation, outside this skill's default authority. This step is done once each red flag is marked absent or recorded as an accepted risk with a named owner, a written plan exists with a recorded approval, and the change is halted absent that approval.

Infrastructure is code — pass the [appsec](../../engineering/appsec/SKILL.md) gate before any apply.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
