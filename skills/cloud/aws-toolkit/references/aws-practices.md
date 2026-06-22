# AWS practices

The judgment behind the aws-toolkit steps. Read the section for the decision in front of
you; each carries a checklist, the red flags that mark a bad change, and where it earns
it, a worked example. The deterministic gates own syntax and formatting — this page is the
architectural and security judgment they cannot encode.

One rule frames everything below: provisioning is an external mutation. A `terraform
apply`, a `cdk deploy`, or a console change alters real infrastructure and real billing,
so the apply runs only behind a reviewed plan with explicit, recorded approval. This skill
authors IaC and advises; the apply is a separate, guarded, approved act — the
[infra-safety discipline](../../../engineering/engineering/references/infra-safety.md) governs
it, and that discipline grounds out in the foundation doctrine's
[Genchi Genbutsu](../../../meta/foundation/SKILL.md): read the real plan, never assume it.

## The Well-Architected pillars

Six pillars frame every AWS design. Each workload takes a named stance on all six before a
resource is authored — a pillar with no stance is a gap, not a default.

- **Operational excellence**: run infrastructure as code, deploy through a pipeline with
  small reversible changes, define runbooks, and emit metrics and alarms a responder can
  act on. Practice: CloudWatch dashboards and alarms wired before launch, not after the
  first incident.
- **Security**: least privilege through IAM roles, encryption at rest and in transit, a
  full audit trail, and a closed network. Detailed in the IAM, encryption, networking, and
  logging sections below — this is the pillar with the lowest tolerance for shortcuts.
- **Reliability**: design for failure — multi-AZ by default, health checks, automated
  recovery, and tested backups. Practice: a stateful tier spans at least two Availability
  Zones, and the restore path is rehearsed, not assumed.
- **Performance efficiency**: pick the resource type the workload needs, scale
  horizontally, and measure before tuning. Practice: an auto-scaling group sized to a
  measured load curve beats a hand-picked instance count.
- **Cost optimization**: pay for what the workload uses — right-size, adopt Savings Plans
  or Spot where the workload tolerates it, and shut down idle resources. Detailed in the
  cost-controls section.
- **Sustainability**: minimize provisioned-but-idle capacity, prefer managed and
  serverless services that pack utilization, and pick efficient regions. Practice:
  serverless or Graviton for spiky workloads rather than an always-on over-provisioned
  fleet.

Red flags: a design that names no pillar stance; security treated as a later hardening
pass; reliability assumed from a single AZ; cost considered only after the first bill.

## IAM — least privilege

Identity is the control plane of AWS. A wildcard policy is the single most common path
from one compromised component to a whole-account breach.

Checklist:

- **Roles over keys**: workloads assume IAM roles (instance profiles, IRSA, task roles);
  long-lived access keys are avoided, and any that exist are rotated and inventoried.
- **No root for daily work**: the root user has MFA, no access keys, and is used only for
  the few account-level tasks that require it.
- **Scoped policies**: every statement names explicit actions and explicit resource ARNs.
- **No wildcards**: `Action: "*"` and `Resource: "*"` are rejected outside narrow,
  reviewed exceptions; prefer the managed job-function policies or a tightly scoped custom
  policy.
- **Conditions and boundaries**: permission boundaries cap delegated roles; conditions
  (source VPC, MFA present, tag match) narrow a grant further.
- **Federation**: human access comes through IAM Identity Center or an external IdP, not
  per-person IAM users with passwords.

Red flags: an inline policy with `"Action": "*"`; access keys committed or passed as
environment variables; the root account used in a pipeline; a role anyone can assume with
no condition; `AdministratorAccess` attached to a service role.

## Encryption — at rest and in transit

Checklist:

- **At rest**: every data store (S3, EBS, RDS, DynamoDB, EFS) declares encryption with a
  KMS key — a customer-managed key (CMK) where key policy and rotation must be controlled.
- **In transit**: TLS on every endpoint; HTTP redirects to HTTPS; internal service calls
  use TLS, not plaintext inside the VPC.
- **Key management**: KMS key policies follow least privilege, automatic key rotation is
  on, and key administrators are separated from key users.
- **Secrets**: credentials live in Secrets Manager or SSM Parameter Store (SecureString),
  injected at runtime — never in code, an AMI, a container layer, or a plan output.

Red flags: an unencrypted EBS volume or RDS instance; an S3 bucket with no default
encryption; a load balancer terminating only on port 80; a database password in a
Terraform variable file committed to git.

