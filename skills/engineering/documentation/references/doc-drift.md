# Doc drift

Documentation drifts the moment code moves and the prose stays still. The danger is
asymmetric: a doc that lies is worse than no doc, because a reader trusts it, acts on it,
and fails in a way the absent doc would never have caused. This page names the kinds of
drift, separates what a tool can prove from what only judgment can settle, and says what
to update when code changes.

The determinism rule applies here as everywhere: prove what a tool can prove, then spend
judgment on the rest. `skill-docs` owns the proof; the model owns the prose.

## The kinds of drift

Ordered by how cheaply each can be caught — the first is mechanical, the rest need a
human or a model to read intent.

### 1. Broken links and file references — tool-checkable

A relative link or a referenced path that no longer resolves: a link whose target was
`../setup.md` after `setup.md` moved, an image whose file was renamed, a "see
`src/auth/login.ts`" after the module moved to `src/auth/session.ts`. This is the one
drift a tool settles
with certainty, because resolution is a filesystem fact, not a reading of meaning.
`skill-docs` walks every Markdown link and reports each repo-relative target that fails
to resolve. A non-zero exit is a hard signal, not advice.

### 2. Stale API signatures — judgment

A documented function, flag, endpoint, or config key whose real shape has changed:
a renamed parameter, a new required argument, a changed return type, a removed option.
The link still resolves and the page still reads cleanly, so a tool sees nothing wrong.
A generator (see below) catches the subset that is generated; the prose around it —
the narrative that explains *why* and *when* — is the model's to reconcile.

### 3. Stale code examples — judgment

A copy-paste snippet that no longer runs: it calls a removed method, imports a moved
module, or passes an argument the function dropped. A reader copies it, runs it, and it
breaks. A tool can flag the example *only* if the example is extracted and executed (a
doctest, a tested snippet); free prose examples are invisible to it and must be read.

### 4. Out-of-date README or quickstart — judgment

The first page a newcomer reads, describing an install step, a command, or a default
that has since changed. High blast radius, because a broken quickstart loses the reader
before they reach anything that works. No tool reads "run `npm start`" and knows the
script was renamed to `dev`; a human or the model must.

### 5. A changelog missing the change — judgment

A user-visible change — a new feature, a fix, a breaking change — that shipped without a
CHANGELOG entry. A reader upgrading has no record of what moved. The `git-guardrails`
skill generates the entry from conventional commits deterministically, so the gap is
checkable *given disciplined commit subjects*; a malformed or missing commit subject is
the actual hole, and that is a judgment call.

## Tool-checkable vs. judgment

| Drift                        | Tool                          | Verdict                  |
| ---------------------------- | ----------------------------- | ------------------------ |
| Broken links / file refs     | `skill-docs`                  | certain                  |
| Generated API reference      | doc generator (typedoc, etc.) | certain for the subset   |
| Extracted, executed examples | doctest / snippet runner      | certain for the subset   |
| Prose API signatures         | none                          | judgment                 |
| Free-text code examples      | none                          | judgment                 |
| README / quickstart accuracy | none                          | judgment                 |
| Changelog completeness       | `git-guardrails` + commits     | checkable given subjects |

The rule: never hand-check what a tool proves, and never assume a tool proves what only
a reader can settle. Run `skill-docs` first so the certain drift is gone before judgment
starts; a clean link check narrows the search to the prose a tool cannot see.

## What to update when code changes

When code changes, four doc surfaces can fall behind. Walk the named set, not an open
"all docs" sweep:

- **The README** — when an install step, a top-level command, or a headline capability
  changed. The newcomer's entry point states the current behavior.
- **The public API reference** — when an exported signature, a flag, an endpoint, or a
  config key changed. The generated reference is regenerated; the prose around it is
  rewritten.
- **The affected guides** — the how-to and tutorial pages that walk through the changed
  surface. A renamed command breaks every page that invokes it.
- **The changelog** — when the change is user-visible. The entry records what moved, so
  an upgrader can see it.

A private refactor that changes no exported surface and no user-visible behavior touches
none of these — the doctrine of the smallest change that is correct (Kanso) forbids
churning docs that nothing made stale.

## Doc types and their audiences (Diátaxis)

Drift lands differently per doc type because each type serves a different reader. The
four Diátaxis quadrants:

- **Tutorial** — learning-oriented, for a newcomer. A stale step here is the most costly:
  the reader has no model yet to route around the error, so a broken first command stops
  them cold.
- **How-to** — task-oriented, for a user with a goal. Drift here misleads someone mid-task
  who trusts the recipe; a removed flag in a how-to wastes their time and trust.
- **Reference** — information-oriented, for a user who needs an exact fact. Accuracy is the
  whole value; a wrong signature here is a defect, since reference is consulted precisely
  *because* the reader does not already know.
- **Explanation** — understanding-oriented, for a reader building a mental model. Drift here
  is subtler and ages slowest, because explanation describes the *why*, which changes less
  often than the *how* — but a stale rationale quietly teaches the wrong model.

Match the fix to the quadrant: regenerate reference, rewrite how-to and tutorial steps to
run, and revise explanation only when the underlying reasoning actually changed.

## Failure modes

- **A doc that lies is worse than none.** No doc makes a reader check the code; a wrong
  doc makes them trust it and fail. The expensive failure is confident misinformation,
  so a doc known to be stale is corrected or deleted, never left to mislead.
- **A copy-paste example that no longer runs.** An example is a contract: it claims "paste
  this and it works." A broken snippet breaks that contract at the worst moment — when the
  reader is acting on trust. Examples that matter are extracted and executed so the test
  suite catches their drift, not the user.
- **Regenerated docs nobody reviewed.** A generator fixes signatures, never the prose that
  frames them. Shipping generator output unread leaves correct types wrapped in stale
  narrative — accurate and misleading at once.
- **A green link check read as "docs are correct."** `skill-docs` proves links resolve,
  nothing more. A page can pass every link and still describe behavior that no longer
  exists. The tool clears one drift class; the others stay the reader's job.

## Worked example: a rename that breaks a link and a stale example

A function is renamed and moved: `parseConfig` in `src/config.ts` becomes `loadConfig` in
`src/config/loader.ts`. Two distinct drifts result, each found and fixed differently.

**Drift 1 — the broken file reference (tool-found).** The how-to guide
`docs/configuration.md` carries a "see the parser" link whose target is `../src/config.ts`.
`skill-docs` walks that link, resolves `docs/../src/config.ts`, finds no such file, and
reports the broken target with its line number. The fix retargets the link to
`../src/config/loader.ts`; rerunning `skill-docs` exits zero. The verdict is certain
because resolution is a filesystem fact.

**Drift 2 — the stale code example (judgment-found).** The same guide shows:

```ts
import { parseConfig } from "./config";
const opts = parseConfig(raw);
```

Every link on the page still resolves, so `skill-docs` says nothing — yet the snippet is
dead: the import path moved and the symbol was renamed. A reader who pastes it gets an
import error. Catching this needs a reader, or a snippet runner that executes the example
against the current code. The fix rewrites both lines:

```ts
import { loadConfig } from "./config/loader";
const opts = loadConfig(raw);
```

The two drifts share one cause — the rename — but split cleanly across the determinism
line: the link is a fact a tool settles, the example is a meaning a reader settles. Run
the tool first to clear Drift 1, then read the prose to catch Drift 2. Close the loop by
recording the rename in the changelog as a breaking change via `git-guardrails`, so an
upgrader sees `parseConfig` is gone.
