---
name: software-architecture
description: Design a software or cloud system as a tech lead and emit the artifacts — requirements and quality attributes first, then components, data, contracts, cloud building blocks; finish by emitting C4 diagrams (Mermaid) and an ADR. Use when the user asks to design a system or cloud architecture, choose monolith vs services, pick a datastore, plan for scale, select regions or network topology, weigh build-vs-managed, draw a C4 or sequence diagram, or write an architecture decision record.
---

Design the system the way a tech lead does: let the dominant quality attributes drive the structure, not the technology you want to use, and not the cloud vendor's default. The leverage is in naming the constraints and the trade-offs out loud, then emitting the artifacts — the diagrams a reader can navigate and the [ADR](references/adr-and-docs.md) the next person inherits — so the reasoning survives the meeting, not just the result.

A design is a hypothesis under constraints. State the constraints, rank the attributes, sketch the smallest structure that satisfies them (on-premise or on a cloud), name what the structure costs, then emit the [C4 diagrams](references/diagrams-c4-mermaid.md) and the [ADR](references/adr-and-docs.md) as the deliverables.

The depth bar across the seven steps is [the design process](references/design-process.md). Cloud-specific moves live in [cloud architecture](references/cloud-architecture.md); the two output formats live in [C4 diagrams](references/diagrams-c4-mermaid.md) and [ADR and docs](references/adr-and-docs.md).

## Steps

1. **Frame requirements and constraints.** Write the functional scope, the scale numbers (users, requests/sec, data volume, growth), and the hard constraints (budget, team size, deadline, compliance, data residency, existing stack). The frame holds once a back-of-envelope estimate of load and storage sits on the page — see [capacity estimation](references/design-process.md#capacity-estimation).

2. **Rank the quality attributes.** From [the eight attributes](references/design-process.md#quality-attributes) — scalability, availability, latency, consistency, security, cost, operability, evolvability — pick the two or three that dominate this system and state why. The ranking holds once each chosen attribute carries a target number or a concrete bar, not an adjective.

3. **Sketch components and data.** Draw the deployable units, each with one responsibility, and the data each one owns — entities, keys, access patterns — per [components and data](references/design-process.md#sketch-components-and-data). The sketch holds once every container has one clear responsibility and the data model names its entities, keys, and access patterns.

4. **Place it on infrastructure and define the contracts.** Map each component to a building block, taking the [build-vs-managed call](references/cloud-architecture.md#build-vs-managed), the [region and availability-zone topology](references/cloud-architecture.md#regions-zones-and-residency), and the [network layout](references/cloud-architecture.md#network-topology); for a cloud target, take a stance on each [Well-Architected pillar](references/cloud-architecture.md#the-well-architected-pillars). Then specify each contract: call style, payload shape, failure behavior. This step is done once every component names its building block and a reader can trace one end-to-end request across every boundary it crosses.

5. **Analyze trade-offs against patterns.** Per major choice, name the [pattern](references/design-process.md#patterns-and-trade-offs) and its alternative, then state what each option costs in the attributes ranked at step 2. The analysis holds once at least one viable alternative per major choice has a stated reason for rejection.

6. **Check the failure modes.** Test the design against the [system-design failure modes and red flags](references/design-process.md#failure-modes) and, for a cloud target, the [cloud red flags](references/cloud-architecture.md#failure-modes-and-red-flags): big design up front, resume-driven architecture, ignored NFRs, missing trade-off analysis, accidental distributed monolith, single-AZ production, click-ops. The check holds once each listed red flag is marked absent or recorded as an accepted risk with a named owner.

7. **Emit the diagrams and the ADR.** Produce the [C4 diagrams](references/diagrams-c4-mermaid.md) (System Context, then Container, then Component on the contested container) plus a sequence or ER diagram where a flow or schema is load-bearing, all in fenced `mermaid` blocks; then record the central decision as an [ADR](references/adr-and-docs.md#the-adr-template) and write the [one-page design doc](references/adr-and-docs.md#the-design-doc). The work is done once the System Context and Container diagrams both render and an ADR with at least one rejected alternative and one named negative consequence exists.

## See also

- [aws-toolkit](../../cloud/aws-toolkit/SKILL.md), [azure-toolkit](../../cloud/azure-toolkit/SKILL.md), [gcp-toolkit](../../cloud/gcp-toolkit/SKILL.md) — once the architecture names a cloud vendor, the matching toolkit carries the provider-specific service map, security baseline, and IaC.
- [code-review](../code-review/SKILL.md) — the review lenses that judge a change against the architecture it lands in.

See also [project-context](../project-context/SKILL.md) to keep the project's AGENTS.md and task list current.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
