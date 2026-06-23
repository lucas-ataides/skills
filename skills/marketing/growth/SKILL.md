---
name: growth
description: Run a founder's growth loop — generate and prioritize growth ideas, instrument the funnel and revenue metrics from one source of truth, then compound the result by cutting churn. Use when the user wants growth or marketing ideas, a growth strategy, or ideas scored with ICE/RICE; wants to set up revenue ops, design a funnel, define lead/MQL/SQL stages, or compute CAC, LTV, LTV:CAC, payback, win rate, or NRR; or wants to reduce churn, lift retention, run a save or win-back play, or report GRR/NRR.
---

Growth is one loop, not three jobs: an engine that **finds** growth (generate and
prioritize ideas), **measures** it (one funnel, real unit economics from a single
source of truth), and **compounds** it (retention that turns each won customer into
the fuel for the next). The three connect — a ranked idea is a bet, the funnel proves
whether the bet paid, and retention decides whether the payoff compounds or leaks. A
metric a founder cannot trust breaks the loop, so spend the judgment once on
definitions and let every later read be mechanical.

Ideas are cheap; the founder's time to build and run them is the scarce resource, so
prioritization is the point. A funnel a founder cannot reason about is worse than
none, because a false number drives a false decision. A cancellation is the lagging
echo of a decision the customer made weeks earlier, so the leverage in churn is the
leading signal, not the discount. Three references carry the depth — read the one a
step names before running that step:

- [references/idea-generation.md](references/idea-generation.md) — generation frameworks, divergent-then-convergent discipline, ICE and RICE, honest scoring.
- [references/funnel-metrics.md](references/funnel-metrics.md) — stage definitions, metric formulas, one source of truth, handoff SLAs, the LTV:CAC and payback math.
- [references/retention.md](references/retention.md) — leading churn signals, health segmentation, intervention playbooks, dunning, GRR/NRR/cohort metrics.

## Steps

1. **Frame the thesis, the goal, and the constraint.** State the growth thesis in one
   sentence (the single mechanism this business bets on to acquire and keep
   customers), the one metric that mechanism moves, the audience, and the real budget
   or time limit. This step is done when thesis, metric, audience, and constraint each
   sit on one written line.

2. **Diverge, then converge to a ranked few.** Run several generation frameworks as
   separate prompts (the channel list / Bullseye, growth loops vs funnels,
   jobs-to-be-done, competitor teardown, 10x not 10%) deferring all scoring, then
   cluster the raw list, cut the off-thesis ideas, and score the survivors on one
   model from [references/idea-generation.md](references/idea-generation.md). This step
   is done when 15 or more raw ideas collapse to 6–8 scored bets, each carrying an
   ICE or RICE value, a growth-mode tag (loop or funnel), and a one-line reason.

3. **Pick the top bets and attach a success metric to each.** Commit to the
   highest-ranked bets the constraint allows, name the deferred tail as not-now rather
   than dropping it silently, and give every pick one quantified metric and a numeric
   threshold with a time window. This step is done when the picks fit the stated
   constraint and each pick names one metric and one threshold.

4. **Define the funnel and instrument it from one source of truth.** Write one binary
   entry condition and one owner per stage across the eight named stages (lead, MQL,
   SQL, opportunity, closed-won, closed-lost, expansion, churn) from
   [references/funnel-metrics.md](references/funnel-metrics.md), designate the CRM as
   the system of record, then write each metric's formula and the exact fields it
   reads beside the dashboard: CAC, LTV, LTV:CAC, payback, per-stage conversion, win
   rate, pipeline coverage, and NRR. This step is done when two people pulling the same
   metric on the same day get the same value.

5. **Set targets, then find the bottleneck.** Attach a target to each metric (LTV:CAC
   at or above 3:1, payback under 18 months, pipeline coverage at 3×–4× of the period
   goal, a conversion target per adjacent stage pair), then rank the gaps against
   target. This step is done when one stage is named the bottleneck, its conversion gap
   is quantified, and one owned action is recorded against it.

6. **Stand up retention signals and route the base by health.** Instrument the four
   leading churn signals from [references/retention.md](references/retention.md) — usage
   decay against the account baseline, failed payments, support sentiment, unmet
   activation — each with a threshold and a data source, then score every account into
   one health bucket (at-risk, healthy, power user). This step is done when each
   signal carries a threshold and a source, and each account carries exactly one
   segment, never a single blended MRR number.

7. **Diagnose each at-risk driver, match one play, and close the loop.** For an
   at-risk account, name the single driver (stalled activation, usage decay, stated
   cancel, failed payment), assign the one play whose trigger matches it (onboarding
   nudge, value reminder, save offer or win-back, dunning) holding the discount as the
   last lever, then report GRR, NRR, logo churn, and the cohort curve side by side and
   feed every confirmed driver back into the signals. This step is done when each
   at-risk account carries one driver and one matching play, every play has a closing
   metric, and the four retention metrics are reported together with the latest
   cohort's drivers recorded.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