## Networking — VPC, subnets, security groups

Checklist:

- **VPC layout**: workloads run in a VPC with public subnets for ingress only (load
  balancers, NAT) and private subnets for compute and data.
- **Private by default**: instances, containers, and databases sit in private subnets with
  no public IP; outbound goes through a NAT gateway or VPC endpoint.
- **Security groups**: scoped to the exact port and source; reference other security groups
  rather than CIDR ranges where possible; no `0.0.0.0/0` to a workload or admin port.
- **Endpoints**: VPC endpoints (Gateway for S3 and DynamoDB, Interface for other services)
  keep traffic off the public internet.
- **Segmentation**: separate accounts or VPCs per environment; production is isolated from
  development at the network and account boundary.

Red flags: a database with a public IP; a security group opening port 22 or 3389 to
`0.0.0.0/0`; a single flat subnet for everything; cross-environment traffic on a shared
security group.

## Logging and audit

Checklist:

- **CloudTrail**: a multi-region, organization-wide trail captures management and (where
  needed) data events to a dedicated, locked-down S3 bucket; log-file validation is on.
- **AWS Config**: records resource configuration and evaluates conformance rules
  (encryption present, public access blocked, required tags) continuously.
- **GuardDuty**: threat detection enabled across all accounts and regions, with findings
  routed to a responder or SIEM.
- **CloudWatch**: application and platform logs centralized, with metric filters and alarms
  on the signals that matter.

Red flags: CloudTrail off or single-region; the trail bucket writable by the workload
accounts it audits; GuardDuty findings with no destination; logs with no retention policy.

## Core services map

Pick the managed service that fits the shape of the workload before reaching for a
self-managed equivalent. The grain of AWS runs toward managed and serverless.

- **Compute**: EC2 (full control), ECS or EKS (containers), Lambda (event-driven,
  serverless), Fargate (containers without nodes to manage).
- **Storage**: S3 (object), EBS (block, attached to EC2), EFS (shared file).
- **Database**: RDS and Aurora (relational), DynamoDB (key-value, serverless), ElastiCache
  (in-memory cache).
- **Queue and event**: SQS (queue), SNS (pub/sub), EventBridge (event bus), Kinesis
  (streaming).
- **Serverless glue**: Lambda plus API Gateway, Step Functions for orchestration, and
  EventBridge for routing — the default for spiky or event-driven work.

Red flags: a hand-managed database on EC2 where RDS fits; a polling loop where SQS or
EventBridge belongs; an always-on fleet for a once-a-day batch job.

## Infrastructure as code — Terraform and CDK

Checklist:

- **Everything in code**: no resource is created by hand in the console; the console is for
  reading state, not changing it.
- **Pinned versions**: provider and module versions are pinned; the state backend is
  remote (S3 plus DynamoDB lock, or Terraform Cloud), versioned, and locked.
- **Plan before apply**: `terraform plan` or `cdk diff` is produced and read by a human who
  names what it creates, changes, and destroys, per the
  [infra-safety discipline](../../../engineering/engineering/references/infra-safety.md).
- **Modules**: reusable, parameterized modules carry the secure defaults so a new resource
  inherits encryption, tags, and private networking rather than re-deriving them.
- **Guarded teardown**: a destroy runs only against a named, non-production target with
  recorded approval and a verified state backup. A teardown command is never inlined in a
  step — describe the approval path; the destructive command stays behind the guarded,
  approved step.

Red flags: a resource that exists in the console but not in code; an unpinned provider; a
local or unlocked state file; an apply with no plan anyone read; auto-apply on a production
workspace.

## Cost controls

Checklist:

- **Budgets**: an AWS Budget per account or workload with an alert threshold routed to an
  owner; anomaly detection on for unexpected spend.
- **Tagging**: a mandatory tag set (owner, environment, cost-center, application) enforced
  by a Config rule or a tag policy, so spend is attributable.
- **Right-sizing**: instance and storage classes matched to measured use; Compute Optimizer
  and Cost Explorer recommendations reviewed on a cadence.
- **Commitment and lifecycle**: Savings Plans or Reserved capacity for steady workloads,
  Spot for fault-tolerant ones, S3 lifecycle rules to tier cold data, and idle resources
  scheduled off.

Red flags: an account with no budget; untagged resources with no cost attribution; an
oversized instance picked by guess; a dev environment running 24x7.

## SOC2-relevant controls

