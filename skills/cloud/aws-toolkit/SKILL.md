---
name: aws-toolkit
description: Design and operate AWS the way a Solutions Architect does — managed-first to remove undifferentiated heavy lifting, least-privilege, encrypted, cost-aware, judged against the Well-Architected pillars. Use when designing, provisioning, reviewing, or hardening AWS; picks compute (Lambda, Fargate, EC2) or data (DynamoDB, Aurora, RDS); writes Terraform or CDK; audits IAM, S3, VPC, KMS, or CloudTrail; sizes for cost; or maps a control to SOC2. Advisory and IaC by default; an apply is approval-gated.
---

Design and operate AWS the way a Solutions Architect does. The default move is **managed-first**: prefer the service that removes undifferentiated heavy lifting, so owning a server is the last resort, not the first reach. The hard part is rarely the resource — it is choosing the most managed option that still meets the constraint, scoping the IAM policy, containing the blast radius, and proving the control before an auditor or an attacker finds it.

This skill is advisory and authors IaC by default. A provision or apply is an external mutation that runs only behind a reviewed plan and explicit, recorded approval, never freehand from a step here.

Climb the determinism ladder: an AWS CLI command, a Config rule, or a Service Control Policy beats prose; a lint or policy-as-code gate beats a checklist; judgment is the last rung.

## Steps

1. **State the workload and its bar.** Write what the workload must do, its traffic and state shape, its data classification, the environment (production carries the higher bar), and the compliance regime in scope. The constraints recorded here are what every later managed-service choice is measured against. This step is done when the workload, its data classification, and its environment are written down.

2. **Choose the most managed service that meets the constraint.** Walk the compute and data decisions through the [managed-first reference](references/managed-first.md): Lambda before Fargate before EC2 for compute; DynamoDB or Aurora Serverless before RDS before a self-managed database; S3, SQS, SNS, EventBridge, Cognito, and Step Functions for the glue. Reach for a server only where a recorded constraint from step 1 rules the managed option out. This step is done when each compute and data component names its chosen service, and each self-managed choice names the constraint that forced it.

3. **Apply the six Well-Architected pillars.** Take a named stance on operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability, per the [Well-Architected reference](references/well-architected.md). A pillar with no stance is a gap, not a default. This step is done when each of the six pillars carries a written stance for this workload.

4. **Lay the security baseline.** Grant access through IAM roles, not long-lived keys; scope every policy to explicit actions and resource ARNs; encrypt at rest with KMS and in transit with TLS; close the network; turn on CloudTrail, Config, and GuardDuty, per the [security-baseline reference](references/security-baseline.md). This step is done when no policy carries `*` in `Action` or `Resource`, every data store declares a KMS key, and CloudTrail is on for the account.

5. **Author as IaC and attach cost controls.** Express every resource in Terraform or CDK with pinned versions and remote, locked state — no console click-ops, since click-ops leaves no diff and no review. Set an AWS Budget with an alert, apply the mandatory tag set, and pull the cost levers (right-size, Graviton, Savings Plans or Spot, S3 lifecycle) named in the [Well-Architected cost section](references/well-architected.md#5-cost-optimization). This step is done when `terraform validate` (or `cdk synth`) passes clean, the budget alert exists, and every resource carries the required tags.

6. **Review against Well-Architected and the red flags.** Check the design against each pillar's failure modes and the security red flags: public S3, wildcard IAM, hardcoded keys, no CloudTrail, a server where a managed service fits, click-ops. This step is done when each listed red flag is marked absent or recorded as an accepted risk with a named owner.

7. **Gate the mutation on a reviewed plan.** Produce the plan (`terraform plan` or `cdk diff`) and have a human name what it creates, changes, and destroys, per the [infra-safety discipline](../../engineering/engineering/references/infra-safety.md): a plan showing replace or destroy on a stateful resource stops the line until the data path is confirmed. The apply itself is the approval-gated external mutation, outside this skill's default authority. This step is done once a written plan exists with a recorded approval, and the change is halted absent that approval.

Infrastructure is code — pass the [appsec](../../engineering/appsec/SKILL.md) gate before any apply.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
