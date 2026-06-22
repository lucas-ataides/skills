# Thinking moves

The reference behind the brainstorming procedure. Thinking partners earn their keep at three moments: when the question is wrong, when the first idea is mistaken for the only idea, and when a simple need gets dressed as a hard one. The sections below give the moves one phase at a time — the framing discipline, the divergent and convergent halves, the bias toward simplicity, the techniques that unstick a stalled list, the stop condition, the failure modes, the red flags, and a full worked example.

The order is the method. Frame before generating, generate before judging, judge on simplicity, and stop on a next step. The leverage is in keeping those four phases separate, because collapsing any two is how thinking goes wrong.

## Framing — the problem behind the problem

The highest-leverage move. A perfect answer to the wrong question is worth nothing, so the first work is naming the question worth answering. The named problem is almost never the real one: it arrives already shaped as a solution ("I need a queue"), and the shape hides the outcome the user actually wants ("I need this request to return fast").

The move: take the stated problem, ask what solving it would *get* the user, and keep asking until the answer is an outcome rather than a mechanism. Then check whether a different mechanism reaches the same outcome cheaper. A request framed as "add a cache" reframes to "the dashboard is slow," which opens options the cache framing hid — a smaller query, a narrower payload, a precomputed view.

The check: the underlying question is written as an outcome, and the user agrees that reaching it would settle the request.

## Divergent thinking — generate before you judge

The second phase opens the space of answers. The single rule is suspension of judgment: every option goes on the page before any option is critiqued. The reason is mechanical, not motivational — a critique voiced mid-generation kills the branch it lands on before anyone sees where the branch led, and the best idea is often two steps past a bad-sounding one.

- **Quantity first.** Three distinct directions is the floor, not the target. The first idea is an anchor, the second a reaction to it, and the divergence only really starts at the third.
- **Distinct, not adjacent.** Three flavors of the same approach is one option wearing three hats. Push for directions that disagree about the shape of the answer, not its parameters.
- **Defer the cost question.** "That's too expensive" is a convergent thought. Park it; the next phase is where cost decides.

The check: three or more genuinely different options sit on the page, none yet judged.

## Convergent thinking — pick the simplest that works

The third phase closes the space. Now judgment is welcome, applied through one filter: what does the framed question actually need? Score each option against that need, drop the ones that overshoot or undershoot, and pick the survivor with the fewest moving parts.

Simplicity is the tie-breaker and usually the decider. "Simplest that works" carries a load-bearing qualifier — *that works* means the full framed need, carve-outs included, never a subset that only demos. A solution that is simple because it ignores half the requirement is not simple; such a solution is merely incomplete. The same bias drives the [least-code](../../least-code/SKILL.md) ladder for implementation, pulled one level up to the choice of direction: reach for the elaborate option only after the plain one is shown not to cover the need.

The check: one direction is chosen, and its advantage over the runners-up is stated in a sentence tied to the framed need.

## The techniques

Reach for these when the option list stalls, the framing feels stuck, or the chosen direction needs a stress test. Each is a specific prompt, not a mood.

### First principles

Strip the problem to what must be true and rebuild from there, ignoring how it is usually done. The move: ask "what are the facts that cannot change here?" — the physics, the contract, the hard constraint — then ask what those facts alone permit. It breaks the grip of convention and surfaces options that the by-analogy framing ("everyone uses a message bus") never reaches. Use it when every option on the list is a variation of the standard approach.

### Inversion — what would make this fail

Flip the question from "how do I succeed?" to "what guarantees failure?" The move: list the ways the goal could be defeated, then invert each into a thing to avoid or ensure. Inversion finds failure modes that forward thinking skips, and it doubles as the stress test for a chosen direction — name the single assumption whose collapse breaks the choice. A direction with no nameable failure mode has not been examined — that direction has been hoped at.

### The 5 whys

Chase a symptom down to its cause by asking "why" of each answer, roughly five times, until the answer stops being a mechanism and becomes a root. The move guards against fixing symptoms: "the page is slow" → why → "the query is slow" → why → "it scans the table" → why → "no index on the filter column" — and only the last answer is worth acting on. Use it when the stated problem smells like a symptom of something upstream.

### Constraints as a creativity tool

Add an artificial constraint to force invention. The move: ask "what if I had one day?" or "what if I could not add a dependency?" or "what if this had to be one file?" A tightened budget collapses the option space to the essential and routinely surfaces a simpler answer that the unconstrained framing buried under nice-to-haves. Constraints are not the enemy of a good idea; the blank page is.

### The "what would make this trivial" prompt

