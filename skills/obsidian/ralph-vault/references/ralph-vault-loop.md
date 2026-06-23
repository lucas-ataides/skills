# The ralph-vault loop

The reference behind the loop steps. Ralph-vault names one application of a single
technique: take the autonomous [ralph](../../../engineering/agent-loop/SKILL.md) loop and point it
at the [obsidian-vault](../../obsidian-vault/SKILL.md) compiler, so a vault of unprocessed
sources compiles itself into canonical notes under hard guardrails. One stable prompt drives
every iteration — re-read the vault loop state, ingest one source, canonicalize it, run the
vault validators, write the new state back — with no human between iterations. The loop runs
unattended until a fixed done-condition holds or a guardrail halts it. This page is the
judgment the steps assume: how the loop maps onto the compiler, what each guardrail does, the
state contract, when ralph-vault is the right tool, how it fails, and a worked example.

Ralph-vault inherits the whole base technique from [ralph](../../../engineering/agent-loop/SKILL.md)
and changes only the domain: the backlog is sources and entities rather than code call sites,
the gate is the vault validator rather than a code test suite, and the safety burden grows
because a vault holds private data and the connectors reach external services. The
[obsidian-vault](../../obsidian-vault/SKILL.md) skill owns the actual compilation — ingest,
canonicalize, reconcile, synthesize, validate — and ralph-vault calls it once per iteration.

## How the loop maps onto the vault compiler

The base loop has three fixed pieces — one stable prompt, one persistent backlog file, one
loop that re-reads state. Each maps onto a vault concept:

- **The backlog = the unprocessed sources and entities.** Vault compilation has a natural
  queue: raw sources dropped into the inbox, sources saved to `raw/` but not yet distributed
  into canonical notes, and entities named in processed sources that still lack a page. The
  backlog is that queue, enumerated as a numbered list before the run. A backlog item is one
  source to compile or one named entity to canonicalize — never a vague goal like "improve
  the vault".
- **The done-condition = backlog empty AND the vault hard-gates pass.** Both halves are
  required, exactly as in the base loop. An empty queue with a red validator is not done — a
  vault that ingested every source but left broken links or unresolved contradictions has
  compiled badly. A green validator with sources still queued is not done either. Only the
  conjunction — every source processed *and* the validator green — stops the loop with success.