AWS controls map cleanly to the SOC2 Trust Services Criteria. Each in-scope control names
the AWS service that implements it and the evidence an auditor reads.

- **Audit logging**: CloudTrail plus Config plus CloudWatch — evidence: an immutable,
  retained trail of who changed what, when.
- **Access control**: IAM least privilege, Identity Center, and MFA — evidence: scoped
  policies, no shared accounts, a reviewed access list.
- **Encryption**: KMS at rest and TLS in transit — evidence: a Config rule showing every
  store encrypted, no plaintext endpoints.
- **Change management**: IaC in version control plus a reviewed plan plus a pipeline —
  evidence: every infrastructure change traceable to a commit, a review, and an approval.
- **Availability and monitoring**: multi-AZ, backups, and alarms — evidence: tested
  restores and an alerting path with an owner.

Red flags: a control claimed with no service behind it; change management asserted while
console edits bypass the pipeline; an access list nobody has reviewed.

## Failure modes

The recurring ways an AWS estate goes wrong. Each is a blocker until resolved.

- **Public S3**: a bucket with public access enabled or an over-broad bucket policy leaks
  data — the canonical AWS breach. Block public access at the account level.
- **Wildcard IAM**: `Action: "*"` or `Resource: "*"` turns one compromised credential into
  whole-account access.
- **Hardcoded keys**: access keys in code, an AMI, a container image, or a commit — they
  leak and are scraped within minutes.
- **No CloudTrail**: without a trail there is no forensic record, no SOC2 audit evidence,
  and no way to answer "who did this".
- **Click-ops**: a resource created by hand in the console has no diff, no review, no
  reproducibility, and drifts from code until the next apply silently reverts or clobbers
  it.

## Red flags

A fast scan over a change — any one of these stops the line:

- An S3 bucket without `block_public_access` and default encryption.
- An IAM statement containing `"*"` in `Action` or `Resource`.
- A credential or key literal in code, a variable file, or an image.
- CloudTrail disabled, single-region, or writing to an unprotected bucket.
- A security group opening an admin port to `0.0.0.0/0`.
- A resource in the console that does not exist in the IaC.
- An apply or deploy proposed with no reviewed plan.

## Worked example — a private, encrypted, logged S3 bucket

A bucket that holds data correctly closes four controls at once: public access blocked,
encryption at rest with a KMS key, access logging to a separate log bucket, and versioning
for recovery. Authoring this in IaC and reading the plan before any apply is the whole
discipline in one resource.

```hcl
# A customer-managed KMS key for the bucket's encryption.
resource "aws_kms_key" "data" {
  description             = "Encryption key for the app data bucket"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

# A separate bucket to receive access logs (logs never live in the bucket they audit).
resource "aws_s3_bucket" "logs" {
  bucket = "example-app-data-logs"
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# The data bucket itself.
resource "aws_s3_bucket" "data" {
  bucket = "example-app-data"
}

# Block all public access at the bucket level (account-level block belongs on top of this).
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Default encryption with the customer-managed KMS key.
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.data.arn
    }
    bucket_key_enabled = true
  }
}

# Versioning, so an overwrite or delete is recoverable.
resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Access logging into the dedicated log bucket.
resource "aws_s3_bucket_logging" "data" {
  bucket        = aws_s3_bucket.data.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access/"
}
```

The CDK equivalent collapses the same controls into a single construct, which carries the
secure defaults so a new bucket inherits them:

```typescript
import { Bucket, BlockPublicAccess, BucketEncryption } from "aws-cdk-lib/aws-s3";
import { Key } from "aws-cdk-lib/aws-kms";

const key = new Key(this, "DataKey", { enableKeyRotation: true });

const logs = new Bucket(this, "LogBucket", {
  blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
  enforceSSL: true,
});

new Bucket(this, "DataBucket", {
  blockPublicAccess: BlockPublicAccess.BLOCK_ALL, // no public exposure
  encryption: BucketEncryption.KMS,               // at-rest encryption
  encryptionKey: key,                             // customer-managed key
  enforceSSL: true,                               // in-transit: deny non-TLS
  versioned: true,                                // recoverable overwrites
  serverAccessLogsBucket: logs,                   // access audit trail
});
```

Before either is real, the plan (`terraform plan` or `cdk diff`) is produced, read, and
approved. A plan that shows a replace or destroy on the bucket stops the line until the
data path is confirmed — the apply itself is the guarded, approved external mutation, not a
step taken here.
