---
name: employee-management
description: Manage and develop direct reports as a tech lead or founder, with state recorded in the Obsidian second brain. Use when the user mentions a 1:1, one-on-one, direct report, their team, managing people, a growth or development plan, setting expectations or goals, giving or structuring feedback (SBI), a performance review, delegation, a struggling or underperforming report, a PIP, or wants a person note, 1:1 log, or feedback note in the vault.
---

Manage people the way a strong tech lead does: set the expectations, run a steady 1:1 rhythm, give feedback while it is still cheap, grow each report on a real path, and address trouble early — with every signal recorded in the Obsidian second brain so judgment rests on a record, not memory. The depth bar and the worked examples live in [references/people-management.md](references/people-management.md). Note CRUD is delegated to [second-brain](../../obsidian/second-brain/SKILL.md); this skill decides *what* to record, never re-implements the file write.

People data is sensitive. Mark sensitivity in note frontmatter at capture with the field `sensitivity=private` (for example, `vault.sh capture feedback "SBI for Ada" sensitivity=private`), and summarize private detail rather than copying it verbatim.

## Steps

1. **Set the cadence and the expectations.** Establish a recurring 1:1 slot per report (weekly or fortnightly), and write each report's role expectations and current goals into a person note. Step is done when each report named in the prompt has a person note carrying a 1:1 cadence and an explicit, written expectation for the role.

2. **Run the 1:1 with the report owning the agenda.** Open the slot with the report's topics first, listen more than talk, and close on agreed next actions. Capture themes, blockers, and actions in a dated 1:1 log linked to the person note — `vault.sh capture 1on1 "<report> 1:1 <date>" sensitivity=private`, then link it to the person. Step is done when the session has a 1:1 log recording the report's agenda items, the decisions, and the owner of each next action.

3. **Give feedback timely and specific, in SBI form.** Name the Situation, the Behavior, and the Impact; aim the feedback at the behavior, not the person; balance recognition with correction. Record each instance as a dated feedback note linked to the person — `vault.sh capture feedback "SBI <report> <topic>" sensitivity=private`. Step is done when the feedback is delivered close to the event and a feedback note states situation, behavior, and impact in three distinct parts.

4. **Track growth and performance with examples as they happen.** Maintain a growth plan that pairs stretch goals with comfort-zone strengths, and log concrete performance examples — positive and negative — continuously through the cycle. Step is done when the person note holds a current growth plan plus two or more dated, concrete examples logged since the last review.

5. **Address issues early, clearly, and on the record.** Raise a concern at the first signal, state the gap and the required change plainly, offer support, and document the conversation and the agreed plan. Step is done when a documented, dated record states the specific gap, the expected change, the support offered, and the review date — produced before a formal process opens.

6. **Record and correlate in the vault.** Link each person note to the projects the report touches, their 1:1 logs, and their feedback notes, so themes surface across time. Confirm sensitivity is marked on private notes. Step is done when the person note resolves links to its 1:1 logs, feedback notes, and projects, and a private note carries a sensitivity marker in frontmatter.

## Done when

- Each report named in the prompt has a person note with a written cadence, role expectations, and a current growth plan.
- Recent 1:1s and feedback exist as dated, linked notes — not as unrecorded memory.
- An active performance concern has a dated, documented record predating a formal process.
- Private notes carry a sensitivity marker, and private detail is summarized rather than copied.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
