# Orchestration

Subagent-driven development splits one large task into independent units and runs them through parallel worker agents. The orchestrator owns decomposition, dispatch, verification, and merge. The leverage is parallelism and context isolation; the danger is concurrent writes to shared state. The governing invariant: **no two agents write the same file.**

This reference inherits the [foundation](../../../meta/foundation/SKILL.md) doctrine — predictability over cleverness — and the verification depth bar from [code-review](../../code-review/SKILL.md). Worker agents are non-user-facing, so each dispatch carries the [cavecrew](../../../meta/cavecrew/SKILL.md) protocol.

## When subagents help, and when they hurt

Parallel subagents earn their coordination cost on a specific shape of work. The wrong shape pays the cost and loses determinism on top.

Subagents help when:

- **Work is independent.** Units touch disjoint files and need no result from a sibling mid-flight.
- **Breadth dominates depth.** Many similar units (per-module migration, per-endpoint test, per-package upgrade) run faster fanned out than in series.
- **Context isolation pays.** A unit needs a large, self-contained slice of context that would crowd the orchestrator's window; a worker holds that slice and returns only the result.
- **The seams are known.** Decomposition boundaries align with existing module or file boundaries, so ownership is clean.

Subagents hurt when:

- **Work is tightly coupled.** Units share a data structure, an interface under active design, or a sequential dependency where unit B reads unit A's output. Coordination overhead exceeds any parallel gain, and shared-file writes invite corruption.
- **The task is tiny.** Dispatch, brief-writing, and verification cost more than doing the work inline. One small edit is faster done directly.
- **The boundary is fuzzy.** No clean file split exists, so any decomposition forces two agents to touch the same file. Stop and refactor the seam first, or keep the work serial.
- **The result needs whole-task context to judge.** A change whose correctness depends on the full system state cannot be verified unit-by-unit; one agent holding the whole picture is safer.

Red flag: reaching for subagents to "go faster" on coupled work. Speed comes from independence, not from agent count.

## Decomposition into independent units

The decomposition step converts a task into a set of units, each ownable by one agent.

1. List the concrete deliverables the task requires.
2. Group deliverables by the files each touches.
3. Cut the groups so no two groups share a writable file. A file is the unit of ownership — the cut runs between files, never through one.
4. Name each unit's exact file set, scope, and output contract.
5. Mark cross-unit dependencies. A dependency edge means those units are sequential, not parallel — schedule the producer before the consumer, or merge them into one unit.

A unit is well-formed when one agent can complete it from its brief alone, write only its owned files, and return a result another agent can verify. A unit that needs a sibling's in-progress state is not independent — fold it into that sibling.

## The FILE-OWNERSHIP rule

**No two agents write the same file — the determinism-critical guard.**

Two agents writing one file concurrently race: last-writer-wins silently discards the other's work, or interleaved writes corrupt the file. The outcome depends on timing, which makes the run non-reproducible — the exact failure the foundation doctrine exists to prevent.

The rule, stated as mechanics:

- Each file has exactly one owner agent for the duration of the dispatch.
- An agent writes only files in its declared ownership set, and reads anything.
- Shared state that several units must update (a manifest, a barrel export, a lockfile, a registry, a routing table) is owned by **no** worker. The orchestrator owns it and applies every change serially after the workers return. A manifest written by three agents at once is the textbook corruption case.
- Generated or moved files count: the agent that creates `dist/x` owns `dist/x`.

Verify the ownership sets are pairwise disjoint before dispatch. Overlap detected after dispatch means corruption already happened — re-run the affected units from a clean tree, do not patch the wreckage.

## The dispatch brief

A worker agent starts with none of the orchestrator's context. The brief is the entire contract. A vague brief is the second-most-common failure mode after ownership overlap.

Each brief carries five parts:

- **Context** — the background the unit needs, self-contained: the goal, the relevant file contents or paths, the conventions to follow, the interfaces to honor. The worker cannot see the conversation that produced the brief.
- **Exact scope** — the precise deliverable, and the explicit non-goals. "Add validation to `parse_config` in `src/config.py`; do not change the call sites" beats "improve config handling."
- **Owned files** — the exact file set this agent writes, named. Everything else is read-only to it. This line is what enforces the ownership rule on the worker side.
- **Output contract** — the shape of the result the orchestrator will consume: which files were changed, what each public symbol's signature is, which command proves it, the structured summary. The contract is what makes the result verifiable.
- **The cavecrew protocol** — the worker is non-user-facing, so its output is data, not prose. Point it at [cavecrew](../../../meta/cavecrew/SKILL.md): return the result not a narrative, one fact per line, paths and symbols verbatim, confidence and blockers stated plainly.

A brief passes when a reader with zero prior context could execute the unit, touch only the owned files, and produce the contracted output.

## Integration and merge

Workers return results; the orchestrator integrates. Because ownership sets are disjoint, the file-level changes do not conflict by construction — the merge work is at the seams, not in the files.

1. Collect each worker's result against its output contract. A result missing a contracted field is incomplete — re-dispatch that unit, do not guess the field.
2. Apply the orchestrator-owned shared-state changes serially: update the manifest, the barrel export, the lockfile once, folding in every unit's contribution in a defined order.
3. Resolve the seams — the integration points the decomposition flagged: a caller now wired to a new signature, a type shared across two units, an import that two units assume.
4. Run the whole-task gate: build, type-check, and the test suite across the merged tree. Unit-level green does not imply integrated green; the seams are exactly what unit verification could not cover.

