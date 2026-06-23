# Cloud controls

The judgment behind the cloud-best-practices steps. The gates (`skill-gate`, run through
[autoguardrails](../../../engineering/autoguardrails/SKILL.md)) scan infrastructure-as-code
and emit policy findings; this page is what the scanner cannot decide — which control a
criterion demands, how to build it across three clouds, and what artifact proves it ran. An
auditor never sees your cloud console. The auditor sees evidence. A control that produces no
evidence did not happen as far as the audit is concerned, so the deliverable is never the
cloud feature — it is the trail from a criterion to a control to a dated artifact a stranger
can open and check.

The principles below are cloud-agnostic on purpose. AWS, Azure, and GCP name the same
control three different ways; the control is the same, so the mapping is written against the
concept and the per-cloud service is named in parentheses.

## The Well-Architected themes — the shared vocabulary

All three clouds publish a "Well-Architected" framework (AWS Well-Architected, Azure
Well-Architected, Google Cloud Architecture Framework), and the five cross-cloud themes are
the same. Read a design against all five, because optimizing one alone bends the others:

- **Security.** Least-privilege identity, encryption everywhere, network segmentation, audit
  logging. This theme is the one the compliance regimes formalize, so the rest of this page
  expands it.
- **Reliability.** The system withstands and recovers from failure: multi-AZ or multi-region
  redundancy, health checks, automated failover, tested backups and disaster recovery. A
  design with a single point of failure fails this theme regardless of how secure it is.
- **Cost.** Spend tracks value: right-sized resources, autoscaling down as well as up,
  budgets and anomaly alerts, no orphaned volumes or idle instances. Cost is a theme, not an
  afterthought, because an unmonitored account bleeds money the same way it bleeds data.
- **Operational excellence.** The system is observable and changes are routine: IaC for every
  resource, telemetry on every service, runbooks for the known failures, blameless incident
  review. Operations is where security and reliability are either sustained or quietly eroded.
- **Performance efficiency.** Resources match the load: the right instance family, caching,
  managed services over hand-rolled ones, and a way to measure latency against a budget.

Security and reliability carry the audit weight; cost, operations, and performance keep the
workload alive long enough to stay compliant. A control that wins security and wrecks
reliability is not a win.

## The security baseline — non-negotiable across every cloud

These controls are the floor. A workload missing any of them is not a candidate for an audit,
it is a finding waiting to be written.

- **Least-privilege IAM.** Every identity (user, role, service account) holds exactly the
  permissions its job needs and no more. The default is deny; access is granted by explicit
  policy, scoped to specific resources, and reviewed on a schedule. Wildcard grants
  (`Action: "*"` on `Resource: "*"`) are the single most common cloud misconfiguration and
  the widest blast radius. (AWS IAM, Azure RBAC, GCP IAM.)
- **MFA on every human identity.** Multi-factor authentication is enforced on the root or
  global-admin account first, then every console user. A password alone is a phished password.
- **No long-lived static keys.** Workloads authenticate with short-lived, automatically
  rotated credentials from the platform's identity service, never a static access key checked
  into config. A long-lived key is a credential that leaks once and works forever. (AWS IAM
  roles / STS, Azure managed identities, GCP workload identity.)
- **Encryption at rest.** Every data store — object storage, block volumes, databases,
  backups, snapshots — is encrypted with keys managed by the platform's key service, with
  customer-managed keys where the regime demands key control. (AWS KMS, Azure Key Vault, GCP
  Cloud KMS.)
- **Encryption in transit.** TLS on every network path, internal and external; plaintext
  HTTP and unencrypted database connections are disabled, not merely unused.
- **Network segmentation.** Resources sit in private subnets by default, reachable only
  through controlled ingress; security groups and network ACLs default-deny and open only the
  ports a service needs. A database on a public IP is a finding. (AWS VPC / security groups,
  Azure VNet / NSGs, GCP VPC / firewall rules.)
- **Secrets management.** Database passwords, API tokens, and certificates live in a secret
  manager and are injected at runtime, never baked into an image layer, an environment file in
  the repo, or a Terraform variable in plaintext state. (AWS Secrets Manager, Azure Key Vault,
  GCP Secret Manager.)
- **Centralized, immutable audit logging.** Every control-plane action is logged to a
  central, append-only, access-restricted store with a defined retention period. This log is
  the raw material of most evidence below, so it is the control that makes every other control
  provable. (AWS CloudTrail, Azure Monitor / Activity Log, GCP Cloud Audit Logs.)

## The shared-responsibility model — who owns which control

The cloud provider secures the cloud; the customer secures what they run in it. The line
moves with the service model, and mistaking which side owns a control is how a gap opens that
neither party watches:

- **Provider always owns** the physical data center, the host hypervisor, and the managed
  service's internals. The provider proves this half with its own SOC2 / ISO report — the
  customer inherits that evidence rather than reproducing it.
- **Customer always owns** identity and access configuration, data classification and
  encryption choices, network rules, and application code. No provider report covers an
  over-permissive IAM policy the customer wrote.
