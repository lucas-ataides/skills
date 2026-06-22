# Authoring guide

How to write a skill that is worth its context. This page condenses the methodology
behind a great skill; the [SKILL.md](../SKILL.md) beside it is the step-by-step
procedure that puts the methodology to work. Read the [foundation
doctrine](../../foundation/SKILL.md) for the rules every skill inherits; read this for
the craft those rules leave open.

A skill is a procedure the agent loads at the moment of need and then *follows*. Two
forces fight over every line: **context load** (every word the description and body
cost, paid on every relevant turn) against **cognitive load** (the ambiguity the agent
must resolve when the skill is too thin to be followed). Great authoring spends the
fewest words that still leave nothing to guess.

## The invocation choice

A skill fires one of two ways, and the choice is the first decision, made before the
body exists.

**Model-invoked** — the agent reads the description and decides to fire the skill on
its own. No leading `disable-model-invocation` key; the description carries triggers.
The cost is permanent: every model-invoked description loads into context on every
turn the agent weighs its tools. Reserve model invocation for a procedure the agent
should reach for without being told.

**User-invoked** — the human types `/skill-name`; the agent never fires it unprompted.
Set `disable-model-invocation: true`. The cost is zero until invoked, so the bar is
lower. Reserve user invocation for a procedure with a human in the loop, or one too
specialized to earn standing context.

The trade-off is context load against discoverability. A model-invoked skill is
discoverable but always loaded; a user-invoked skill is free but only the human can
summon it. When the agent must act unprompted, pay the context. Otherwise, keep it
user-invoked and spend nothing.

## Writing a model-invoked description

The description is the only part of a model-invoked skill the agent reads *before*
deciding to load the body, so the description alone must earn the load. Four rules:

1. **Front-load the leading word.** Open with the verb of the job — "Review…",
   "Scaffold…", "Author…". The first token does the heaviest matching, so the strongest
   signal goes first.
2. **State what it does, then when to use it.** One clause of capability, then rich
   "Use when …" triggers naming the situations that should fire it.
3. **One trigger per branch.** Name each distinct situation as its own trigger rather
   than welding two with a conjunction. Separate triggers match separately; a welded
   pair matches neither half cleanly.
4. **Cut what the body already says.** The description is a router, not a summary. Drop
   any sentence the agent does not need until *after* it has loaded the body.

Budget: under 500 characters (`skill-lint` SK006). Every word is permanent load, so the
description is the most expensive prose in the repository per byte.

## The information hierarchy

A skill holds three tiers of content, ranked by how often the agent needs them. Place
each fact at the tier that matches its read frequency.

- **In-skill steps** — the load-bearing procedure, read on every run. Numbered, each
  ending on a checkable completion criterion. The shortest path that still leaves
  nothing to guess.
- **In-skill reference** — short, stable facts the steps lean on, kept inline because a
  pointer would cost more than the fact: a flag list, a severity table, a naming rule.
- **External reference** — depth most runs skip: the rationale, the worked examples, the
  edge cases. Lives in `references/*.md`, reached by a pointer (this file is one).

The test for the boundary: would most runs read this? A yes keeps it in the steps; a no
pushes it behind a pointer.

## Progressive disclosure

Progressive disclosure is pushing depth behind a pointer so the top stays legible. The
SKILL.md top is the most-read surface in the skill, so it carries only the procedure;
the methodology, the rationale, and the examples sit one hop away in `references/`,
loaded only when the agent follows the link.

The discipline mirrors the exemplar: [`code-review/SKILL.md`](../../../engineering/code-review/SKILL.md)
is six tight steps, and the weighted lenses, red flags, and severities live in
[`references/review-lenses.md`](../../../engineering/code-review/references/review-lenses.md).
The procedure stays scannable; the depth is there when needed. `skill-lint` SK070
enforces the floor: a SKILL.md over 500 lines is sprawl, and the fix is disclosure, not
deletion.

## Completion criteria

