# Verification methods

Verification is the act of observing that a claim is true before making it. The model's strongest pull near the end of a task is to declare victory from intent — the change was written, so it must work. That pull is the defect. This reference states the core rule, gives the method per output type, defines the evidence discipline, separates real verification from assumption, sets the cost-appropriate level, catalogs the failure modes and red flags, and closes on a worked contrast.

## The core rule: claimed-done equals observed-done

A completion claim is a statement about reality: the tests pass, the file is written, the bug is gone. A claim is verified only when reality has been observed to match it. The two values that must be equal:

- **Claimed-done** — what the hand-off asserts is finished.
- **Observed-done** — what the artifact's own output shows when the claim is checked against it.

When the two are equal, the work is done. When they diverge, the claim is false and the divergence is the finding. Nothing about effort, confidence, or plausibility closes the gap — only observation does. This rule is one half of a single principle shared with [full-output-enforcement](../../full-output-enforcement/SKILL.md): completeness is that principle applied to the shape of the deliverable, and verification is the same principle applied to its behavior. Both forbid the unobserved claim.

The grounding is the foundation doctrine's [Genchi Genbutsu](../../../meta/foundation/SKILL.md) — go to the source and see the real thing. The opposite of Genchi Genbutsu is the report written from the desk: a status assembled from what should have happened. Verification-before-completion is the rule that the report comes from the floor, never the desk.

## Methods by output type

The observation differs by what was produced. The table below pairs each output type with the act that yields its real output. The method always produces an observation, never an inference.

| Output type | Verification method |
| --- | --- |
| Runnable code | Run it, or run the tests that exercise it, and read the actual output and exit status — not the source as a proxy for its behavior. |
| A written file | Read the file back from disk after the write, and confirm the content is the intended content end to end. |
| A bug fix | Reproduce the original failure first to establish the repro, apply the fix, then re-run the repro and confirm the failure is gone. |
| A UI change | Render the UI and look at it — the screen, a screenshot, the rendered component — rather than reasoning about the markup. |
| A doc | Open the rendered doc, follow the links to confirm they resolve, and check the load-bearing facts against the source. |

Three notes on the table:

- **Code: read the output, not the code.** Reading the source confirms intent, never behavior. A function that looks correct still throws on an empty input; only running it surfaces the throw. The deliverable is behavior, so the observation is behavior.
- **A bug fix needs the before, not only the after.** A fix re-run that passes proves nothing on its own; the same run had to fail before the fix, or the test may never have exercised the bug at all. Establish the red, then observe the green. This mirrors the test-driven discipline: a test that has never failed is not known to test anything.
- **A UI is seen, never inferred.** Correct markup renders wrong under real CSS, a real viewport, real data. The observation is the pixels, captured by a render or a screenshot, not the template read as a promise of them.

## Show me the evidence

Evidence is the command paired with its result, pasted in. A verdict travels with the proof that earns it; the bare word "done" is an assertion, not evidence.

- **Paste the command and the result together.** "Tests pass" is a claim. The `pytest` invocation followed by `=== 47 passed in 2.10s ===` is evidence. The reader checks the second; the first alone asks for trust.
- **Show the exit status where it carries the verdict.** A command that exits non-zero failed even when its stdout looks benign. The exit code is part of the result, captured alongside the output.
- **Quote the specific line that proves the claim.** For a long output, the proof is the assertion line, the absent error, or the changed value — pointed to, not buried in a wall of log the reader must search.

The discipline has a test: an outside reader, without the conversation, can read the pasted evidence and reach the same verdict. Evidence that only convinces the author who already believes the claim is not evidence.

## Real verification versus assumption

The line between verification and assumption is the line between an observation and a prediction. Both can be stated in confident prose; only one survives contact with the artifact.

- **The phrase "it should work" is a prediction.** A prediction about output is not the output. A forecast like "this will fix it" names a result that running the code would confirm or refute, and the forecast stands unchecked until the run happens.
- **The phrase "it works — here is the run" is verification.** Such a claim points at observed output. The prediction has been replaced by the result it predicted.
- **Reading the diff is not running the code.** A diff confirms what changed, never that the change behaves. The diff is necessary and not sufficient; the run is the sufficient part.
- **A passing CI badge from before the edit is not verification of the edit.** Evidence has to come from the artifact under test, after the change under test. Borrowed evidence verifies the wrong version.

The tell of an assumption masquerading as verification is the modal verb: "should", "would", "ought to", "presumably". A verified claim is in the indicative, anchored to output that exists.

