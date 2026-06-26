#!/usr/bin/env bash
# project-context.sh — ensure a project has agent-instructions (AGENTS.md/CLAUDE.md)
# and a TODO list, so any agent can pick the project up cold. Deterministic; never
# overwrites an existing file (Poka-yoke); writes atomically (temp + mv).
#   project-context.sh check     [dir]   report what exists / is missing
#   project-context.sh init      [dir]   create missing AGENTS.md + TODO.md
#   project-context.sh bootstrap [dir]   init + seed brain/ — the full ataides-skills setup
#   project-context.sh --selftest
set -euo pipefail

agents_template() {
  cat <<'TMPL'
# AGENTS.md

> Instructions for any AI agent or developer working in this project. Keep it
> current: when a command, convention, or gotcha changes, update this file in the
> same change. Vague instructions are worse than none — be concrete and anchored.

## Project
<one paragraph: what this project is and its current goal>

## Setup / build / test / run
```sh
# install:
# build:
# test:
# run:
# lint:
```

## Conventions
- <language and style, naming, structure — the rules a newcomer must follow>

## Architecture
- <the few load-bearing facts: entry points, modules, data flow, key boundaries>

## Quality gates (run before every commit)
- <lint> | <types> | <tests> | <security/SCA> — a change is done only when these pass.

## Gotchas
- <non-obvious traps, footguns, environment quirks>

## Agent skills (ataides-skills)
Work this repo with the **ataides-skills** toolkit — invoke the matching skill before acting
(your own explicit instructions still win):

- build or change code/infra, test-first → `ataides-skills:engineering`
- commits, branches, PRs → `ataides-skills:git-guardrails`
- review a diff → `ataides-skills:code-review`
- write tests → `ataides-skills:tdd`
- architecture or design decisions → `ataides-skills:software-architecture`
- keep this file, TODO, and the brain current → `ataides-skills:project-context`

The determinism doctrine every skill inherits is `ataides-skills:foundation`.

## Project brain
Deep memory lives in [brain/](brain/index.md). Read `brain/index.md` first, then the pages a
task touches. On a decision: update the page, refresh its index line, and append `brain/log.md`.
Synthesis only — never restate the code.

## Tasks
See [TODO.md](TODO.md) for the current task list.
TMPL
}

todo_template() {
  cat <<'TMPL'
# TODO

The single source of truth for what is in flight. One item per line, each phrased
as a checkable outcome. Move finished items to Done; keep the history.

## Now
- [ ] <the one thing in progress>

## Next
- [ ] <queued, in priority order>

## Done
TMPL
}

brain_index_template() {
  cat <<'TMPL'
# Project brain

An LLM wiki for this repo (Karpathy pattern). The agent owns it: read this index first, then
the pages a task touches. On a change, update the page, refresh its line here, and append
`log.md`. Synthesis only — never restate the code; flag contradictions with their source.

## Architecture
## Decisions
## Systems
TMPL
}

brain_log_template() {
  cat <<'TMPL'
# Log

Append-only and parseable — one line per event:
`## [YYYY-MM-DD] <kind> | <summary>`  — kind is decision | ingest | change | risk.
TMPL
}

has_agent_instructions() { [ -f "$1/AGENTS.md" ] || [ -f "$1/CLAUDE.md" ]; }

status() { [ -f "$1" ] && echo present || echo MISSING; }

cmd_check() {
  local dir="${1:-.}"
  printf 'AGENTS.md : %s\n' "$(status "$dir/AGENTS.md")"
  printf 'CLAUDE.md : %s\n' "$(status "$dir/CLAUDE.md")"
  printf 'TODO.md   : %s\n' "$(status "$dir/TODO.md")"
}

write_new() { # path template-fn — create only if absent, atomically
  local path="$1" fn="$2" tmp
  if [ -e "$path" ]; then echo "kept existing $path"; return 0; fi
  tmp="$(mktemp "$(dirname "$path")/.pctx.XXXXXX")"
  "$fn" >"$tmp"
  mv "$tmp" "$path"
  echo "created $path"
}

cmd_init() {
  local dir="${1:-.}"
  [ -d "$dir" ] || { echo "no such directory: $dir" >&2; return 2; }
  if has_agent_instructions "$dir"; then
    echo "kept existing agent-instructions"
  else
    write_new "$dir/AGENTS.md" agents_template
  fi
  write_new "$dir/TODO.md" todo_template
}

# bootstrap: the full ataides-skills setup — AGENTS.md (with the skills directive and the
# brain pointer), TODO.md, and a seeded brain/. Never overwrites; safe to re-run.
cmd_bootstrap() {
  local dir="${1:-.}"
  [ -d "$dir" ] || { echo "no such directory: $dir" >&2; return 2; }
  cmd_init "$dir"
  mkdir -p "$dir/brain"
  write_new "$dir/brain/index.md" brain_index_template
  write_new "$dir/brain/log.md" brain_log_template
}

selftest() {
  local t c
  t="$(mktemp -d)"
  cmd_init "$t" >/dev/null
  [ -f "$t/AGENTS.md" ] || { echo "FAIL: AGENTS.md not created"; exit 1; }
  [ -f "$t/TODO.md" ] || { echo "FAIL: TODO.md not created"; exit 1; }
  printf 'marker\n' >>"$t/AGENTS.md"
  cmd_init "$t" >/dev/null
  grep -q marker "$t/AGENTS.md" || { echo "FAIL: overwrote existing AGENTS.md"; exit 1; }
  c="$(mktemp -d)"
  : >"$c/CLAUDE.md"
  cmd_init "$c" >/dev/null
  [ -f "$c/AGENTS.md" ] && { echo "FAIL: created AGENTS.md despite CLAUDE.md"; exit 1; }
  local b
  b="$(mktemp -d)"
  cmd_bootstrap "$b" >/dev/null
  grep -q 'ataides-skills:engineering' "$b/AGENTS.md" || { echo "FAIL: bootstrap skills directive"; exit 1; }
  grep -q 'Project brain' "$b/AGENTS.md" || { echo "FAIL: bootstrap brain pointer"; exit 1; }
  { [ -f "$b/brain/index.md" ] && [ -f "$b/brain/log.md" ]; } || { echo "FAIL: bootstrap brain seed"; exit 1; }
  cmd_bootstrap "$b" >/dev/null  # idempotent: a second run keeps everything
  echo "project-context selftest: ok"
}

main() {
  case "${1:-}" in
    check) shift; cmd_check "${1:-.}" ;;
    init) shift; cmd_init "${1:-.}" ;;
    bootstrap) shift; cmd_bootstrap "${1:-.}" ;;
    --selftest) selftest ;;
    *) echo "usage: project-context.sh {check|init|bootstrap} [dir]  |  --selftest" >&2; exit 2 ;;
  esac
}

main "$@"
