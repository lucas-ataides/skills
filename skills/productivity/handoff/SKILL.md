---
name: handoff
description: Write a handoff document so another agent or person resumes the work with zero context loss — goal, current state, what is done, what remains with next concrete actions, files touched, decisions, gotchas, and how to verify. Use when the user is pausing work, ending a session, switching agents, going off-shift, hitting a context limit, or asks to write a handoff, handover, transfer notes, or a resume-from-here document.
---

A handoff exists so a fresh reader resumes the work without asking the author a single question. The author is about to be unavailable — a new session, a teammate, a future self with no memory of today — and everything that lived only in the author's head must move onto the page before that happens.

The bar is resumability, not narration. A status report says what happened; a handoff says what to do next and hands over the means to do it. Write to the durable file, name the next concrete action, and surface the landmines, because the cost of a gap is a blocked reader who cannot reach back.

## Steps

1. **State the goal and pick the durable file.** Write one or two sentences naming what the work must ultimately deliver, then choose a committed file for the handoff (a `HANDOFF.md` at the repo root, a doc beside the work). A handoff in chat scrollback is lost on the next session. The step ends once the goal is written and the file path is fixed and open.

2. **Capture the current state against the goal.** Record where the work actually stands right now: the branch, what runs, what is broken, the last thing that happened. The reader's first question is always "where are we" — answer that question before anything else. The step ends once a reader could tell, from the file alone, how far the work has progressed toward the goal.

3. **Split done from remaining, and make each remaining item a concrete action.** List what is finished, then list what is left — and rewrite every remaining item as a next action specific enough to start cold: the file to open, the function to change, the command to run. "Finish validation" is a wish; "add the empty-input check in `parse()` at line 40" is an action. The step ends once no remaining item needs a follow-up question to begin.

4. **Record the load-bearing context: files, decisions, and gotchas.** Write the files and artifacts touched, the decisions made with the reason each one beats the alternative, and the gotchas — the landmines a reader would step on: the flaky test, the service that must boot first, the off-by-one that already cost an hour. A decision without its reason gets reversed; an unwritten gotcha gets re-discovered the hard way. The step ends once every non-obvious choice and trap from this session sits on the page.

5. **Write how to verify and name any blockers.** State the exact command or steps that prove the work is correct, the expected result, and any blocker that stops progress (a missing credential, a pending review, an open question) with who or what unblocks it. The step ends once a reader could run the verification and knows what stands in the way.

6. **Confirm resumability against the failure modes.** Read the handoff once as the fresh reader, checking it against [the handoff format](references/handoff-format.md): present current-state, concrete next-actions, documented gotchas, nothing stale. The step ends, and the handoff is done, only when that reader could resume the work without asking the author a single question.

See also: [the handoff format](references/handoff-format.md) for the full anatomy of a complete handoff, the resumability principle, handoff versus status report, the failure modes and red flags, and a worked example.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
