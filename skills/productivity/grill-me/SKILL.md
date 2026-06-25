---
name: grill-me
description: Extract the knowledge only the user holds through pointed, doc-grounded questions asked one at a time, recorded into a target document until answers saturate. Use when the user wants to be interviewed or grilled, capture or sharpen requirements, fill a spec from a vague feature request, surface hidden assumptions, pin down edge cases and constraints, or turn tacit knowledge into a written artifact.
---

The user holds knowledge the docs and code do not. A grill pulls that knowledge out one question at a time, grounds every question in what already exists so it never re-asks an answered point, and records each answer into a target document until new answers stop changing it.

The leverage is in the gaps. Read the existing material first, locate what it leaves unanswered, and spend every question on a gap — never on what the docs already settle.

## Steps

1. **Read what exists, then name the gaps.** Read the relevant docs, the ticket, and the code the request touches. List the open questions the material leaves unanswered — the missing constraints, the undefined edge cases, the unstated trade-offs. A grill with no gap list interrogates blindly, so the step ends only once the list of gaps is written down.

2. **Name the target document.** Decide where each answer will land: a spec file, a PRD section, a design doc. The record is the deliverable, not the chat transcript. The step ends once the target file path is fixed and open for writing.

3. **Ask one grounded question, then wait.** Pose a single question, grounded in a gap from step 1, citing the doc or code line that motivates it. Wait for the answer before posing the next. A batch lowers the quality of every answer in it; one question at a time keeps each answer sharp. The step ends when one answer is in hand. Draw the question from [the question frameworks](references/question-frameworks.md).

4. **Press a vague answer into a concrete one.** An abstract answer is not yet a specification. Ask for a number, a concrete example, or a contrast case until the answer pins down a decision. The step ends once the answer states something a reader could build against.

5. **Record the answer before the next question.** Write the answer into the target document the moment it lands, in the user's words where they carry meaning. An unrecorded answer is lost work. The step ends once the document reflects the answer and the next gap is selected.

6. **Stop at saturation.** Watch the document change with each answer. Saturation is the point where new answers stop changing it and the remaining gaps are closed. The grill ends once the document answers its own open questions and no gap from step 1 remains unaddressed.

See also: [the question frameworks](references/question-frameworks.md) for the question taxonomy, the tacit-knowledge techniques, the anti-patterns, and a worked example.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
