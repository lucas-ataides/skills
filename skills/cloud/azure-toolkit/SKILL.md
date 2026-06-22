---
name: azure-toolkit
description: Build and operate on Microsoft Azure the right way — IaC-first, secure, cost-aware, aligned to the Well-Architected Framework. Use when the user designs, reviews, or hardens Azure infrastructure; writes Bicep or Terraform for Azure; sets up Entra ID, RBAC, or managed identities; configures Key Vault, networking, NSGs, or private endpoints; applies Azure Policy, Defender, or Monitor; reviews Azure cost, tags, or budgets; or asks whether an Azure setup is secure or SOC2-ready.
---

Build and run workloads on Azure that hold up under the Well-Architected Framework: reliable, secure, cost-aware, operable, and fast enough for the intent. Default to advisory and Infrastructure-as-Code authoring — provisioning is an external mutation, so any `apply`, `deploy`, or portal change waits for a reviewed plan and explicit human approval. The leverage is rarely the resource itself; the leverage is the identity that reaches it, the network that exposes it, and the plan that changes it.

Treat the [Azure practices reference](references/azure-practices.md) as the depth bar across the seven steps below.

## Steps

1. **State the workload and its pillars.** Write what the workload must deliver, its environment (production carries a higher bar), and a one-line target per Well-Architected pillar: reliability, security, cost, operational excellence, performance. The step is done when each of the five pillars has a named target, not a blank.

2. **Map identity and secrets.** Name the Entra ID principals, the RBAC role assignments scoped least-privilege, and the managed identity each compute resource uses instead of a shared secret; route every credential through Key Vault. The step is done when no shared key or connection string sits in code or config and every role assignment names its scope.

3. **Map network and data protection.** Name the VNet, subnets, and NSG rules; mark every data resource as private-endpoint-only with public network access disabled; confirm encryption at rest and TLS in transit. The step is done when no storage account, database, or Key Vault is reachable from the public internet without a recorded exception.

4. **Author the IaC and read the plan.** Express the resources in Bicep or Terraform under version control, then produce a `what-if` or `terraform plan` and read it against the [infra-safety discipline](../../engineering/engineering/references/infra-safety.md). The step is done when the plan is captured and a human has named what it creates, changes, and destroys.

5. **Apply governance, cost, and monitoring controls.** Attach Azure Policy and Management Group guardrails, enable Defender for Cloud, route diagnostic logs to Log Analytics, and set a budget plus a cost-allocation tag on every resource group. The step is done when diagnostic settings exist on each resource and a budget with an alert threshold is defined.

6. **Run the failure-mode and SOC2 checklist.** Walk the workload against the red flags in the [Azure practices reference](references/azure-practices.md) — public storage, owner-everywhere RBAC, secrets in config, missing diagnostic logs, click-ops — and map the controls to the relevant SOC2 trust criteria. The step is done when each red flag is marked absent or recorded as an accepted risk with an owner.

7. **Report findings, or stop before any mutation.** For a review, rank findings blocker, major, or minor against the pillar each endangers; for a build, present the IaC and the reviewed plan and stop. The step is done when the review carries a verdict per pillar, or the change waits on explicit approval before `apply`.
