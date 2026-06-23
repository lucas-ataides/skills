---
name: teach
description: Explain a concept, codebase, or system at exactly the learner's level — calibrate first, build from the known, check understanding — never a jargon dump. Use when the user asks you to teach, explain, walk through, or help them understand a concept, function, module, error, or system; when they ask "how does X work", "what is X", "ELI5", or "I don't get X"; when a prior explanation missed and they ask again.
---

Teach the way a great mentor does: meet the learner where they are, then move them one step at a time from what they already know to the thing they do not. Explanation that lands at the wrong level — over their head or beneath them — teaches nothing, however correct it is.

Calibrate before you explain. The depth, the moves, the failure modes, and a worked example live in [the teaching method](references/teaching-method.md).

## Steps

1. **Find the level.** Ask, or infer from the question's vocabulary, what the learner already knows about this topic — the adjacent concept they have, and the one gap they are reaching across. The step is done when one prior anchor and one target gap are named.

2. **Read the material.** Open the actual code, system, or concept being taught, so the explanation rests on this codebase rather than a generic template. The step is done when the specific file, function, or behavior to teach from is in hand.

3. **Answer in one line first.** Give the shortest true answer — one sentence, no jargon the learner has not met — before any layer beneath it. The step is done when a one-line answer exists that uses only words from the learner's anchor.

4. **Build from the known with one example.** Lead from the named anchor to the target through a single concrete example drawn from the material, one idea at a time. The step is done when one worked example connects the anchor to the gap and no second idea was introduced alongside it.

5. **Check by application, not by nodding.** Ask the learner to apply the idea — predict an output, name the next case, spot where it breaks — rather than asking "make sense?". The step is done when the learner has produced an answer that reveals whether the idea landed or hit a blank spot.

6. **Layer or repair on the response.** A correct application earns the next layer of depth on request; a wrong one earns a re-explanation from a different anchor, not a louder repeat. The step is done when the learner can apply the concept to a case neither of you walked through.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
