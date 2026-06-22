# Azure practices

The judgment behind the azure-toolkit steps. This reference inherits the [foundation](../../../meta/foundation/SKILL.md) doctrine — predictability over cleverness — the review depth bar from [code-review](../../../engineering/code-review/SKILL.md), and the change discipline from [infra-safety](../../../engineering/engineering/references/infra-safety.md). Provisioning is an external mutation; advisory and IaC authoring are the default, and any `apply` waits on a reviewed plan plus explicit approval.

The organizing frame is the Azure Well-Architected Framework. A workload earns its place by holding up under all five pillars at once, not by scoring well on one.

## The Well-Architected pillars

- **Reliability.** Design for the failure that will happen: availability zones for stateful tiers, geo-redundant storage for durability, health probes, retry with backoff, and a tested recovery objective (RTO/RPO). A single-region single-instance workload is a reliability finding, not a cost saving.
- **Security.** Assume breach. Least-privilege identity, private networking, encryption everywhere, and centralized detection. Security is the pillar that cannot be retrofitted cheaply, so it leads the design.
- **Cost optimization.** Pay for what the workload needs at the SKU it needs. Right-size, schedule non-production shutdown, buy reservations for steady baseline load, and tag every resource so spend is attributable.
- **Operational excellence.** Everything-as-code, deployed through a pipeline, observable in production. Click-ops is the anti-pattern: a change nobody can review, reproduce, or roll back.
- **Performance efficiency.** Match the service and SKU to the load curve; scale out before scaling up where the service allows; cache the hot path; measure against a budget the intent implies rather than a guess.

## Identity — Entra ID, RBAC, managed identities

Identity is the new perimeter. The control plane and most data planes authenticate through Microsoft Entra ID, so the identity model is the security model.

- **Managed identities over secrets.** A compute resource (VM, App Service, Function, Container App) authenticates to other Azure services through a system- or user-assigned managed identity. No connection string, no client secret, no key in app settings.
- **RBAC scoped least-privilege.** Grant the narrowest built-in role at the narrowest scope (resource, then resource group, then subscription) that the principal needs. `Owner` at subscription scope for a service principal is a blocker; prefer `Contributor` scoped to one resource group, or a purpose-built role.
- **No standing privilege where avoidable.** Human admin access goes through Privileged Identity Management with just-in-time elevation and approval, not a permanent `Owner` assignment.
- **Workload federation.** A pipeline authenticates with OIDC workload-identity federation, removing the long-lived service-principal secret from CI.

## Encryption — Key Vault, at-rest, in-transit

- **Key Vault as the secret boundary.** Keys, secrets, and certificates live in Azure Key Vault with RBAC authorization, soft-delete, and purge protection enabled. Applications read them at runtime through a managed identity; secrets never land in source, image layers, or logs.
- **At rest.** Platform encryption is on by default; for regulated data add customer-managed keys (CMK) backed by Key Vault, and enable infrastructure (double) encryption where the data class demands it.
- **In transit.** Enforce TLS 1.2 or higher, require HTTPS-only on storage and web tiers, and disable plaintext protocols.

## Networking — VNet, NSGs, private endpoints

- **Private by default.** PaaS data services (Storage, SQL, Cosmos DB, Key Vault) expose a private endpoint inside the VNet and disable public network access. A storage account reachable from the internet is the most common Azure breach vector.
- **Segmentation with NSGs.** Network Security Groups gate subnet traffic with explicit allow rules and a default deny; an NSG rule opening `0.0.0.0/0` to a management port (22, 3389) is a blocker.
- **Egress control.** Route outbound traffic through Azure Firewall or a NAT gateway, and front public web workloads with Application Gateway plus WAF or Front Door.
- **DNS.** Private DNS zones resolve private-endpoint records inside the VNet so clients reach the private IP rather than the public name.

## Governance — Policy, Management Groups, Defender, Monitor

- **Azure Policy.** Codify guardrails as policy assignments: deny public storage, require tags, allowed regions, enforce CMK. Policy is the structural control that makes the misconfiguration impossible rather than merely discouraged (poka-yoke).
- **Management Groups.** Organize subscriptions into a hierarchy and assign policy and RBAC at the group so a new subscription inherits the controls.
- **Defender for Cloud.** Enable Defender plans for the resource types in use; track the Secure Score and triage high-severity recommendations.
- **Monitor and Log Analytics.** Route diagnostic settings on every resource to a Log Analytics workspace, set activity-log alerts on privileged operations, and retain logs to the period the compliance regime requires.

## The core services map

| Need | Primary service | Notes |
|------|-----------------|-------|
| Compute (web/api) | App Service, Container Apps, AKS | Managed identity on; private inbound where possible |
| Compute (event) | Azure Functions | Consumption or Premium; identity-based bindings, no keys |
| Object storage | Storage account (Blob) | Private endpoint, public access disabled, CMK for regulated data |
| Relational | Azure SQL Database | Entra auth, private endpoint, TDE on, auditing to Log Analytics |
| NoSQL / global | Cosmos DB | RBAC data plane, private endpoint, multi-region for reliability |
| Messaging | Service Bus | Identity-based access, queues/topics for decoupling |
| Secrets | Key Vault | RBAC, soft-delete, purge protection |

## IaC — Bicep or Terraform, plan before apply

