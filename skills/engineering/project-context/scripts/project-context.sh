#!/usr/bin/env bash
# project-context.sh — ensure a project has agent-instructions (AGENTS.md/CLAUDE.md)
# and a TODO list, so any agent can pick the project up cold. Deterministic; never
# overwrites an existing file (Poka-yoke); writes atomically (temp + mv).
#   project-context.sh check [dir]    report what exists / is missing
#   project-context.sh init  [dir]    create only what is missing
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
  echo "project-context selftest: ok"
}

main() {
  case "${1:-}" in
    check) shift; cmd_check "${1:-.}" ;;
    init) shift; cmd_init "${1:-.}" ;;
    --selftest) selftest ;;
    *) echo "usage: project-context.sh {check|init} [dir]  |  --selftest" >&2; exit 2 ;;
  esac
}

main "$@"
