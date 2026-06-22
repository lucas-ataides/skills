# Google Cloud practices

The judgment behind the gcp-toolkit steps. Google Cloud hands you org-wide reach from a
single binding, so the discipline here is built on least-privilege, an auditable resource
hierarchy, and infrastructure expressed as code rather than clicked into a console. The
deterministic gates catch malformed config; this page catches the design that lints clean
and still leaks data, overspends, or fails an audit.

Provisioning is an external mutation. Authoring Terraform and advising are the default
mode of this skill; a live `apply`, a console edit, or any resource change runs only
behind the human-approval gate described in
[infra-safety](../../../engineering/engineering/references/infra-safety.md). Depth and severity
follow the bar in [the review lenses](../../../engineering/code-review/references/review-lenses.md),
and the determinism doctrine is set in [foundation](../../../meta/foundation/SKILL.md).

## The Architecture Framework pillars

Google's Architecture Framework names five pillars. A GCP design is judged against each,
not against correctness alone.

- **Operational excellence** — deploy through automation, observe through logs and metrics,
  rehearse incident response. Click-ops is the anti-pattern; repeatable IaC is the pillar.
- **Security, privacy, and compliance** — least-privilege IAM, encryption in transit and at
  rest, a defended network perimeter, audit trails. Covered in depth below.
- **Reliability** — design for the failure of a zone or a dependency; pick multi-zone or
  multi-region by the SLO, set health checks, define backup and restore with a tested
  recovery path.
- **Cost optimization** — match resources to load, label spend for attribution, commit to
  steady-state usage, and alert on budget breaches before the invoice lands.
- **Performance efficiency** — size and autoscale to the real workload, place data near
  compute, and measure against a stated latency or throughput budget.

Red flags: a design that optimizes one pillar (often cost or speed) while silently
sacrificing security or reliability; a pillar with no stated requirement.

## Resource hierarchy and org policy

GCP nests resources as **organization → folder → project → resource**. IAM policy and org
policy both inherit down this tree, so placement is a security decision.

- **Organization** — the root, tied to a Cloud Identity or Workspace domain. Org-level
  bindings reach everything beneath; reserve them for a small, audited break-glass group.
- **Folders** — group projects by team, environment, or trust boundary. Bind policy at the
  folder so a new project inherits the right guardrails.
- **Projects** — the unit of billing, quota, and isolation. One workload per project keeps
  blast radius small and cost attribution clean.
- **Org policies** — constraints that the hierarchy enforces regardless of IAM. High-value
  constraints: `storage.publicAccessPrevention`, `iam.disableServiceAccountKeyCreation`,
  `compute.requireOsLogin`, `sql.restrictPublicIp`, and domain-restricted sharing.

Org policy is a guardrail, not a suggestion: a constraint set at the folder blocks the
mistake even when a project owner tries to make it. That is poka-yoke applied to cloud
governance.

## IAM and least-privilege

IAM is the highest-leverage control surface on Google Cloud. The default posture is the
narrowest role that lets the principal do its job, and nothing wider.

- **Primitive roles are banned in practice.** `roles/owner`, `roles/editor`, and
  `roles/viewer` predate fine-grained IAM and grant sweeping access across a project.
  Editor alone can alter most resources. Replace primitive grants with predefined roles
  scoped to a service.
- **Predefined roles first, custom roles second.** Reach for a Google-maintained predefined
  role (for example `roles/storage.objectViewer`). When no predefined role fits the need,
  author a custom role listing only the permissions the task requires.
- **Service accounts are workload identities, not shared logins.** Give each workload its
  own service account with a dedicated role binding, so a compromise is contained and an
  audit log attributes the action.
- **Workload Identity over keys.** GKE Workload Identity and Workload Identity Federation
  let a workload (in-cluster or off-GCP, such as a CI runner or another cloud) impersonate
  a service account with short-lived credentials. Exported JSON service-account keys are
  long-lived secrets that leak and never expire on their own.
- **No JSON keys where avoidable.** Set the `iam.disableServiceAccountKeyCreation` org
  policy. Where a key is genuinely unavoidable, store it in Secret Manager, scope it
  tightly, and rotate it on a schedule.
- **No owner-everywhere.** An organization or folder `roles/owner` binding on a human or a
  service account is a standing breach of least-privilege. Restrict it to a monitored
  break-glass path with alerting on use.

Red flags: a service account reused across unrelated workloads; a JSON key checked into a
repo or baked into an image; `roles/editor` on an automation account; a human with
org-level Owner.

## Encryption (CMEK and KMS)

Google encrypts data at rest by default with Google-managed keys. Regulated or
high-sensitivity workloads upgrade to **customer-managed encryption keys (CMEK)** through
Cloud KMS, which puts key rotation, disabling, and destruction under your control.

