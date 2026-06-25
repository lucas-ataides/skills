---
name: client-satisfaction
description: Manage and improve a client relationship's health by reading the leading signals before the client goes quiet, scoring health red/yellow/green, then matching cadence and intervention to the score. Use when assessing client satisfaction, running a check-in or QBR, setting scope or timeline expectations, handling a complaint or cooling relationship, gathering NPS/CSAT feedback, asking for a referral or case study, recovering an at-risk account, or recording client health in the vault.
---

Manage a client relationship the way a seasoned consultant does: a churned client is
the lagging echo of a decision the client reached weeks earlier in silence, so the
leverage is in the leading signals, the health score, and the intervention matched to
what tripped. Silence is not satisfaction. Read the signals, score the health, then
run the play that fits.

Messaging the client is an external mutation: draft the message and stop, because a
sent message changes a live relationship and cannot be unsent. The founder reviews and
sends by hand.

Work the reference for the depth behind each step: [client health](references/client-health.md).

## Steps

1. **Define the client record and instrument the signals.** Name the client, the
   engagement, and the period under review, then read the five leading signals from
   the reference against the client's own baseline: response latency, sentiment,
   usage and engagement, payment timeliness, and scope tension. Delegate the client
   note and its links to projects, people, and commitments to
   [second-brain](../../obsidian/second-brain/SKILL.md) — capture it with
   `vault.sh capture client "<name>" company="<company>"`. This step is done once each of
   the five signals has a baseline and a current reading, not a single revenue number.

2. **Score the health with the rubric script, not by eye.** Judge each signal onto its
   fixed scale and write the readings to an `inputs.json` of the shape
   `{"factors": {"usage": 0-5, "sentiment": 0-5, "payment": 0-5, "support_load": 0-5,
   "nps": -100..100, "engagement": 0-5}}`. Run `scripts/health-score.py score inputs.json`
   to compute the 0-100 score and its red/amber/green band from the constant weighted
   rubric — the number comes from the script, never from the agent's judgment of the
   total. The band is the routing key for the actions below, so a misread band runs the
   wrong play. The script's amber band is the yellow band the steps below route on —
   the two names denote one middle state. This step is done once the script has printed
   one score, its per-factor contributions, and one RAG band on a zero exit.

3. **Run the cadence at the intensity the band sets.** Hold the standing rhythm for a
   green client — regular check-ins plus the quarterly business review — and add an
   unscheduled touch aimed at the tripped signal for a yellow client. Set scope,
   timelines, and status by the under-promise-and-over-deliver discipline so no
   delivery becomes a surprise. This step is done once the next touch is scheduled and
   the live expectations match the client's current picture.

4. **Act on a yellow or red band.** Diagnose the single driver behind the tripped
   signal — a value-perception gap, a delivery slip, a scope drift, or a cooling
   contact — then run the recovery sequence: surface, acknowledge, remediate, follow
   up. A red band escalates to a same-week, named-human conversation. This step is done
   once each at-risk client carries one named driver and one dated, owned remediation.

5. **Capture feedback and harvest advocacy.** Pulse the relationship with NPS or CSAT
   against the client's own trend, paired with the qualitative "why" beneath the
   number. Gate any referral, case study, or testimonial ask on a green band and a
   recent win, because a mistimed ask spends a recoverable relationship. This step is
   done once the latest pulse has a recorded score and a qualitative note, and any
   advocacy ask is gated on a green band.

6. **Draft client messages for approval, never send.** Prepare each outbound message
   the steps above call for — the check-in, the QBR invite, the acknowledgement, the
   feedback ask, the referral request — as a draft, then stop. Sending is an external
   mutation that waits on explicit founder approval. This step is done once every
   client-facing message sits as a reviewed draft awaiting the founder's send.

7. **Record and correlate in the vault.** Append the health band, the signal readings,
   and the diagnosed driver to the client's dated health log, and write the linked
   notes through [second-brain](../../obsidian/second-brain/SKILL.md) rather
   than by hand. Read the health log beside the linked project and commitment notes so a
   dip lines up with its cause and the next quarter routes on evidence. This step is done
   once the current assessment is logged, linked, and read against its driver.

## Scripts

The agent judges the signals; the script computes the score. A run of `--selftest`
builds fixtures, asserts the rubric, and exits 0:

- `scripts/health-score.py` — read an `inputs.json` of judged factors, normalize each
  against its fixed range, apply the constant weighted rubric, and print the 0-100
  score, the per-factor contributions, and the red/amber/green band. An out-of-range
  or missing factor is rejected with a clear message and a nonzero exit.

## Done when

- Each of the five leading signals carries a baseline and a current reading.
- The client holds exactly one health band — red, yellow, or green — backed by signals.
- The next cadence touch is scheduled at the intensity the band sets.
- Every yellow or red client carries one named driver and one dated, owned remediation.
- The latest feedback pulse has a score and a qualitative note recorded.
- Every client-facing message sits as a reviewed draft awaiting the founder's send.
- The assessment is appended to the health log and linked to projects, people, and commitments.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
