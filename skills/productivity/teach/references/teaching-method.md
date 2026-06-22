# Teaching method

A great explanation is calibrated, concrete, and checked. Calibrated: pitched at the
gap between what the learner knows and what they are reaching for. Concrete: grounded in
a real example from the actual material before any abstraction. Checked: confirmed by
the learner applying the idea, not by them nodding along.

The sections are ordered by weight. The first two carry the most leverage: an
explanation at the wrong level, or one that skips the example, fails no matter how
accurate the words are. The Feynman test runs underneath all of it — if the idea cannot
be said simply in the learner's own vocabulary, the explainer does not yet understand it
well enough to teach it.

## 1. Calibrate to the learner

The highest-weight move. An answer pitched above the learner sails past; one pitched
below insults and bores. Both teach nothing.

- What adjacent concept does the learner already hold? That anchor is the launch point.
- What single gap are they reaching across? Name the one target, not five.
- Does the question's vocabulary signal a novice, a practitioner, or an expert in a near field? Pitch to that, then adjust on their response.
- When the level is genuinely unknown, ask one calibrating question before explaining — cheaper than a wasted three-paragraph answer.

Over-explaining wastes a practitioner's time and buries the point; under-explaining
leaves a novice with words they cannot use. Calibration is the difference.

Red flags: an explanation that opens with the most abstract framing; the same depth
regardless of who is asking; defining terms the learner already uses fluently; reaching
across five gaps at once.

## 2. Move from concrete to abstract

The mind grips a specific case first and generalizes second. Lead with the example; let
the rule fall out of it.

- Show one concrete instance before stating the general principle.
- Build from the known to the unknown: start at the learner's anchor, take one step.
- One idea at a time — a second new concept in the same breath halves retention of both.
- Example-first, not example-as-afterthought: the example carries the lesson, the abstraction names it.

Red flags: the rule stated before a single concrete case of it; two new ideas
introduced in one sentence; an example bolted on after the abstraction as decoration; a
step that assumes a concept the learner has not been given.

## 3. Use analogies that fit, and know where they break

A good analogy borrows an existing mental model so the learner reuses structure they
already own. A bad one imports false structure they must later unlearn.

- Map the analogy to something the learner certainly knows, not to another unknown.
- State where the analogy holds and, explicitly, where it breaks — an unbounded analogy becomes a misconception.
- Drop the analogy once the real concept stands on its own; the scaffold is not the building.

Red flags: an analogy to a domain the learner does not know either; a metaphor carried
so far it teaches a falsehood; no statement of the analogy's limit; clinging to the
analogy after the concept is clear.

## 4. Teach from the actual material

The code, system, or artifact in front of the learner is the best textbook, because it
is the thing they actually need to understand.

- Explain this function, this module, this error — not a generic textbook stand-in.
- Point at real lines, real names, real behavior the learner can run and inspect.
- Tie every abstraction back to where it shows up in the material being taught.

Red flags: a generic example when a real one was available; an explanation that never
touches the learner's actual code; abstractions with no anchor in the material.

## 5. Progressive depth

Answer shallow first, then deepen on demand. The one-line answer serves the learner who
needs orientation; the layers serve the one who needs the mechanism.

- Open with the shortest true answer — one line, no unmet jargon.
- Add the next layer only when the learner asks or their application reveals they are ready.
- Let the learner pull depth rather than pushing all of it at once.
- Each layer rests on the one before, so a learner who stops early still leaves with something whole.

Red flags: the full mechanism dumped before the learner asks for it; a one-line answer
that smuggles in three undefined terms; depth pushed past the question that was asked;
layers that do not stand alone.

## 6. Check understanding

Comprehension is invisible until the learner produces something. A nod is not evidence.

- Ask the learner to apply the idea: predict an output, name the next case, find where it breaks.
- Watch for the blank spot — the specific sub-step where the application stalls is the real gap.
- Treat a wrong application as data about your explanation, not a failing of the learner.
- The bar for "taught" is a case neither of you walked through that the learner now handles.

Red flags: ending on "make sense?" instead of a task; accepting a nod as proof; never
asking the learner to produce anything; missing the blank spot because no application
was requested.

## Failure modes

| Failure | What it looks like | The fix |
|---|---|---|
| Jargon dump | Correct terms the learner has not met, stacked without grounding | Translate to the learner's vocabulary; define one term, in an example |
| Wrong level | Pitched over the head or beneath the floor of the learner | Recalibrate to the anchor; ask one level-finding question |
| No example | Pure abstraction, rule before instance | Lead with one concrete case from the material |
| Lecturing without checking | A monologue that never asks the learner to apply anything | Stop and pose an application; read the answer |
| Answering a different question | A technically rich reply to a question the learner did not ask | Restate the learner's actual question first, then answer that |
| Analogy run amok | A metaphor stretched until it teaches something false | State the limit; drop the analogy once the concept stands |

## Red flags (summary)

- The first sentence is the most abstract one.
- The same explanation would serve a novice and an expert unchanged.
- No concrete example precedes the general rule.
- Two new concepts arrive in one breath.
- The explanation never touches the learner's real code or system.
- It ends with "make sense?" and no task.
- An analogy has no stated breaking point.
- The learner was never asked to apply the idea to an unseen case.

## Worked example: teaching closures at a calibrated level

A learner asks, "What is a closure in JavaScript?" Their phrasing and prior questions
show they write functions and have used callbacks, but find closures slippery. The
calibration follows: **anchor** = functions and variables they already use; **gap** = a
function outliving the scope it was born in.

**One-line answer first** (section 5), in their vocabulary only: "A closure is a function
that remembers the variables from where it was created, even after that place has
finished running."

**Concrete before abstract** (section 2), one example from the kind of code they write:

```js
function makeCounter() {
  let count = 0;            // a local variable
  return function () {      // the inner function...
    count += 1;             // ...still sees `count`
    return count;
  };
}
const next = makeCounter(); // makeCounter has now returned
next(); // 1
next(); // 2   — count survived, held by the returned function
```

Lead from the known: "You already know a local variable dies when its function returns.
Here is the one twist — the returned function kept `count` alive." That is the single
idea; resist adding `this` binding, the module pattern, or memory leaks in the same
breath (section 2).

**An analogy that fits, with its limit** (section 3): "A closure is like a backpack the
inner function carries — it packed `count` when it was created and still has it later. Where
the analogy breaks: there is one shared backpack per call to `makeCounter`, not a fresh
copy each time you call `next` — that is why the count accumulates."

**Check by application, not nodding** (section 6). Do not ask "make sense?". Ask: "If I
call `makeCounter()` a second time into `const other = makeCounter()`, what does
`other()` return — and why?" The right answer, `1`, with the reason "a new call made a
new `count`," shows the idea landed. An answer of `3` reveals the blank spot — the
learner thinks `count` is shared across all counters — and tells you to re-explain from
the "one backpack per call" anchor (section 6), not to repeat the definition louder.

**Progressive depth on demand** (section 5): only once they answer correctly do you offer
the next layer — "want to see how this same mechanism powers private state and the
module pattern?" — and only if they pull it. The learner has been taught when they can
predict the output of a closure case neither of you wrote together.
