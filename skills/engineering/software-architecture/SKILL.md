---
name: software-architecture
description: Design a software system and record the decision as a tech lead — requirements and constraints first, dominant quality attributes next, then components, data, contracts, trade-offs, and an ADR. Use when the user asks to design a system, choose an architecture, pick between monolith and services, select a datastore, plan for scale, weigh a technical trade-off, or write an architecture decision record.
---

Design the system the way a tech lead does: let the dominant quality attributes drive the structure, not the technology you want to use. The leverage is in naming the constraints and the trade-offs out loud, then recording the decision so the next person inherits the reasoning, not just the result.

A design is a hypothesis under constraints. State the constraints, sketch the smallest structure that satisfies them, name what the structure costs, and capture the choice in an [ADR](references/architecture-method.md#the-adr).

## Steps

1. **Frame requirements and constraints.** Write the functional scope, the scale numbers (users, requests/sec, data volume, growth), and the hard constraints (budget, team size, deadline, compliance, existing stack). The frame holds once a back-of-envelope estimate of load and storage exists on the page — see [estimation](references/architecture-method.md#capacity-estimation).

2. **Rank the quality attributes.** From [the eight attributes](references/architecture-method.md#quality-attributes) — scalability, availability, latency, consistency, security, cost, operability, evolvability — pick the two or three that dominate this system and state why. The ranking holds once each chosen attribute carries a target number or a concrete bar, not an adjective.

3. **Sketch components and data.** Draw the [C4 container level](references/architecture-method.md#c4-levels): the deployable units, their responsibilities, and the data each one owns. The sketch holds once every container has one clear responsibility and the data model names its entities, keys, and access patterns.

4. **Define the contracts.** Specify the interface between each pair of containers that talk: the call style (synchronous request or asynchronous event), the payload shape, and the failure behavior. The contracts hold once a reader can trace one end-to-end request across every boundary it crosses.

5. **Analyze trade-offs against patterns.** For each major choice, name the [pattern](references/architecture-method.md#patterns-and-trade-offs) and its alternative, then state what each option costs in the attributes ranked at step 2. The analysis holds once at least one viable alternative per major choice has a stated reason for rejection.

6. **Check the failure modes.** Test the design against the [architecture failure modes and red flags](references/architecture-method.md#failure-modes): big design up front, resume-driven architecture, ignored NFRs, missing trade-off analysis, accidental distributed monolith. The check holds once no red flag is unanswered.

7. **Record the ADR.** Capture the central decision in an [ADR](references/architecture-method.md#the-adr): context, the decision, the alternatives considered, and the consequences (positive and negative). The work is done once the component sketch and an ADR with at least one rejected alternative and one named negative consequence both exist.