A step ends when the agent can *observe* that it is done. A checkable criterion names a
condition the agent verifies against real output (Genchi Genbutsu) — a file that exists,
a command that exits zero, a linter that prints no findings. A vague criterion ("make
sure it works", "handle errors as needed") names nothing the agent can check, so the
step has no edge and the agent guesses where it ends. `skill-lint` SK060 bans the vague
imperatives; the discipline is to replace each with an observable.

Exhaustive matters as much as checkable. "Confirm the gate passes" is checkable but
partial when three gates exist; "confirm `skill-lint --strict` prints 0 findings" is
both checkable and complete. A criterion that covers only part of the work hides the
rest, which surfaces as premature completion.

## Leading words

A leading word is a compact, pretrained concept the agent already thinks with, so one
token anchors a whole region of behavior. "Idempotent" recruits everything the model
knows about repeatable operations; "gate" recruits pass-or-fail enforcement. The
repository's leading words live in the [glossary](../../foundation/GLOSSARY.md), and a
skill reuses them rather than minting a synonym.

How to pick one:

- **Prefer a word the model was trained on** over a coined term. A pretrained concept
  arrives with its definition attached; a neologism must be defined before it pays off.
- **Match the word to the exact behavior**, not a near neighbor. "Validate" and "verify"
  diverge, so the looser fit drags in the wrong region.
- **Reuse the repository's vocabulary** so the distributed definition compounds. Every
  reuse of "gate" or "leading word" sharpens what the next reader infers.

## Pruning

Pruning keeps a skill at its shortest correct length. Two principles drive it.

**Single source of truth** — each meaning lives in exactly one authoritative place, and
every other mention points there. The lint patterns live in `rules.yaml`; the docs
point to it rather than restating them, because a restatement drifts the moment the
source changes. When two passages state the same fact, one of them is wrong soon.

**The no-op test** — read each line and ask what breaks if it is deleted. A line whose
removal changes nothing the agent does is muda (waste): cut it. The test catches
ceremony, hedges, and restatements that survive only because no one challenged them.

Pruning is not a one-time pass. A skill accretes sediment over edits — a clause added to
cover a case, a sentence kept "just in case" — and each revision re-runs the no-op test
on what it touches (Kaizen).

## Failure modes

Five ways a skill rots. Name the one you are committing before you ship.

- **Premature completion** — the procedure stops before the work is done, because a
  step's completion criterion was checkable but not exhaustive. The agent reports
  success on a partial result. The fix: make every criterion cover the whole step.
- **Duplication** — a fact stated in two places, which drift until they contradict. The
  fix: one source of truth, with pointers from everywhere else.
- **Sediment** — clauses and caveats accreted over edits that no longer earn their
  context. The fix: the no-op test on every revision.
- **Sprawl** — depth that belongs behind a pointer left inline, so the top stops being
  scannable (`skill-lint` SK070). The fix: progressive disclosure into `references/`.
- **No-op** — a step, line, or whole skill that changes nothing the agent does. The fix:
  delete it, and question whether the skill should exist at all.

## Worked example: a vague process becomes a conformant skill

Start with a process a teammate might describe in passing:

> "When you add a dependency, check it's not already there, scan it for vulnerabilities,
> make sure the lockfile is updated, and clean up anything left over."

Four sentences, and not one is a skill. The diagnosis, defect by defect:

- "check it's not already there" — no named set, no checkable result.
- "scan it for vulnerabilities" — no tool named, so the agent improvises the scan.
- "make sure the lockfile is updated" — SK060 vague imperative, no observable.
- "clean up anything left over" — SK041 vague-destructive, dangerously broad reading.

Now the conformant rewrite. Invocation: model-invoked, because the agent should reach
for it whenever it touches dependencies. Description (under 500 chars):

> `Add a dependency safely — dedupe, scan, lock, verify. Use when the user adds, bumps,
> or replaces a package, or edits the dependency manifest.`

The body, as checkable steps:

1. **Dedupe.** Run the package manager's list command and grep the named package. A hit
   means the dependency exists; stop and report it. Completion: the package is absent
   from the listing.
2. **Add and lock.** Run the manager's add command for the named package. Completion:
   the lockfile diff shows the new package pinned to a resolved version.
3. **Scan.** Run the SCA gate (`skill-gate --strict`, or the project's audit command).
   Completion: the scan exits zero with no advisory at or above the project threshold.
4. **Verify the tree.** Run the manager's install in frozen-lockfile mode. Completion:
   the install exits zero and reports no drift between manifest and lockfile.

What changed: every vague verb became a command with an observable result; "clean up"
was deleted as a no-op (the frozen install already proves the tree is consistent);
the unbounded "anything left over" never reached the page. The depth — why frozen mode,
how to read an advisory threshold — would go in a `references/` file, not the steps.
