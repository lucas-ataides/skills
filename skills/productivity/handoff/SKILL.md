---
name: handoff
description: Write a handoff document so another agent or person resumes the work with zero context loss — goal, current state, what is done, what remains with next concrete actions, files touched, decisions, gotchas, and how to verify. Use when the user is pausing work, ending a session, switching agents, going off-shift, hitting a context limit, or asks to write a handoff, handover, transfer notes, or a resume-from-here document.
---

A handoff exists so a fresh reader resumes the work without asking the author a single question. The author is about to be unavailable — a new session, a teammate, a future self with no memory of today — and everything that lived only in the author's head must move onto the page before that happens.

The bar is resumability, not narration. A status report says what happened; a handoff says what to do next and hands over the means to do it. The structure of the page is mechanical and the same every time, so a script stamps it (`scripts/handoff.sh`); the judgment is what fills each section, and that is the agent's work.

## Steps

1. **Stamp the document structure with the script.** Run `scripts/handoff.sh new [path]` to create the handoff from the fixed template (default `HANDOFF.md`, or the path given). The script writes the section skeleton atomically and never overwrites an existing file, printing the created or kept path. A handoff in chat scrollback is lost on the next session, so the durable file is the artifact. The step ends once the script prints the path and that file is open.

2. **Fill the Summary with the goal.** Write one or two sentences under `## Summary` naming what the work must ultimately deliver. The goal is the yardstick every later section is measured against. The step ends once a reader could state, from the Summary alone, what done looks like.

3. **Fill Current state against the goal.** Record under `## Current state` where the work actually stands right now: the branch, what runs, what is broken, the last thing that happened. The reader's first question is always "where are we" — answer that question before anything else. The step ends once a reader could tell, from the file alone, how far the work has progressed toward the goal.

4. **Fill What's done, then make each item under What's left a concrete action.** List finished work under `## What's done`; under `## What's left / next steps` rewrite each remaining item as a next action specific enough to start cold — the file to open, the function to change, the command to run. "Finish validation" is a wish; "add the empty-input check in `parse()` at line 40" is an action. The step ends once no remaining item needs a follow-up question to begin.

5. **Fill the run, risk, file, and contact sections.** Under `## How to run / build / test` write the exact command that proves the work correct and the result to expect; under `## Risks & gotchas` write the landmines a reader would step on (the flaky test, the service that must boot first); under `## Key files & links` write the files and artifacts touched; under `## Contacts / owners` write any blocker with who or what clears it. A decision without its reason gets reversed, so record the reason beside each non-obvious choice. The step ends once every trap, file, and blocker from this session sits on the page.

6. **Confirm resumability against the failure modes.** Read the handoff once as the fresh reader, checking it against [the handoff format](references/handoff-format.md): present current-state, concrete next-actions, documented gotchas, nothing stale. The step ends, and the handoff is done, only when that reader could resume the work without asking the author a single question.

## Scripts

- `scripts/handoff.sh new [path]` — stamp a handoff document from the fixed template (default `HANDOFF.md`). The command is idempotent — the file is created only when absent, the write is atomic, and the created or kept path is printed. The agent owns the content; the script owns the structure.
- `scripts/handoff.sh --selftest` — verify the stamper in a throwaway sandbox: the file appears with every section header, and a re-run preserves an appended marker (no overwrite). Prints `handoff selftest: ok` and exits 0.

See also: [the handoff format](references/handoff-format.md) for the full anatomy of a complete handoff, the resumability principle, handoff versus status report, the failure modes and red flags, and a worked example.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