## Verification before trusting output

Never integrate a worker's result on its say-so. A worker reports success against its own understanding, which may be wrong, partial, or hallucinated. This ties directly to verification-before-completion: trust observed output, not claims.

Per agent, before integrating its result:

- Confirm every contracted file was actually changed, by reading the diff, not the worker's summary.
- Run the command the contract named as proof, and observe it pass firsthand.
- Check the change against the verification depth bar in [the review lenses](../../code-review/references/review-lenses.md): does it deliver the unit's scope in full, fit the architecture, stay inside its owned files. A worker that wrote outside its ownership set is a corruption signal, not a stylistic note.
- Confirm the worker honored the agreed interface, so the seams will integrate.

A result that fails verification is not integrated. The cost of trusting a bad result is a corrupt merge whose origin is hard to trace.

## Re-dispatch on failure

A failed unit is re-dispatched, not hand-patched by the orchestrator. Hand-patching pulls work the worker owned back into the orchestrator's context and erodes the ownership boundary.

The re-dispatch loop:

1. State the failure precisely: which contract field is missing, which proof command failed, which file fell outside the ownership set.
2. Reset that unit's owned files to the pre-dispatch state from version control, so the retry starts clean rather than compounding a half-done attempt.
3. Re-brief the same unit with the failure named and the corrected constraint added.
4. Re-dispatch, then re-verify against the same contract.

Cap the retries. A unit that fails twice signals a decomposition fault — the seam is wrong, the brief is under-specified, or the unit is coupled to a sibling. Stop the loop, re-decompose, and reconsider whether this work should be parallel at all.

## Failure modes

- **Overlapping file ownership → corruption.** Two agents write one file; last-writer-wins or interleaving destroys work. The non-reproducible failure the whole protocol guards against.
- **Races on shared state.** A manifest, lockfile, or registry written by several workers at once corrupts under concurrency. Shared state is orchestrator-owned, updated serially.
- **Vague briefs.** A worker with thin context invents scope, drifts off the deliverable, or honors the wrong interface. The brief is the entire contract; thin brief, wrong output.
- **No verification.** Integrating a worker's claimed success unchecked merges partial or hallucinated work. Trust observed output only.
- **Lost context.** The orchestrator dispatches without the slice the unit needs, and the worker cannot recover it from a conversation it never saw.
- **False parallelism on coupled work.** Splitting sequentially dependent units forces shared-file writes and serializes anyway through the dependency. Coordination cost, no speed gain.

## Red flags

- Two agents list the same file as owned.
- Shared state (manifest, lockfile, barrel export, registry) assigned to a worker rather than the orchestrator.
- A brief that says "improve" or "tidy" with no exact scope and no named file set.
- Dispatching coupled units in parallel to save time.
- Integrating a result without reading its diff or running its proof command.
- Hand-patching a worker's failure inside the orchestrator instead of re-dispatching.
- A unit that fails twice and gets dispatched a third time unchanged.
- Worker output written as narrative prose rather than the cavecrew data contract.

## Worked example: three agents, disjoint ownership

Task: add a `DELETE /widgets/:id` endpoint to a service, covering handler, data layer, and tests, then register the route.

Decomposition by file ownership:

| Agent | Owned files (writes) | Scope | Output contract |
|-------|----------------------|-------|-----------------|
| A — data layer | `src/db/widgets.py` | Add `delete_widget(widget_id) -> bool`; return `False` on a missing id | Signature of `delete_widget`; the unit test command that proves it |
| B — handler | `src/api/widgets_handler.py` | Add `handle_delete(request)` calling `delete_widget`; map missing id to 404, success to 204 | Signature of `handle_delete`; status-code mapping; proof command |
| C — tests | `tests/test_widgets_delete.py` | Cover success, missing id, and a malformed id, asserting status codes against the agreed contract | Test file path; the run command and its observed result |

Shared state — **the route registry `src/api/routes.py` — is owned by no worker.** All three units depend on the new route existing, which is exactly why a worker must not write it. The orchestrator adds the single registry line after A, B, and C return and verify.

Ownership check: `widgets.py`, `widgets_handler.py`, `test_widgets_delete.py` are pairwise disjoint. `routes.py` is orchestrator-only. The sets do not overlap, so dispatch is safe.

Seams flagged for integration: B depends on A's `delete_widget` signature; C depends on B's status-code mapping. The briefs pin both contracts up front, so the workers build against a fixed interface rather than a moving one. A and C can run fully parallel; B consumes A's signature, so the brief states it rather than making B wait.

Dispatch, then per agent: read the diff to confirm only the owned file changed, run the named proof command and watch it pass, check the change delivers its scope against the review lenses. Then the orchestrator writes the one `routes.py` line and runs the whole-task gate — build, types, full suite — across the merged tree. Integrated green, not three unit-greens, is the done condition.

If agent B comes back with the handler also editing `routes.py`, that is an ownership breach: reset `widgets_handler.py` and `routes.py` from version control, re-brief B with "do not touch the route registry; the orchestrator owns it," and re-dispatch.