## Cost-appropriate verification

Verification has a cost, and the right depth is set by the cost of the claim being false — the blast radius. Total verification of a typo fix wastes effort; a glance at a payment path is negligence. Match the depth to the stakes.

- **Low blast radius — a read-back or a single run.** A one-line doc edit, a comment, a local rename: read the result back, or run the one command that exercises it. The cost of being wrong is small and local, so the proportional check is light.
- **Medium blast radius — the relevant suite plus the changed path.** A feature, a non-trivial refactor, a shared utility: run the tests that cover the change and exercise the new path directly. The cost of being wrong reaches other callers, so the check reaches them too.
- **High blast radius — the suite plus the failure cases plus the real environment.** A payment flow, an auth change, a migration, a destructive operation: run the full relevant suite, exercise the failure and edge cases, and observe behavior in a realistic environment. The cost of being wrong is severe or irreversible, so the verification is deep.

Under-verifying a high-blast change is the dangerous error; over-verifying a trivial one is the wasteful error. The proportional response sits between them, indexed to what breaks when the claim is false.

## Failure modes

- **Assuming success.** The change was made, so it is reported working — no run happened. The cause is the intent-result conflation, and the cure is step 3: capture real output before any claim.
- **Declaring done on a red gate.** A failing test, a type error, or a lint finding is present, and "done" is declared over it — the red signal ignored or unseen. The cause is not reading the output that was produced, and the cure is step 4: read the result against the claim, treating any non-zero exit as a blocker.
- **Hallucinated completion.** Output is described that was never produced — an invented "47 passed", a summarized run that never ran. The cause is generating the shape of evidence instead of observing it, and the cure is the evidence discipline: paste the real command and the real result, never a plausible-looking facsimile.
- **Verifying the wrong thing.** A real check ran, but against the wrong target — a stale build, a different file, a test that does not exercise the change. The green is genuine and irrelevant. The cause is an unvalidated method, and the cure is step 2: confirm the method observes the actual artifact the claim is about.
- **Stale evidence.** The output is real but predates the last edit — a run from before the final change, cited as proof of the current state. The cause is not re-running after the last edit, and the cure is step 6: confirm the evidence postdates the final change.

## Red flags

- A completion claim — "fixed", "working", "passing", "done" — appears with no command output beside it.
- The prose says "should work", "this will fix it", "presumably passes", or any modal forecast standing in for a result.
- A diff is shown as proof that code behaves, with no run.
- A test result is summarized ("all green") rather than pasted, or the count looks too round to be real.
- A bug is called fixed with no evidence the failure was ever reproduced first.
- A UI change is asserted correct from the markup, with no render or screenshot.
- The cited run predates the most recent edit to the artifact under test.
- A non-zero exit status, a stack trace, or a lint finding sits in the output under a claim of success.

## Worked example: assumed-done versus verified

Task: "Fix the crash in `parse_config` when the file is empty."

### Assumed-done claim (the defect)

> Fixed. I added an empty-file guard to `parse_config` that returns an empty dict, so the crash is gone. The guard should handle the empty-file case correctly.

Four tells in three sentences: the verb is "should handle", a forecast, not an observation; the original crash was never reproduced, so the repro is unestablished; nothing was run, so no output backs "fixed"; and the reader is given a description of the change in place of evidence of its effect. The claim might be true — but it is unverified, and an unverified claim is the defect this skill exists to stop.

### Verified claim (the rule met)

> Reproduced the crash first against the original code:
>
> ```
> $ printf '' > /tmp/empty.toml && python -c "from app.config import parse_config; parse_config('/tmp/empty.toml')"
> Traceback (most recent call last):
>   ...
> TypeError: 'NoneType' object is not iterable
> ```
>
> Applied the empty-file guard, then re-ran the same repro:
>
> ```
> $ python -c "from app.config import parse_config; print(parse_config('/tmp/empty.toml'))"
> {}
> ```
>
> And ran the suite, which now covers the case:
>
> ```
> $ pytest tests/test_config.py -q
> ........                                                          [100%]
> 8 passed in 0.34s
> ```
>
> Fixed: the `TypeError` reproduced before the change, the same input returns `{}` after it, and the 8 config tests pass.

The before-run establishes the repro; the after-run on the identical input shows the crash gone; the suite confirms no regression — and every claim is pasted beside the command and the result that prove it. Claimed-done equals observed-done, and an outside reader can confirm each step without trusting the author.
