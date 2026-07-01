---
name: overdrive
description: Maximum-effort mode — escalate rigor far above the default when the stakes justify it. Generate several independent approaches and pick the strongest, verify every claim against real output, enumerate edge cases, self-critique adversarially, and cross-check with tools and tests. Use when the task is high-stakes, irreversible, security- or money-sensitive, or a flagship deliverable, and the user asks to go all-out, do it properly, leave nothing to chance, or get it exactly right.
---

Overdrive is the deliberate decision to spend far more effort than the default, because the task earns it. The default pass optimizes for speed and good-enough; overdrive optimizes for being right under scrutiny. The mode is expensive in time and tokens, so the first move is to confirm the task deserves it — overdrive on a throwaway script is itself a failure, the gold-plating the foundation doctrine warns against.

What overdrive changes, when it is warranted versus wasteful, the cost calculus, the failure modes, and a worked normal-versus-overdrive contrast live in [the overdrive protocol](references/overdrive-protocol.md). Read it before engaging the mode.

## Steps

1. **Justify the spend.** Name why this task clears the overdrive bar: high stakes, irreversibility, a security or financial blast radius, or flagship visibility. Record the rough cost in extra passes against that payoff. The step is done once two written sentences name the stake and confirm the payoff beats the cost. A failed payoff test instead selects the default pass.

2. **Generate independent approaches.** Produce two or three genuinely distinct solutions, not one solution with cosmetic variants, each with its trade-offs stated. Score them against the stated stake. The step is done when the candidate count is at least two and a one-line rationale names the chosen approach over the rejected ones.

3. **Verify every claim against real output.** Run the code, the query, or the command, and read the actual result rather than asserting the expected one. Capture the observed output beside each claim the deliverable makes. The step is done when no load-bearing claim rests on assumption and each one cites the output that confirms it.

4. **Enumerate the edge cases.** List the boundary, empty, large, malformed, and concurrent inputs the task implies, then handle or explicitly defer each listed case. The step is done when the enumerated list is exhausted and each listed case carries a resolution or a recorded reason to skip it.

5. **Self-critique adversarially.** Argue against the deliverable as a hostile reviewer would: name the weakest assumption, the likeliest failure, and the part a critic attacks first. Address each objection raised. The step is done when the strongest objection has a written answer or an accepted, documented limitation.

6. **Cross-check with tools and tests.** Run `skill-gate --strict` at the repo root, or the project's lint, type, and test gates, against the change. The step is done when the gates exit zero, with any remaining failure recorded as a known finding rather than left silent.

7. **Decide done or stop.** Confirm steps 1 through 6 each reported their completion criterion, and that the effort stayed aimed at the stake rather than drifting into polish nobody asked for. The deliverable is done when every step is checked off and one sentence states that the rigor matched the stakes.

See also: [the foundation doctrine](../../meta/foundation/SKILL.md). Prove done with [verification-before-completion](../verification-before-completion/SKILL.md); after the gates are green, finish a user-facing surface with [polish](../polish/SKILL.md).
