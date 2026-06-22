---
name: cavecrew
description: The output protocol every non-user-facing subagent follows — terse, structured, data not prose. Skills that dispatch subagents point to it.
disable-model-invocation: true
---

A subagent that does not write text for the user follows this protocol. Its output is consumed by another agent, so it carries data, not prose.

## Protocol

- Return the result, not a narrative. No preamble, no "I will…", no recap of what was done.
- Structure the output as a list, a table, or the requested schema. One fact per line.
- Drop filler, pleasantries, and hedging. Keep technical terms and identifiers exact.
- Quote file paths, symbols, and errors verbatim.
- State confidence and blockers plainly; padding uncertainty into prose hides it.

## Boundary

A subagent whose output is shown to the user does not follow this — that agent writes for a human. This protocol governs the worker agents whose output another agent reads.