- **The per-iteration state = the vault's `state.json` plus `INGESTION-LOG.md`.** The base
  loop's `handoff/state.json` becomes a vault-local `state.json` holding the open and processed
  sources and the loop counters, paired with `INGESTION-LOG.md` — the append-only operation log
  (the vault's `log.md` / `Logs/` analog) that records every ingest, every validator result, and
  every connector approval verbatim. The loop reads both first each iteration and writes both
  back each iteration.

A single iteration delegates the whole compile to obsidian-vault: classify the source, extract
entities and claims, save the raw source immutably, rewrite existing pages around the new
knowledge, canonicalize entities against existing notes so no duplicate page is created, and
reconcile any contradiction it surfaces. Ralph-vault adds nothing to that procedure — the loop
contributes only the queue discipline, the stop-condition, and the guardrails around it.

## The done-condition — the stop the loop runs toward

Write the backlog first, as a numbered list, before a single iteration runs. A backlog item is
well-formed when it is:

- **Binary** — the item is processed or not, decided by the validator and the log, not by an
  opinion. "Canonicalize the vault" is not an item; "the source `raw/2026-06-01 — paper.md` is
  distributed into canonical notes and the validator is green" is.
- **Validator-decidable** — the named vault validator, or a scripted check it runs, can rule on
  the item without a human reading the diff. A source whose correct compilation needs a human
  judgment call has no place in an autonomous run.
- **Independent** — items do not overlap, so processing one source cannot silently reopen
  another and the open set shrinks monotonically.
- **Mechanical** — the source is routine enough that compiling it needs execution, not a design
  decision about vault structure. A queue full of structural judgment calls belongs in
  checkpointed ingestion, where a human rules on each.

The vault hard-gates are the second half of the done-condition, and the loop names them
explicitly before running. The gates are the validator's hard failures: the critical-finding
count is zero (no broken links, no unfilled template syntax, no malformed frontmatter), the
unresolved-contradiction count is zero, and no source in the processed set lacks the canonical
notes it should have produced. The loop never relaxes a gate to finish — eroding the validator
to make the vault look green is the silent-gate-skipping failure mode, and it is banned.

Red flags: a backlog written as prose goals rather than per-source items; a source no validator
could rule on; a "done-condition" that is just the iteration cap; sources that need a human to
judge whether they compiled correctly.

## The guardrails — what keeps the loop safe

The checkpointed alternative is kept safe by a human approving each source. Ralph-vault has no
such human, so safety is mechanical. Seven guardrails bound the run, and every one is set
before the first iteration:

- **Bounded iteration cap (N).** A hard ceiling on iterations. The loop halts at N regardless
  of queue state — the last-resort brake against an infinite loop. Size N from the source count
  with headroom for retries, not as an open-ended large number.
- **Cost/time budget.** A ceiling on spend — wall-clock minutes, token and API cost, or both.
  The loop checks accumulated spend at the top of each iteration and halts the moment the budget
  is exhausted. The budget matters more here than in code ralph, because the connectors
  (research commands like deep web research, X scans, transcript extraction) carry per-call API
  cost that compounds across a large queue.
- **No-progress detector (K stalled rounds).** A counter of consecutive iterations that
  processed no source. One stalled round is noise; K in a row is a halt. The detector catches
  the loop stuck ingesting, failing the validator, and retrying the same source forever. Reset
  the counter to zero on any iteration that processes a source; halt when it reaches K.
- **Validators green each iteration.** No iteration reports a source processed behind a red or
  skipped validator. The validator runs every pass and its result is recorded verbatim in
  `INGESTION-LOG.md`. A red validator reverts the source to open; a source never advances behind
  a narrowed or skipped check.
- **No external connector writes without approval.** The loop runs no connector or research
  command that writes remote state — no published export, no third-party API mutation — without
  recorded prior approval. Read-only research that pulls a source into the queue is in scope;
  any connector action that changes state outside the vault is held behind a human sign-off
  logged before the action runs. The connector-verification gate is exactly this sign-off, and
  skipping it is a named failure mode below.
- **No destructive operations.** The loop runs no irreversible command unattended — no
  recursive delete of vault files, no history rewrite, no overwrite of an immutable `raw/`
  source. Destruction routes through a guarded helper or is forbidden outright; canonicalization
  rewrites pages additively and preserves history rather than deleting prior facts.
- **The obsidian-vault hard checkpoints still apply.** Every checkpoint the
  [obsidian-vault](../../obsidian-vault/SKILL.md) compiler enforces for a single ingest holds
  inside the loop unchanged — raw sources stay immutable, bi-temporal facts append rather than
  overwrite, and a private-folder rule is never crossed. The loop adds guardrails on top of
  those checkpoints; it never removes them to move faster.

A loop that trips a guardrail halts and writes its termination reason to `state.json`. A
guardrail halt is the loop working as designed; a loop that runs past its guardrails is the
exact failure this skill exists to prevent.

## Resumability — read state first, write state last

The loop carries no memory across iterations beyond the durable vault state. Every iteration
opens by reading `state.json` and `INGESTION-LOG.md` fresh and closes by writing both back, so
a fresh agent after a crash resumes cold with zero context loss. `state.json` holds, at minimum:

- **`sources_open`** — the remaining sources and entities, top-first, each a binary
  validator-decidable item.
- **`sources_processed`** — the compiled sources, so the loop neither redoes them nor distrusts
  them.
- **`iteration`** — the current count, checked against the cap N.
- **`spend`** — accumulated cost and elapsed time, checked against the budget.
- **`stall_count`** — consecutive iterations that processed nothing, checked against K.
- **`validator`** — the named vault validator command and its last recorded result.
- **`connector_approvals`** — the external actions a human signed off in advance, each tied to
  the iteration that may use it.
- **`termination`** — empty while running; on halt, the reason (done, cap, budget, stall,
  guardrail) and the final counts.

`INGESTION-LOG.md` is the human-readable companion: one append-only entry per iteration naming
the source compiled, the notes created and rewritten, the validator result verbatim, and any
connector approval consumed. The discipline is strict — read both first, write `state.json`
back atomically so a reader never sees a half-written file, and append to `INGESTION-LOG.md`
never rewrite it. A crash mid-iteration loses at most one source's progress.

Red flags: loop counters tracked in context instead of `state.json`; a state file written
non-atomically; reconstructing loop position from chat scrollback after a reset; an
`INGESTION-LOG.md` that records processed sources but omits the validator result or the
connector approvals, blinding the guardrails.

## When ralph-vault fits — and when checkpointed compilation is safer

Ralph-vault and checkpointed ingestion via [obsidian-vault](../../obsidian-vault/SKILL.md)
compile the same vault and differ on one axis: whether a human rules between sources. Choose by
the backlog and the source sensitivity, not by taste.

**Ralph-vault fits** a large, mechanical source backlog:

- The queue is big — a research dump, an exported read-later list, a folder of transcripts, a
  month of saved articles — and stopping for approval per source wastes the autonomy.
- The sources are routine and non-sensitive, so correct compilation needs no human judgment per
  source.
- The validator is strong enough to rule on each source, and a mistake is cheap to catch and
  revert because the blast radius is contained to the vault working tree.

**Checkpointed compilation is safer** for sensitive or judgment-heavy sources:

- The sources carry private or regulated content — personal correspondence, medical or legal
  material, anything where a wrong canonicalization or a privacy leak is expensive.
- A source forces a structural decision the validator cannot make — a new folder taxonomy, a
  contested entity merge, a contradiction whose resolution changes the vault's model of the
  world.
- The batch is small enough that a per-source human review costs little.

The deciding question: *could the vault validator, with no human reading the diff, rule
correctly on every source in this backlog, and is every source safe to ingest unattended?* A
confident yes points to ralph-vault. Any real doubt — especially about privacy — points to
checkpointed compilation. When unsure, default to the checkpoint: the cost of an unnecessary
checkpoint is minutes; the cost of an autonomous loop loose on sensitive sources is a leak or a
corrupted vault nobody caught.

## Failure modes

Six ways the ralph-vault loop fails, each with the guardrail that counters it:

- **Runaway ingestion.** The loop keeps pulling and compiling sources without a fixed target,
  ballooning the vault and the spend. Countermeasure: the done-condition bounds termination, the
  iteration cap N is the hard last-resort brake, and the budget halts on exhausted spend.
- **Duplicate entities.** The loop creates a second page for an entity that already has one,
  because it skipped the search-before-create step, fragmenting the canonical graph.
  Countermeasure: every iteration canonicalizes against existing notes through obsidian-vault,
  and the validator's duplicate check is a hard gate that reverts the source on a collision.
- **Drift.** The stable prompt is edited mid-run, or the loop wanders off the queue into
  unrelated vault edits. Countermeasure: one unchanging prompt and the fixed source queue as the
  only scope; work discovered mid-run is recorded for after the run, never absorbed into the
  current loop.
- **Skipping the connector-verification gate.** The loop fires a research connector that writes
  external state, or pulls a source through a connector, without the recorded approval the gate
  requires. Countermeasure: no external connector write runs without a prior sign-off logged in
  `INGESTION-LOG.md`, and the iteration records its connector approvals or records zero.
- **Privacy leakage.** A private source is compiled into a shared note, or a connector sends
  private vault content to an external service. Countermeasure: the obsidian-vault private-folder
  checkpoint holds inside the loop, and the connector gate blocks any external send that lacks
  approval.
- **Silent gate-skipping.** The validator is skipped, narrowed, or reported green when it is
  not, so a badly compiled source advances to processed. Countermeasure: validators-green is
  required every iteration and the result is recorded verbatim; a red or skipped validator
  reverts the source and is never reported as done.

## Red flags

Signs a ralph-vault loop is unsafe or mis-scoped:

- No iteration cap, no budget, or no stall limit set before the loop runs — a loop with no brakes.
- The done-condition is the iteration cap rather than the conjunction of an empty queue and green
  hard-gates.
- The prompt is rewritten between iterations, so the run is no longer reproducible.
- Loop position lives in the agent's context instead of `state.json` and `INGESTION-LOG.md`.
- A connector that writes external state sits inline in the loop body with no approval logged.
- Sensitive or private sources are queued into an autonomous run instead of a checkpointed one.
- The validator is rerun many times against one source, or narrowed to make the source pass.
- The loop absorbs newly discovered sources into the current run instead of recording them for
  after termination.

## Worked example — two iterations

Task: compile a batch of three saved articles into the vault and leave the validator green. The
backlog and bounds, written first.

Done-condition — backlog (each item validator-decidable), plus the vault hard-gates green:

1. `raw/2026-06-01 — agent-memory.md` is distributed into canonical notes and the validator is green.
2. `raw/2026-06-02 — vector-db-costs.md` is distributed into canonical notes and the validator is green.
3. `raw/2026-06-03 — rag-eval.md` is distributed into canonical notes and the validator is green.
4. No duplicate entity page and no broken link remain in the vault (validator critical count zero).

Guardrails: iteration cap N = 8; budget = 20 minutes; stall limit K = 2; validator = the
obsidian-vault vault-health check run in its hard-gate mode. The state seeds with these items in
`sources_open`, `iteration: 0`, `spend: 0`, `stall_count: 0`, empty `connector_approvals`, and an
empty `termination`. No connector write is approved, so the loop runs read-only against the queue.

### Iteration 1 — a source compiles

**Open by re-reading state.** Read `state.json` and `INGESTION-LOG.md`: three sources open,
iteration 0 of 8, spend under budget, stall count 0, last validator result green. Another
iteration is permitted.

**Process one source.** Take item 1. Delegate to obsidian-vault: classify the article, extract
its entities (a memory framework, two people, one company), save the raw source immutably,
search existing notes, find the company already has a page, rewrite that page with the new claim
rather than creating a second one, and create new pages for the framework and the two people. No
destructive command runs; no connector writes external state.

**Run the validator, write back.** Run the vault-health hard-gate check. No broken link, no
duplicate, no malformed frontmatter — the validator exits green. Move item 1 to
`sources_processed`, reset `stall_count` to 0, set `iteration: 1`, add the spend, and append an
`INGESTION-LOG.md` entry naming the four notes and the green result. Two sources remain open.

### Iteration 2 — a stalled round, detected

**Open by re-reading state.** Read both files: two sources open, iteration 1 of 8, spend under
budget, stall count 0. Another iteration is permitted.

**Process one source.** Take item 2. Delegate the compile of the vector-db-costs article.

**Run the validator, write back.** Run the hard-gate check. The validator fails: the article
introduced a new entity whose page links to a note that does not yet exist, leaving a broken
link — a critical finding. Per the validators-green guardrail, item 2 stays open, `stall_count`
increments to 1, `iteration: 2`, spend added, and the red result is logged verbatim. No source
closed this round.

The next iteration re-reads state, sees `stall_count: 1` (below K = 2), and retries item 2 —
this time creating the missing linked note so no broken link remains. That pass closes item 2
and resets the stall count. Had a second consecutive iteration also closed nothing, `stall_count`
would have reached K = 2 and the no-progress detector would have halted the loop, writing
`termination: { reason: "stall", item: 2 }` for a human to inspect.

The loop continues — re-read, process, validate, write back — until item 3 compiles and the
vault hard-gates pass. At that point the open set is empty and the validator's critical count is
zero: the done-condition holds, the loop writes `termination: { reason: "done" }`, and it stops.
Every iteration was bounded by the cap, the budget, and the stall detector; no destructive
command and no unapproved connector write ran; the obsidian-vault checkpoints held throughout;
and `state.json` with `INGESTION-LOG.md` alone could have resumed the run after any crash — which
is the whole point of ralph-vault.