- **The line shifts by model.** On infrastructure-as-a-service the customer owns the guest OS
  and patching; on platform-as-a-service the provider takes the OS and the customer keeps the
  app and the data; on software-as-a-service the customer keeps little but access control and
  data. Name the model per workload, because the customer-owned controls are the only ones the
  workload's audit can claim.

The practical rule: map every in-scope criterion to an owner before writing a control. A
criterion the provider owns is satisfied by citing the provider's report; a criterion the
customer owns needs a control and evidence in the workload.

## SOC2 Trust Services Criteria — mapped to controls and evidence

SOC2 is structured around five Trust Services Criteria categories. Security (the Common
Criteria, "CC") is mandatory; the other four are included only if the engagement's scope
names them. Each criterion below maps to concrete cloud controls and, decisively, to the
**evidence** the control produces — because the audit tests evidence, not intentions.

### Security / Common Criteria (CC) — mandatory

The backbone category, covering access control, change management, and monitoring.

- **Access control (CC6).** Controls: least-privilege IAM, MFA enforcement, no long-lived
  keys, periodic access review, network segmentation.
  Evidence: IAM policy exports showing scoped permissions; an MFA-enabled report across all
  users; a quarterly access-review record with sign-off; security-group rules showing
  default-deny.
- **Change management (CC8).** Controls: every infrastructure change lands through reviewed,
  version-controlled IaC; a CI gate blocks an unreviewed or non-compliant change; production
  access to apply changes is restricted.
  Evidence: pull-request history with required reviewers; the CI pipeline's pass/fail log per
  change; the IaC commit trail tying a deployed resource to an approved diff.
- **Monitoring (CC7).** Controls: centralized audit logging with retention; alerting on
  anomalous activity (root login, policy change, failed-auth spikes); a defined incident
  response process.
  Evidence: the audit-log retention configuration; alert-rule definitions and a sample of
  fired alerts; incident tickets showing detection-to-resolution timelines.

### Availability — backups, DR, SLAs

Included when the engagement covers uptime commitments.

- Controls: automated backups with a tested restore; multi-AZ or multi-region redundancy;
  disaster-recovery runbooks with a defined RTO and RPO; SLA monitoring.
- Evidence: backup-job success logs; a dated restore-test record proving the backup is usable,
  not merely present; the DR runbook plus a record of a DR exercise; an uptime report against
  the SLA.

### Confidentiality — encryption, data classification

Included when the workload handles confidential business data.

- Controls: encryption at rest and in transit; a data-classification scheme that tags data by
  sensitivity; access restricted to classified data on a need-to-know basis.
- Evidence: encryption-configuration snapshots per data store; the data-classification policy
  and a sample of tagged resources; access-grant records scoped to the classification.

### Processing Integrity — complete, accurate, authorized processing

Included when the system's correctness is a contractual commitment.

- Controls: input validation at trust boundaries; reconciliation or checksum on data
  pipelines; monitoring that processing completed without silent drops; authorization on every
  state-changing action.
- Evidence: validation-rule definitions; reconciliation reports showing input-vs-output
  counts; pipeline-completion logs and alerting on failures.

### Privacy — personal data lifecycle

Included when the workload processes personal data (and the overlap with GDPR / CCPA is where
this criterion does the most work).

- Controls: a notice-and-consent record; data-subject-access and deletion mechanisms; data
  retention and disposal schedules; restriction of personal data to the purpose collected.
- Evidence: the privacy notice and consent log; a sample fulfilled access or deletion request
  with timestamps; the retention schedule and disposal-job records.

The pattern repeats: a criterion names a control, the control runs in the cloud, and the
control emits an artifact. The artifact is the audit's unit of truth.

## Compliance-as-code — the only way the controls stay true

A control configured once in the console decays the moment someone clicks a setting back.
Compliance-as-code makes the control a versioned, enforced, continuously checked artifact, so
the gap between "compliant on audit day" and "compliant every day" closes.

- **Policy-as-code.** Encode the organization's rules as machine-checked policy (Open Policy
  Agent / Rego, AWS Service Control Policies, Azure Policy, GCP Organization Policy) so a
  forbidden configuration — a public storage bucket, an unencrypted volume, a wildcard IAM
  grant — is rejected rather than reviewed. The policy is the control written as code that the
  cloud or the pipeline enforces.
- **IaC scanning.** Scan the infrastructure-as-code before it applies (`checkov`, `tfsec`,
  `terrascan`, `trivy config`) so a misconfiguration fails the build instead of reaching the
  account. This scan is a `skill-gate` category, run through
  [autoguardrails](../../../engineering/autoguardrails/SKILL.md) and ordered with the other
  gates by [appsec](../../../engineering/appsec/SKILL.md). The scan output is itself
  change-management evidence.
- **Drift detection.** Compare the live account against the IaC state on a schedule
  (`terraform plan` in check mode, AWS Config rules, Azure Policy compliance state) so a
  manual change made outside the pipeline raises an alert. Drift is the proof that someone
  bypassed change management, which is exactly the event the audit cares about.

