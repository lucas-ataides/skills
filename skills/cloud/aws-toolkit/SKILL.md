---
name: aws-toolkit
description: Build and operate on AWS the right way — IaC-first, least-privilege, encrypted, cost-aware, Well-Architected. Use when the user designs, provisions, reviews, or hardens AWS infrastructure; writes Terraform or CDK for AWS; audits IAM, S3, VPC, KMS, or CloudTrail; sizes or tags resources for cost; or maps AWS services to a SOC2 control. Advisory and IaC authoring by default — a provision or apply is an external mutation needing a reviewed plan and explicit approval.
---

Design and operate AWS the way a cloud platform lead does: infrastructure as code first, least-privilege by default, encrypted end to end, and judged against the Well-Architected pillars before anything is provisioned. The hard part is rarely the resource — it is scoping the IAM policy, containing the blast radius, and proving the control before an auditor or an attacker finds it.

This skill is advisory and authors IaC by default. Any provision or apply is an external mutation that runs only behind a reviewed plan and explicit approval, never freehand from a step here.

## Steps

1. **State the workload and its bar.** Write what the workload must do, its data classification, the environment (production carries the higher bar), and the compliance regime in scope. Work the design against the [AWS practices reference](references/aws-practices.md) Well-Architected section. This step is done when the six pillars each have a named stance for this workload.

2. **Author the resource as IaC.** Express every resource in Terraform or CDK — no console click-ops, since click-ops leaves no diff and no review. Pin provider and module versions. This step is done when the resource exists only in version-controlled IaC and `terraform validate` (or `cdk synth`) passes clean.

3. **Scope identity and encryption.** Grant access through IAM roles, not long-lived keys; write policies to the exact actions and resource ARNs the workload needs, with no `*` in `Action` or `Resource`; encrypt at rest with KMS and in transit with TLS. This step is done when the policy names its actions explicitly and every data store declares a KMS key.

4. **Close the network and turn on the audit trail.** Place workloads in private subnets behind scoped security groups; reserve public exposure for a load balancer or gateway. Enable CloudTrail, AWS Config, and GuardDuty across accounts. This step is done when no security group allows `0.0.0.0/0` to a workload port and CloudTrail is on for the account.

5. **Attach cost and compliance controls.** Set an AWS Budget with an alert, apply the mandatory tag set, and right-size against the performance pillar. Map each control to its SOC2 family per the reference (audit logging, access control, encryption, change management). This step is done when the budget alert exists, every resource carries the required tags, and each in-scope control names its evidence.

6. **Plan, review, and gate the change.** Produce the plan (`terraform plan` or `cdk diff`) and have a human name what it creates, changes, and destroys. Reuse the [infra-safety discipline](../../engineering/engineering/references/infra-safety.md): a plan showing replace or destroy on a stateful resource stops the line until the data path is confirmed. This step is done when the reviewed plan is recorded and approved.

7. **Verify against the red flags.** Check the change against the reference's failure modes: public S3, wildcard IAM, hardcoded keys, no CloudTrail, click-ops. This step is done when none of the listed red flags is present and the worked example's controls are mirrored in the change.