Ask which single constraint, dropped or added, collapses the whole problem to almost nothing. The move hunts for the reframe that beats every solution to the original problem: "if the data were already sorted, this is one line"; "if duplicates were allowed, the dedup logic vanishes." A problem made trivial by a cheap reframing is the best outcome a brainstorm can reach — better than the cleverest solution to the hard version. Run it early, because a trivial reframing makes the rest of the work moot.

## Knowing when to stop

Brainstorming ends, and the end is a condition, not a feeling. The stop condition is a clear next step: a concrete action the user can take — a file to open, a spike to run, an experiment to design, a smaller question to settle. Reaching that, the thinking has done its job and one more round only delays the doing.

Two opposite errors crowd the stop point. Stopping too early — grabbing the first option before the space is opened — is premature convergence. Refusing to stop — generating a tenth option when a next step already exists — is analysis paralysis. The next-step test cuts both: stop when one exists, and not before.

## Failure modes

The four ways this thinking reliably goes wrong. Each maps to a phase collapsed or skipped.

- **Premature convergence.** Locking onto the first plausible option before the space is opened. The first idea is an anchor, and treating it as the answer skips divergence entirely. The fix is the floor of three distinct options, judged only after the list is complete.
- **Analysis paralysis.** Generating and re-generating without ever choosing, mistaking option volume for progress. More options past a workable one is not diligence — the extra churn is avoidance of the commitment. The fix is the stop condition: converge once a clear next step exists.
- **Solving the wrong problem.** Answering the stated question without checking it is the real one, so the effort lands on a symptom or a mis-framed need. Solving the wrong problem is the most expensive failure because the work is competent and wasted. The fix is the framing phase and the 5 whys — confirm the outcome before generating answers for it.
- **Complexity worship.** Preferring the elaborate option because it looks more serious, more general, or more impressive than the plain one that covers the need. A bias toward complexity reads sophistication as value, when the elaborate option is cost with no return. The fix is the simplest-that-works filter — the burden of proof sits on the complex option, not the simple one.

## Red flags

Signals that the thinking has drifted off the method:

- The first option named is the option chosen — divergence was skipped.
- Every option is a variation of one approach — the list is adjacent, not distinct.
- The critique started before the list was complete — judgment leaked into divergence.
- The chosen direction has no nameable failure mode — it was hoped at, not stress-tested.
- The problem statement is a solution ("I need a queue") and was never traced to an outcome.
- The chosen option is the most elaborate one and the reason is that it is "more flexible" — complexity worship.
- A tenth option appears while a usable next step already exists — paralysis dressed as thoroughness.
- The simple option was dismissed as "too simple" rather than "does not cover the need" — simplicity confused with inadequacy.

## Worked example — a vague problem to a simple direction

The request, as stated: "We need a notification system so users know when their report is ready."

**Frame — the problem behind the problem.** "Notification system" is a solution. What does it get the user? A user who started a long report finds out the moment it finishes, instead of refreshing the page. The outcome is *the user learns their report is done without watching for it*. The 5 whys confirms the root sits at "the report is slow enough that waiting is painful" — but the committed need is the knowing, not the speed, so the framed question is: how does a user learn their report finished, hands-off?

**Diverge — options, unjudged.** Four distinct directions, no critique yet:

1. A full notification service — events, a queue, a delivery layer, per-channel preferences.
2. An email sent when the report job completes.
3. The browser tab polls a status endpoint and shows a banner when ready.
4. A server-sent-events stream that pushes the "done" signal to the open page.

**Probe for the trivial version.** What would make this trivial? Constraint added — "the user keeps the tab open while waiting," which the usage data supports. With that, the whole delivery problem collapses: the page that started the report is still on screen to receive the answer. The trivial framing makes options 1 and 2 overshoot.

**Converge — simplest that works.** Against the framed need (hands-off knowing, tab stays open), score the four. Option 1 is a system for a future of many notification types that is not committed — complexity worship, dropped. Option 2 works but reaches outside the app for a signal the open page could get directly, and adds email deliverability as a new failure surface. Option 4 is clean but needs streaming infrastructure the app does not yet run. Option 3 — poll a status endpoint, show a banner — covers the full need with parts the app already has. Chosen, because it meets the framed need with the fewest new moving parts.

**Stress-test by inversion.** What makes polling fail? The load-bearing assumption is "the tab stays open." Inverting: a user who closes the tab gets nothing. Acceptable for the committed need (the data shows tabs stay open), and recorded as the ceiling — when background delivery becomes a real requirement, option 2 or 4 is the upgrade path.

**Stop on a next step.** A clear next action exists: add a `GET /reports/{id}/status` endpoint and a small client poll-and-banner. The brainstorm is done — it converged from a vague "notification system" to a bounded, simple direction with a named ceiling and a first step, and the elaborate option was set aside not because it was bad but because the framed need never asked for it.
