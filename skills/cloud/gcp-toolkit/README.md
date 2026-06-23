# gcp-toolkit

> Design and operate Google Cloud like a GCP architect — serverless-first, managed-first, least-privilege, judged against the Architecture Framework's five categories. Use when designing, provisioning, reviewing, or hardening GCP; picking compute (Cloud Run, GKE Autopilot, Functions, GCE) or data (Firestore, Spanner, Cloud SQL, BigQuery); writing Terraform; auditing IAM, projects, VPC, CMEK, or audit logs; setting SLOs; mapping to SOC2. IaC and advisory; a live-project provision is approval-gated.

**Model-invoked** — the agent runs it automatically when your request matches the triggers below. You can also invoke it by name.

## When to use

- designing
- provisioning
- reviewing
- hardening GCP; picking compute (Cloud Run
- GKE Autopilot
- Functions
- GCE)
- data (Firestore
- Spanner
- Cloud SQL
- BigQuery); writing Terraform; auditing IAM
- projects
- VPC
- CMEK
- audit logs; setting SLOs; mapping to SOC2

## What it does

1. State the workload and its bar.
2. Choose the most managed service that meets the constraint.
3. Apply the five Architecture Framework categories.
4. Place the project and lay the identity and security baseline.
5. Set the SLO and error budget.
6. Author as IaC and attach cost controls.
7. Review against the five categories and the red flags, then gate the mutation on a reviewed plan.

## Learn more

- [SKILL.md](SKILL.md) — the full procedure the agent follows.

---

*Generated from SKILL.md by `skill-readme`. Run `skill-readme` to refresh; do not edit by hand.*