- Create a KMS key ring and key per data domain, with automatic rotation set.
- Point CMEK-capable services (Cloud Storage, BigQuery, Cloud SQL, Compute disks, Pub/Sub)
  at the key through their `kms_key_name` setting.
- Grant the service's agent the `roles/cloudkms.cryptoKeyEncrypterDecrypter` role on that
  key, and nothing broader.
- Treat key destruction as the most destructive act available: a scheduled key destruction
  renders the ciphertext permanently unreadable, so route it through the approval gate.

Red flags: sensitive data on default encryption where a compliance regime requires CMEK; a
single key shared across every service; the KMS admin and key user roles held by the same
principal.

## Networking

The network is the perimeter. The default posture is private, with egress and ingress
opened deliberately.

- **VPC** — use custom-mode VPCs with explicitly defined subnets, not auto-mode. Reserve
  internal ranges and size subnets to the workload.
- **Firewall rules** — default-deny ingress, then allow the specific ports and source
  ranges a service needs. A `0.0.0.0/0` allow on SSH (22), RDP (3389), or a database port
  is a finding.
- **Private Google Access** — let resources without external IPs reach Google APIs over
  internal routes. Pair it with Private Service Connect or VPC Service Controls to keep API
  traffic off the public internet.
- **VPC Service Controls** — draw a service perimeter around sensitive APIs (Storage,
  BigQuery) so data cannot be exfiltrated to a project outside the perimeter even with valid
  credentials.
- **No public IPs by default** — Cloud SQL, GKE nodes, and VMs take private IPs unless a
  reviewed requirement justifies a public address behind a load balancer.

Red flags: an auto-mode VPC in production; a firewall rule opening a management port to the
internet; a database with a public IP; egress wide open from a sensitive subnet.

## Core services map

Reach for the managed service before the self-run one; the framework's operational-excellence
pillar favors offloading undifferentiated work to Google.

- **Compute** — Compute Engine for VMs and lift-and-shift; GKE for containers needing
  orchestration; Cloud Run for stateless containers that scale to zero.
- **Storage** — Cloud Storage for objects (set uniform bucket-level access and
  public-access prevention); Persistent Disk and Filestore for block and file.
- **Data** — BigQuery for analytics and the warehouse; Cloud SQL for managed
  Postgres/MySQL/SQL Server; Spanner for global relational scale; Firestore for documents.
- **Serverless compute** — Cloud Functions for event-driven glue; Cloud Run for HTTP
  services and jobs. Both bind to a dedicated service account and scale on demand.
- **Messaging** — Pub/Sub for asynchronous, decoupled, at-least-once delivery between
  services; prefer an event over a synchronous cross-service call.

## IaC with Terraform

Infrastructure on GCP is expressed as code, reviewed as code, and applied behind a plan.
The discipline is the one in
[infra-safety](../../../engineering/engineering/references/infra-safety.md), specialized to GCP.

- **Plan before apply.** Produce `terraform plan`, then have a human name what it creates,
  changes, and destroys. A plan showing a replace or destroy on a stateful resource (a
  Cloud SQL instance, a disk, a bucket with data) halts the line until the data path is
  confirmed.
- **Remote, locked, versioned state.** Keep Terraform state in a Cloud Storage backend with
  object versioning and state locking. Never hand-edit state; never run two applies against
  one state at once.
- **`apply` is gated.** A live `apply` mutates real infrastructure, so it runs only with
  explicit, recorded approval against a named target. A `terraform` teardown, a `gcloud`
  delete, or a KMS key destruction is guarded the same way and never run freehand.
- **Modules and least-privilege CI.** Factor reusable resources into modules. The pipeline's
  service account holds exactly the roles the change needs, granted through Workload
  Identity Federation rather than an exported key.
- **Labels on everything billable.** Every resource that incurs cost carries labels for
  team, environment, and service, so spend is attributable.

## Worked example: a secure storage bucket

A Cloud Storage bucket configured against the failure modes below — private, uniform
access, public-access prevention on, CMEK-encrypted, versioned, and labeled. Adjust the
project, key, and names to the target.

```hcl
resource "google_storage_bucket" "secure_data" {
  name     = "acme-prod-secure-data"
  project  = "acme-prod"
  location = "US"

  # Deny ACLs; IAM is the only access path.
  uniform_bucket_level_access = true

  # Block any policy that would expose the bucket publicly.
  public_access_prevention = "enforced"

  # Customer-managed encryption via Cloud KMS.
  encryption {
    default_kms_key_name = google_kms_crypto_key.bucket_key.id
  }

  # Recover from accidental overwrite or delete.
  versioning {
    enabled = true
  }

  # Expire noncurrent versions to bound storage cost.
  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }

  # Cost attribution and audit.
  labels = {
    team        = "data-platform"
    environment = "prod"
    service     = "ingest"
  }
}

# Grant only the storage service agent encrypt/decrypt on the key.
resource "google_kms_crypto_key_iam_member" "bucket_key_user" {
  crypto_key_id = google_kms_crypto_key.bucket_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_storage_project_service_account.gcs.email_address}"
}
```