Run the controls through the same `skill-gate` discipline as every other gate: a non-zero
exit blocks the change (Jidoka — stop the line on a defect), and the gate record is the
evidence that the control ran on this change. The destructive-operation guard (SK040) keeps a
`terraform destroy` or a `kubectl delete` out of any inlined skill step — those belong behind
a guarded, approved path per [infra-safety](../../../engineering/engineering/references/infra-safety.md),
never freehand.

## Failure modes — how cloud compliance turns into theater

Each of these passes a superficial look and fails an audit, or worse, fails an attacker test:

- **Compliance theater.** Controls exist on paper or in a slide deck but are not enforced in
  the account. The policy says "all buckets are private"; three buckets are public. The
  defense is enforcement-as-code: a control the pipeline rejects cannot be quietly skipped.
- **Click-ops with no audit trail.** A change applied by hand in the console leaves no diff,
  no reviewer, and no record of who changed what or why. The next reader cannot reconstruct
  it, and the audit cannot prove it was authorized. The defense is IaC for every change and
  drift detection for everything else.
- **No evidence.** The control runs, but nothing captures that it ran, so on audit day the
  team scrambles to screenshot settings that prove nothing about the period under review. The
  defense is treating evidence as a deliverable of the control, captured continuously with a
  timestamp, not reconstructed at the end.
- **Secrets in code.** A credential committed to the repo, baked into an image, or sitting in
  plaintext Terraform state. The blast radius equals whatever the credential owns. The defense
  is a secret manager plus secret scanning (`gitleaks`) on every commit and on history.
- **Over-permissive IAM.** A role with `*:*`, a service account that is project owner, a
  policy granted "to make it work." This is the widest and most common cloud finding. The
  defense is least-privilege by default, policy-as-code that rejects wildcards, and access
  review.

## Red flags

- A storage bucket, database, or admin port reachable from the public internet.
- An IAM policy granting `Action: "*"` on `Resource: "*"`, or a service account with
  owner / global-admin role.
- A long-lived static access key in config, an environment file, or Terraform state.
- The root or global-admin account without MFA, or used for daily operations.
- An audit log that is disabled, short-retention, or writable by the accounts it audits.
- A backup that has never been restore-tested, or a DR plan that has never been exercised.
- A control claimed in the audit with no artifact that proves it ran during the period.
- Infrastructure changed in the console with no corresponding IaC diff (drift).

## A worked example — three SOC2 controls, end to end

A SaaS workload on AWS is preparing for a SOC2 Type II audit covering Security and
Availability. Walk three criteria from scope to evidence:

1. **Access control (CC6) — least-privilege IAM.**
   - *Map:* the criterion demands that access is granted by explicit, scoped policy with MFA on
     human identities.
   - *Implement:* Terraform defines each role with a resource-scoped policy; a Service Control
     Policy denies any policy containing `"*"` in both action and resource; `checkov` in CI
     fails a plan that introduces a wildcard grant; an account-wide rule requires MFA.
   - *Evidence:* the IAM policy export showing scoped permissions; the SCP denying wildcards;
     the `checkov` pass record on each change; the MFA-enabled report across all users. An
     auditor sampling any change in the period sees a reviewed diff and a green gate.

2. **Change management (CC8) — IaC and a CI gate.**
   - *Map:* the criterion demands every infrastructure change is reviewed, version-controlled,
     and authorized.
   - *Implement:* all infrastructure lives in Terraform in a repo with required reviewers on
     every pull request; the pipeline runs IaC scanning and policy checks and blocks on a
     non-zero exit; AWS Config detects any resource changed outside the pipeline and raises a
     drift alert.
   - *Evidence:* the pull-request history with reviewer sign-off; the CI pass/fail log tying
     each deployed resource to an approved diff; the AWS Config drift report showing zero
     unexplained out-of-band changes. The drift report is the proof that change management was
     not bypassed.

3. **Availability — backups with a tested restore.**
   - *Map:* the criterion demands data is recoverable within the committed RTO and RPO.
   - *Implement:* automated daily snapshots of the database and volumes via IaC-defined backup
     policy; a scheduled job restores the latest snapshot into an isolated environment and
     verifies integrity; the restore result is logged.
   - *Evidence:* the backup-job success logs; the dated restore-test record proving the backup
     is usable, not merely present; the RTO/RPO measured during the restore against the SLA. A
     backup nobody has restored is not availability evidence — it is an assumption.

The deliverable in every case is the same shape: a criterion, the control that satisfies it,
and a dated artifact a reviewer can open. The cloud services were the easy half. The mapping
and the captured evidence are the audit.

## Going deeper

- [the determinism doctrine](../../../meta/foundation/SKILL.md) — predictability over cleverness.
- [infra-safety](../../../engineering/engineering/references/infra-safety.md) — blast radius
  and rollback for the IaC changes that implement these controls.
- [appsec](../../../engineering/appsec/SKILL.md) — the gate order the compliance
  scans join.
- [supply-chain](../../../engineering/appsec/references/supply-chain.md) — the
  same evidence-and-triage discipline applied to the dependency tree.
