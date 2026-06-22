---
name: gcp-toolkit
description: Build and operate on Google Cloud the IaC-first, secure, cost-aware way, aligned to the Google Cloud Architecture Framework. Use when designing or reviewing GCP architecture, IAM, projects, VPC/networking, KMS/CMEK, or Terraform for GCP; when auditing a GCP project for least-privilege, public buckets, primitive roles, service-account keys, or missing audit logs; or when planning GCP cost controls or SOC2-relevant controls.
---

Treat Google Cloud as production infrastructure governed by the [Architecture Framework](references/gcp-practices.md): IaC-first, least-privilege, cost-aware. Author Terraform and advise by default; a live `apply`, console change, or any resource mutation is an external action gated on explicit human approval plus a reviewed plan.

Work down the determinism ladder: a `gcloud`/`terraform` command or org policy beats prose, a policy-as-code or lint gate beats a checklist, judgment is the last rung.

## Steps

1. **Frame intent against the five pillars.** State the workload and the target against operational excellence, security/privacy/compliance, reliability, cost, and performance, per [the framework pillars](references/gcp-practices.md#the-architecture-framework-pillars). Done when the named pillars each carry a stated requirement or an explicit non-goal.

2. **Map the hierarchy and the blast radius.** Name the org, folder, and project the change targets, the org policies in force, and what shared state the change touches, per [resource hierarchy](references/gcp-practices.md#resource-hierarchy-and-org-policy) and [infra-safety blast radius](../../engineering/engineering/references/infra-safety.md). Done when target project, environment, and blast radius are written down.

3. **Design identity and data protection.** Specify IAM as predefined or custom roles bound to service accounts with workload identity, encryption via CMEK/KMS, and the VPC, firewall rules, and Private Google Access posture, per [IAM least-privilege](references/gcp-practices.md#iam-and-least-privilege), [encryption](references/gcp-practices.md#encryption-cmek-and-kms), and [networking](references/gcp-practices.md#networking). Done when no binding grants Owner or Editor, no JSON service-account key is introduced where workload identity is available, and every data store names its encryption and network exposure.

4. **Author the Terraform.** Encode the resources as Terraform against the [IaC discipline](references/gcp-practices.md#iac-with-terraform) and the [worked secure-bucket snippet](references/gcp-practices.md#worked-example-a-secure-storage-bucket), with remote locked state and labels for cost allocation. Done when `terraform validate` and `terraform fmt -check` both pass and every resource carries a cost-allocation label.

5. **Wire observability, audit, and cost controls.** Enable Cloud Logging, Cloud Audit Logs (admin and data access), Security Command Center, plus budgets and committed-use where the spend justifies it, per [logging and audit](references/gcp-practices.md#logging-audit-and-detection) and [cost controls](references/gcp-practices.md#cost-controls). Done when audit logs are configured on the target project and a budget with an alert threshold is defined.

6. **Audit for the known failure modes.** Check the design against the [failure modes and red flags](references/gcp-practices.md#failure-modes-and-red-flags): public buckets, primitive roles, service-account key sprawl, absent audit logs, click-ops, plus the [SOC2-relevant controls](references/gcp-practices.md#soc2-relevant-controls). Done when each listed failure mode is marked absent or recorded as an accepted risk with an owner.

7. **Gate the mutation on a reviewed plan.** Produce `terraform plan`, then route any create, change, or destroy on a stateful resource through the human-approval gate in [infra-safety plan-before-apply](../../engineering/engineering/references/infra-safety.md); `apply` is an external mutation outside this skill's default authority. Done once a written plan exists and a recorded approval accompanies it, with the change halted absent that approval.
