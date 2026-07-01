# Project brain

An LLM wiki for this repo (Karpathy pattern). The agent owns it: read this index first, then
the pages a task touches. On a change, update the page, refresh its line here, and append
`log.md`. Synthesis only — never restate the code; flag contradictions with their source.

## Architecture
- [[architecture]] — the system map: authoring → gates → distribution → runtime

## Concepts
- [[determinism-doctrine]] — the root doctrine every skill inherits, and why
- [[second-brain-protocol]] — prime on the way in, feed on the way out

## Systems
- [[toolchain]] — the skill-* CLIs, skillkit, and where each gate runs
- [[plugin-distribution]] — packaging, SHA versioning, the router hook, Cursor export

## Decisions
- [[consolidation-2026-06]] — 47 → 43: the four merges, and what deliberately stayed apart

## Reviews
- [[review-2026-07-01]] — full-session review: defects found, fixes shipped, open risks
