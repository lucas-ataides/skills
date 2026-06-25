---
name: copywriting
description: Write, edit, and ethically persuade with marketing copy — landing pages, headlines, CTAs, product descriptions, sales pages, email — for a founder selling through a personal brand. Use when the user asks to write or rewrite a headline, hero, landing page, sales page, value proposition, or CTA; to tighten, polish, or copy-edit bloated or weak copy; or to decide whether a tactic (scarcity, urgency, social proof, a trial) is honest persuasion or a manipulative dark pattern.
---

Marketing copy earns attention, then a decision. A draft converts when one reader recognizes one problem, believes one claim, and takes one action — so the work is subtraction and proof, not adjectives. The full arc is one procedure: name the reader and the contract, write against a framework, cut the draft tighter, prove every claim, and stop at the line where persuasion turns into manipulation.

Push the work down a ladder before reaching for prose: a stated reader and offer remove guesswork, a named framework removes blank-page drift, a proof inventory removes unsupported hype, and the ethics tests remove the dark patterns that convert this week and cost the founder's trust next week. Write only the irreducibly creative line — the headline turn, the benefit phrasing — after the structure is fixed.

Three references carry the depth. Read [frameworks.md](references/frameworks.md) for the drafting craft (AIDA, PAS, BAB, the 4 Ps, headline patterns, the rule of one, features-vs-benefits, proof, voice). Read [editing-passes.md](references/editing-passes.md) for the ordered passes that tighten a draft. Read [persuasion.md](references/persuasion.md) for Cialdini's principles, the conversion biases, the three ethics tests, and the forbidden dark patterns.

## Steps

1. **Fix the contract: reader, offer, action.** Write one sentence each — who the reader is and the pain they feel right now, what the offer is and the one transformation it delivers, and the single action this copy must produce (buy, sign up, book, reply). This contract anchors every later cut; an edit that breaks it is a rewrite, not an edit. This step is done when all three sentences exist and the action is one verb, not a menu.

2. **Pick the framework and the fitting principle.** Choose one structure from [frameworks.md](references/frameworks.md) — AIDA, PAS, BAB, or the 4 Ps — by the reader's awareness, then pick one or two persuasion principles from [persuasion.md](references/persuasion.md) that suit this action. This step is done when one framework and at most two principles are named, each paired with the one-line reason it fits this reader.

3. **Draft against the beats, honestly.** Write the copy section by section along the chosen framework's beats and the headline patterns in the reference, leading with the reader's problem or desired outcome rather than the product, and expressing each chosen principle on a claim that is literally true. This step is done when every beat has copy, the opening names a reader problem or outcome, and each applied principle has a concrete on-page element.

4. **Cut to the rule of one.** Reduce the draft to one reader, one core idea, and one action, then run the clarity and concision passes from [editing-passes.md](references/editing-passes.md): one idea per sentence, filler and hedges and throat-clearing gone, passive turned active where the actor is known. This step is done when removing any remaining sentence would weaken the single argument and no filler word from the cut list survives.

5. **Convert features to benefits, then prove and verify.** Rewrite each feature as the outcome the reader gets, attach a specific proof to every claim — a number, a named result, a testimonial, a guarantee — and confirm each number, deadline, and testimonial against a real source. This step is done when no claim stands without evidence, no vague intensifier ("best", "powerful", "seamless") survives without a concrete fact, and any claim that fails the truth test is cut.

6. **Run the mechanical lint and fix every finding.** Save the draft to a file, then run `python scripts/copy-lint.py check <draft>` — adding `--platform <p>` for an `x`, `instagram`, or `linkedin` post and `--cta` once this copy must carry a call-to-action. The script flags hype and weasel words, sentences past 30 words, likely passive voice, a missing call-to-action verb, and any over-limit length, each located by line and column. A nonzero exit lists findings the agent rewrites by judgment; clean copy exits zero with one line. This step is done when `scripts/copy-lint.py check` exits zero on the draft.

7. **Sharpen the CTA and clear the ethics gate.** Rewrite the call-to-action as a specific, first-person, friction-named ask, test the whole draft against the forbidden dark patterns and the three ethics tests (transparency, truth, interest) in [persuasion.md](references/persuasion.md), and run the red-flags checklist in [frameworks.md](references/frameworks.md). This step is done when the CTA states exactly what happens next, every dark pattern is marked absent, the three tests pass, and zero red flags remain.

8. **Read aloud against voice and the contract.** Read the final copy aloud once for the founder's voice and rhythm, flatten any line that sounds like a corporate brochure, then set the result beside the step-1 contract. This step is done when every sentence sounds like the founder speaking, no jargon filler remains, and the claim, reader, and action survive unchanged.

## Scripts

The agent writes the copy and judges the message; the script enforces the mechanical rules a prose checklist cannot enforce reliably.

- `scripts/copy-lint.py check <draft>` — flag hype and weasel words, sentences past 30 words, likely passive voice, a missing call-to-action verb (under `--cta`), and an over-limit length (under `--platform {x,instagram,linkedin}`). Reads stdin when no file is given. Exits zero on clean copy, exits nonzero with located findings otherwise, and exits 2 on a missing file.
- `scripts/copy-lint.py --selftest` — assert the rules against fixtures; prints `copy-lint selftest: ok` and exits zero.

See also: [persuasion.md](references/persuasion.md) for the ethics line and the dark patterns this skill refuses to emit.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
