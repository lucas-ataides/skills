# Context files: AGENTS.md and TODO.md

Two files decide whether an agent (or a new teammate) is productive in a project within
minutes or flails for an hour: the agent-instructions file and the task list. They are
load-bearing infrastructure for the development process, not documentation afterthoughts.

## AGENTS.md (or CLAUDE.md)

`AGENTS.md` is the emerging cross-tool standard for "how to work in this repo"; `CLAUDE.md`
is the Claude-specific equivalent (Claude Code reads it). Prefer `AGENTS.md` for
portability; if a `CLAUDE.md` already exists, keep maintaining it rather than splitting
the source of truth. A `CLAUDE.md` that just says "see AGENTS.md" is a fine bridge.

### What a strong one contains

- **Project** — one paragraph: what it is and the current goal.
- **Setup / build / test / run / lint** — the exact commands, copy-pasteable. This is the
  highest-value section; a newcomer must build and test from it alone.
- **Conventions** — the rules a change must follow (style, naming, structure, immutability).
- **Architecture** — only the load-bearing facts: entry points, modules, data flow, the
  boundaries that must not be crossed. Not an essay.
- **Quality gates** — the checks that must pass before commit (lint, types, tests, SCA).
- **Gotchas** — the non-obvious traps that cost an hour to rediscover.
- **Tasks** — a pointer to TODO.md.

### Write it the way a skill is written — anchored, not ambiguous

An AGENTS.md is an instruction set an agent executes, so the same ambiguity that degrades a
skill degrades it. Apply the determinism rules:

- **Anchored references** — name the thing, not "it" / "this".
- **Bounded scope** — no "for every file, do X" that explodes on a large repo; name the set.
- **Shallow branching** — one condition per instruction; split compound rules.
- **Concrete commands** — `pnpm test`, not "run the tests".
- **No vague imperatives** — "the build is green" beats "make sure it works".

### Failure modes

- **Stale instructions** — an AGENTS.md that lies (a renamed command, a dead convention) is
  worse than none: it sends the agent down a wrong path with confidence. Update it in the
  same change as the code.
- **Kitchen-sink** — a 600-line AGENTS.md nobody reads. Keep it to the load-bearing few.
- **Ambiguity** — "follow best practices" instructs nothing. State the actual rule.

Red flags: a command in the README that is absent from AGENTS.md; an AGENTS.md last touched
months before the last refactor; instructions that hedge instead of stating.

## TODO.md

The single source of truth for what is in flight — so a resumed session (or a teammate)
knows the state without asking.

- **One item per line, each a checkable outcome** ("auth refresh endpoint returns 200 with a
  rotated token"), not a vague theme ("work on auth").
- **Now / Next / Done** — exactly one item under Now; the queue in priority order under Next;
  finished items kept under Done (history, not deleted).
- **Current** — a started task moves to Now, a finished one to Done, in the same change. A
  TODO that drifts from reality is noise.

Failure modes: a TODO that lists everything and prioritizes nothing; items with no checkable
done-state; a list nobody updates so it rots into fiction.

## Worked example

A fresh Node service. `project-context.sh init` creates `AGENTS.md` + `TODO.md`. The author
fills AGENTS.md:

```md
## Setup / build / test / run
```sh
pnpm install
pnpm build
pnpm test
pnpm dev
pnpm lint
```
## Quality gates
- `pnpm lint` | `pnpm typecheck` | `pnpm test` — green before every commit.
## Gotchas
- The dev server needs DATABASE_URL; copy .env.example to .env first.
```

TODO.md:

```md
## Now
- [ ] POST /sessions issues a JWT and a refresh token (test: returns 201 + both tokens)
## Next
- [ ] refresh rotation; [ ] rate-limit on /sessions
## Done
- [x] health endpoint returns 200
```

Any agent opening this repo now builds, tests, and knows the next move — without a single
question. That is the whole point.