The bucket grants access through IAM bindings on least-privilege roles (for example
`roles/storage.objectViewer` for readers), never through a public `allUsers` or
`allAuthenticatedUsers` member.

## Logging, audit, and detection

An action nobody can reconstruct is an action nobody can defend in an audit. Observability
and audit are configured up front, not after the incident.

- **Cloud Logging** — centralize logs and route them through log sinks to a retention
  bucket, BigQuery, or Pub/Sub. Set retention to the compliance window.
- **Cloud Audit Logs** — Admin Activity logs are on by default; explicitly enable Data
  Access logs on sensitive services, since those record reads of data. Audit logs answer
  who did what, where, and when.
- **Security Command Center** — the org-wide posture and threat surface. The premium tier
  surfaces misconfigurations (public buckets, open firewalls, over-privileged accounts) and
  active threats. Treat its findings as a work queue.
- **Log-based alerts** — alert on the high-signal events: a new Owner binding, a service
  account key creation, an org-policy change, a firewall opened to the internet.

Red flags: Data Access logs off on a project holding regulated data; logs with no retention
or no sink; Security Command Center findings left unread.

## Cost controls

Cost is a first-class pillar, not an afterthought. Controls are set so spend is bounded,
attributed, and committed where it is steady.

- **Budgets and alerts** — define a billing budget per project or billing account with
  alert thresholds (for example 50/90/100 percent) wired to email or Pub/Sub. The alert
  fires before the invoice surprises anyone.
- **Labels for attribution** — the labels applied in Terraform flow into billing export, so
  cost is sliced by team, environment, and service. Unlabeled spend is unaccountable spend.
- **Committed-use discounts** — for steady-state compute, a one- or three-year commitment
  cuts the rate substantially. Reserve it for the predictable baseline, not the spiky peak.
- **Right-sizing and autoscaling** — use recommender output to drop idle resources, scale
  Cloud Run and managed instance groups on demand, and lifecycle-tier cold storage.

Red flags: no budget on a production billing account; unlabeled resources; on-demand
pricing on a workload that has run flat for a year.

## SOC2-relevant controls

GCP supplies the technical substrate for the SOC2 Trust Services Criteria. The controls
above map onto the audit as follows.

- **Logical access (CC6)** — least-privilege IAM, no primitive roles, Workload Identity over
  keys, and the `iam.disableServiceAccountKeyCreation` org policy evidence access control.
- **Change management (CC8)** — Terraform in version control, peer-reviewed plans, and the
  apply-approval gate evidence that infrastructure change is controlled and reviewed.
- **System monitoring (CC7)** — Cloud Audit Logs, Security Command Center, and log-based
  alerts evidence detection of unauthorized or anomalous activity.
- **Confidentiality and encryption (CC6.7 / C-series)** — CMEK through Cloud KMS,
  encryption in transit, and VPC Service Controls evidence protection of data at rest and
  in motion.
- **Availability (A-series)** — multi-zone or multi-region design, tested backup and
  restore, and budgets evidence resilience and capacity management.

The evidence is the configuration itself: an auditor reads the Terraform, the org policies,
and the audit logs rather than a screenshot.

## Failure modes and red flags

The recurring ways a GCP estate goes wrong. The audit step checks the design against this
list.

- **Public buckets** — a bucket exposed to `allUsers` or `allAuthenticatedUsers`, or one
  without public-access prevention. The classic data-leak vector. Enforce uniform
  bucket-level access and the public-access-prevention org policy.
- **Primitive roles** — `roles/owner` or `roles/editor` granted to humans, automation, or
  service accounts. Over-broad, hard to audit, and the root of most privilege-escalation
  paths. Replace with predefined or custom roles.
- **Service-account key sprawl** — exported JSON keys scattered across repos, laptops, and
  images, never rotated. Each is a long-lived credential waiting to leak. Disable key
  creation by org policy and adopt Workload Identity.
- **No audit logs** — Data Access logs disabled, or logs with no retention. A breach becomes
  unreconstructable and the SOC2 monitoring criterion fails.
- **Click-ops** — infrastructure created and changed by hand in the console, undocumented
  and unrepeatable. Drift accumulates and no plan exists to review. Move the estate into
  Terraform.

Severity follows [the review lenses](../../../engineering/code-review/references/review-lenses.md):
a public bucket, a primitive role on automation, or a leaked key is a **blocker**; missing
Data Access logs or unmanaged click-ops drift is a **major**; an unlabeled non-production
resource is a **minor**. Tie each finding to the pillar it endangers.
