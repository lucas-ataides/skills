---
name: azure-toolkit
description: Operate Azure the way a Cloud Architect does — PaaS-first, identity through Entra ID, least-privilege RBAC, private, cost-aware, against the Well-Architected pillars. Use when provisioning, reviewing, or hardening Azure; picking compute (App Service, Container Apps, Functions, AKS, VM) or data (Azure SQL, Cosmos DB); writing Bicep or Terraform; setting up Entra ID, managed identities, Key Vault, or landing zones; sizing for cost; or mapping to SOC2. IaC-first; a deploy is approval-gated.
---

Design and operate Azure the way a Cloud Architect does. The default move is **PaaS-first**: prefer the managed service that removes undifferentiated heavy lifting, so a virtual machine you patch is the last resort, not the first reach. The hard part is rarely the resource — it is choosing the most managed option that still meets the constraint, modeling identity through Microsoft Entra ID, scoping the RBAC assignment, containing the blast radius behind private networking, and proving the control before an auditor or an attacker finds it.

This skill is advisory and authors IaC by default. A provision, `apply`, `az deploy`, or portal change is an external mutation that runs only behind a reviewed plan and explicit, recorded approval, never freehand from a step here.

Climb the determinism ladder: an Azure CLI command, an Azure Policy assignment, or a deny rule in a landing zone beats prose; a lint or policy-as-code gate beats a checklist; judgment is the last rung.

## Steps

1. **State the workload and its bar.** Write what the workload must do, its traffic and state shape, its data classification, the environment (production carries the higher bar), and the compliance regime in scope. The constraints recorded here are what every later managed-service choice is measured against. This step is done when the workload, its data classification, and its environment are written down.

2. **Choose the most managed service that meets the constraint.** Walk the compute and data decisions through the [managed-first reference](references/managed-first.md): App Service or Container Apps or Functions before AKS before a VM for compute; Azure SQL Database or Cosmos DB before a self-managed engine for data; Service Bus, Storage, Event Grid, and Logic Apps for the glue. Reach for a VM or a self-managed engine only where a recorded constraint from step 1 rules the managed option out. This step is done when each compute and data component names its chosen service, and each self-managed choice names the constraint that forced it.

3. **Apply the five Well-Architected pillars.** Take a named stance on reliability, security, cost optimization, operational excellence, and performance efficiency, per the [Well-Architected reference](references/well-architected.md). A pillar with no stance is a gap, not a default. This step is done when each of the five pillars carries a written stance for this workload.

4. **Lay the identity and governance baseline.** Authenticate every compute resource through a managed identity, not a secret; scope each RBAC assignment to the narrowest built-in role at the narrowest scope; keep secrets in Key Vault; place the workload under its landing-zone management group with Azure Policy guardrails, per the [governance-and-identity reference](references/governance-and-identity.md). This step is done when no role assignment grants `Owner` at subscription scope to a non-human principal, no secret or connection string sits in code or config, and each data resource declares private-endpoint-only access.

5. **Author as IaC and attach cost controls.** Express every resource in Bicep or Terraform with pinned versions and remote, locked state — no portal click-ops, since click-ops leaves no diff and no review. Set an Azure budget with an alert, apply the mandatory tag set, and pull the cost levers (right-size, reservations or savings plans, deallocate idle, schedule non-production off) named in the [Well-Architected cost section](references/well-architected.md#3-cost-optimization). This step is done when `bicep build` or `terraform validate` passes clean, the budget alert exists, and every resource carries the required tags.

6. **Review against Well-Architected and the red flags.** Check the design against each pillar's failure modes and the governance red flags: public storage, `Owner`-everywhere RBAC, secrets in app settings, no diagnostic logs, a VM where a managed service fits, click-ops, per the [governance-and-identity reference](references/governance-and-identity.md#red-flags). This step is done when each listed red flag is marked absent or recorded as an accepted risk with a named owner.

7. **Gate the mutation on a reviewed plan.** Produce the plan (`az deployment ... what-if` for Bicep, or `terraform plan`) and have a human name what it creates, changes, and destroys, per the [infra-safety discipline](../../engineering/engineering/references/infra-safety.md): a plan showing replace or destroy on a stateful resource stops the line until the data path is confirmed. The deploy itself is the approval-gated external mutation, outside this skill's default authority. This step is done once a written plan exists with a recorded approval, and the change is halted absent that approval.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
