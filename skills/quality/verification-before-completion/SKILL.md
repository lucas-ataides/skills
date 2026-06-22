---
name: verification-before-completion
description: Never declare work done without observing that it is done — claimed-done must equal observed-done. Use when about to report a task finished, a bug fixed, a feature working, a file written, tests passing, or a build green; when tempted to write "it should work", "this will fix it", or "done" without running anything; when handing back code, a UI change, or a doc; or when a prior turn asserted success with no command output to back it.
---

A task is done when its real output has been observed to be done — not when the change was made, and not when success seems likely. The defect this skill stops is the unobserved completion claim: "fixed", "working", "passing", asserted from intent rather than evidence. The rule is one line and admits no exception: **claimed-done equals observed-done.**

The rule is [Genchi Genbutsu](../../meta/foundation/SKILL.md) — go and see the real thing — applied to the moment before hand-off. The verification method depends on the output type, the evidence is the command plus its result pasted in, and "it should work" is never evidence. Read [the verification methods](references/verification-methods.md) for the method-by-output-type table, the show-me-the-evidence discipline, the cost-appropriate level, the failure modes, red flags, and a worked assumed-vs-verified contrast.

## Steps

1. **Name the completion claim and its output type.** State the exact thing about to be called done — "the test suite passes", "the link works", "the bug is fixed" — and classify its output type: runnable code, a written file, a bug fix, a UI change, or a doc. A claim with no named output type has no defined check, so naming the type is the first artifact. Done when the claim and its output type are both written down.

2. **Pick the verification method for that type.** Match the output type to its observation in [the methods table](references/verification-methods.md#methods-by-output-type): code runs or its tests run; a file is read back; a fix reproduces the original failure then confirms the repro is gone; a UI renders and is looked at; a doc has its links and facts checked. The method produces an observation, never an inference. Done when the chosen method names a command or an observation that yields real output.

3. **Run it and capture the real output.** Execute the method against the actual artifact and capture what came back — the command's stdout and exit status, the file's read-back contents, the rendered screen. Observation means the artifact's own output, not a mental model of it. Done when real output exists to read, not a prediction of what it would say.

4. **Read the output against the claim.** Compare the captured output to the completion claim: an exit code of 0 and the expected assertions for "tests pass", the awaited content for "file written", the original error absent for "bug fixed". A green-looking run that tested the wrong thing fails this step. Done when the observed output supports the specific claim, or the claim is corrected to match the output.

5. **Scale the verification to the cost of being wrong.** Set the depth by the blast radius named in [the cost-appropriate level](references/verification-methods.md#cost-appropriate-verification): a one-line doc edit warrants a read-back, a payment path warrants running the suite plus the failure cases. Under-verifying a high-blast change and over-verifying a trivial one are both findings. Done when the verification depth matches the cost of the claim being false.

6. **Reject stale or assumed evidence.** Confirm the evidence came from the current artifact, not a prior run before the last edit, and that no step rests on "should work" in place of an observation. Evidence from before the change under test is checked against [the stale-evidence failure mode](references/verification-methods.md#failure-modes). Done when every completion claim traces to fresh output observed after the final change.

7. **Report the claim with its evidence attached.** Hand back each claim beside the command and the result that prove it, per [the evidence discipline](references/verification-methods.md#show-me-the-evidence) — the verdict carries its proof, not the bare word "done". A claim that cannot show its evidence returns to step 2. Done when every completion claim in the hand-off is backed by pasted, fresh, output that an outside reader can check.