Infrastructure is expressed as code in version control, never assembled by hand in the portal. The change discipline is the [infra-safety](../../../engineering/engineering/references/infra-safety.md) one: blast radius first, plan read by a human, destruction guarded, rollback proven.

- **Plan is mandatory.** Bicep produces a `what-if`; Terraform produces a `plan`. A human names what the plan creates, changes, and destroys before a single mutation runs.
- **A replace or destroy on a stateful resource stops the line** until the data path is confirmed and state is backed up.
- **Remote, locked, versioned state.** Terraform state lives in a storage account backend with locking; nobody edits state by hand, and two applies never run against one state at once.
- **Modules and stacks.** Compose reusable modules per workload, parameterize per environment, and keep production and lower environments on the same code with different inputs.

## Cost controls

- **Budgets and alerts.** Define a budget per subscription or resource group with alert thresholds, so spend that drifts triggers a notification rather than a surprise invoice.
- **Tags.** A cost-allocation tag (owner, environment, cost-center) on each resource group makes spend attributable; enforce the tag through Azure Policy.
- **Reservations and savings plans.** Steady baseline compute moves to one- or three-year reservations; spiky load stays on-demand or spot.
- **Right-size and schedule.** Review Advisor right-sizing recommendations, deallocate idle resources, and schedule non-production environments to shut down outside working hours.

## SOC2-relevant controls

Azure-native controls map onto the SOC2 trust criteria:

- **Security / access (CC6).** Entra ID with MFA, RBAC least-privilege, PIM just-in-time elevation, Key Vault secret management, private networking.
- **Change management (CC8).** IaC in version control, pull-request review, plan-before-apply, pipeline-gated deploys — no click-ops.
- **Monitoring (CC7).** Defender for Cloud, Log Analytics, activity-log alerting, retained audit logs.
- **Availability (A1).** Zone-redundant deployment, geo-redundant backup, tested recovery objectives.

The auditor wants evidence: the policy assignment, the diagnostic setting, the access review, the plan in the pipeline log. A control with no evidence trail is a control with a gap.

## Failure modes

- **Public storage.** A storage account or blob container open to the internet — the canonical Azure data leak. Private endpoint plus disabled public access closes it.
- **Owner-everywhere RBAC.** Broad `Owner` or `Contributor` at subscription scope handed to humans and service principals alike. Scope down and move humans to PIM.
- **Secrets in config.** Connection strings and keys in app settings, source, or pipeline variables instead of Key Vault behind a managed identity.
- **No diagnostic logs.** Resources with diagnostic settings unset, so an incident has no audit trail and the SOC2 monitoring criterion fails.
- **Click-ops.** Resources created and edited in the portal, leaving no reviewable, reproducible, reversible record — the operational-excellence anti-pattern.

## Red flags

- An `Owner` role assignment at subscription or management-group scope on a non-human principal.
- A storage account, SQL server, Cosmos account, or Key Vault with public network access enabled.
- A client secret, connection string, or key checked into source or set in plain app settings.
- An NSG rule allowing `0.0.0.0/0` inbound to port 22 or 3389.
- A resource with no diagnostic settings and no Log Analytics destination.
- A plan that shows an unexplained `replace` on a database, disk, or volume.
- An `apply` or portal change proposed without a captured, human-read plan.
- A production workload in a single region with no zone redundancy and no recovery objective.

## Worked snippet — a secure storage account

A storage account hardened against the most common failure mode: public access disabled, TLS enforced, private-endpoint-only, with a diagnostic setting routing logs to Log Analytics.

Bicep:

```bicep
param location string = resourceGroup().location
param namePrefix string
param logAnalyticsWorkspaceId string
param subnetId string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: '${namePrefix}sa${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard_GRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    encryption: {
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: true
      services: {
        blob: { enabled: true }
      }
    }
  }
}

resource pe 'Microsoft.Network/privateEndpoints@2023-09-01' = {
  name: '${namePrefix}-sa-pe'
  location: location
  properties: {
    subnet: { id: subnetId }
    privateLinkServiceConnections: [
      {
        name: 'blob'
        properties: {
          privateLinkServiceId: storage.id
          groupIds: [ 'blob' ]
        }
      }
    ]
  }
}

resource diag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'to-log-analytics'
  scope: storage
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    metrics: [
      { category: 'Transaction', enabled: true }
    ]
  }
}
```

Terraform equivalent:

```hcl
resource "azurerm_storage_account" "secure" {
  name                            = "${var.name_prefix}sa"
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "GRS"
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  public_network_access_enabled   = false
  infrastructure_encryption_enabled = true

  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]
  }

  tags = {
    owner       = var.owner
    environment = var.environment
    cost-center = var.cost_center
  }
}

resource "azurerm_private_endpoint" "secure" {
  name                = "${var.name_prefix}-sa-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "blob"
    private_connection_resource_id = azurerm_storage_account.secure.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }
}

resource "azurerm_monitor_diagnostic_setting" "secure" {
  name                       = "to-log-analytics"
  target_resource_id         = azurerm_storage_account.secure.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_metric {
    category = "Transaction"
  }
}
```

Authoring stops at the plan. Run a `what-if` (Bicep) or `terraform plan`, hand the captured plan to a human reviewer, and apply only on explicit approval.
