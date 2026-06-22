# Infrastructure safety

The judgment behind the devops steps. Infrastructure is the one place where a single
command takes down production, so the discipline is built around blast radius and a way
back. The gates (`skill-gate`) catch misconfiguration; this page catches the change that
lints clean and still causes an outage.

## Blast radius — the first question

Before applying anything, answer: *if this is wrong, what breaks, and how widely?*

- Does the change touch shared state (a VPC, a security group, an IAM policy, a cluster
  role) or something isolated?
- Is the target production or a lower environment? Production changes carry a higher bar.
- Is the change reversible in minutes, or does it destroy data?

A change with a large blast radius is split, staged, or rolled out behind a flag — never
applied wholesale.

## Plan before apply

- Always produce and read the plan (`terraform plan`, a Helm diff, an Ansible `--check`).
- The plan is reviewed by a human who names what it creates, changes, and **destroys**.
- A plan that shows a *replace* or *destroy* on a stateful resource (a database, a volume,
  a disk) stops the line until the data path is confirmed.

Red flags: applying without a plan; a plan with an unexplained resource replacement; a
diff nobody read; auto-apply on a production workspace.

## Destruction is guarded, not banned

Teardown is legitimate — uncontrolled teardown is not.

- A `destroy`, `kubectl delete`, or volume removal runs only against a **named**,
  non-production target with explicit, recorded approval.
- State is backed up before a destructive apply; the backup is verified, not assumed.
- The skill-lint destructive rule (SK040) blocks these commands inlined in a skill — they
  belong behind a guarded, approved step, never freehand.

## State and secrets

- **State** (Terraform state, cluster state) is the source of truth; it is remote,
  locked, and versioned. Never edit state by hand; never run two applies against one
  state at once.
- **Secrets** never land in a manifest, a plan output, an image layer, or a log. Inject
  them from a secret manager at runtime.
- **Least privilege**: the pipeline's credentials grant exactly the scope the change
  needs and no more.

## Rollback is part of the change

A change is not done until the way back is proven.

- Prefer immutable, versioned deploys that roll back by repointing to the previous version.
- A schema migration has a tested down path, or a forward-fix plan if down is impossible.
- The rollback is rehearsed in a lower environment, not discovered during the incident.

Red flags: a migration with no down path and no forward-fix plan; a deploy with no prior
version to return to; a rollback nobody has ever run.
