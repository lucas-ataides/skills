#!/usr/bin/env bash
# Deterministic conventional-commit helper. Validates type + subject, then commits.
# Shell, not Python: the job is string validation + one git call.
#   git-commit.sh feat auth "add token refresh"   -> feat(auth): add token refresh
#   git-commit.sh fix "" "correct off-by-one"      -> fix: correct off-by-one
#   git-commit.sh --selftest                       -> run the validation checks
set -euo pipefail

TYPES="feat fix refactor docs test chore perf ci build style"

build_header() { # type scope subject -> echoes header; returns 2 on invalid
  local type="$1" scope="$2" subject="$3"
  # A control character (newline, tab, CR) would smuggle extra lines into the message
  # or corrupt the header — reject before any other check.
  case "$type$scope$subject" in *[[:cntrl:]]*)
    echo "control characters are not allowed in type/scope/subject" >&2; return 2;;
  esac
  echo "$TYPES" | grep -qwF -- "$type" || { echo "invalid type: $type (allowed: $TYPES)" >&2; return 2; }
  case "$scope" in *[!a-z0-9._-]*) echo "invalid scope: $scope (allowed: a-z 0-9 . _ -)" >&2; return 2;; esac
  [ -n "$subject" ] || { echo "empty subject" >&2; return 2; }
  case "$subject" in *.) echo "subject must not end with a period" >&2; return 2;; esac
  [ "${#subject}" -le 72 ] || { echo "subject exceeds 72 chars (${#subject})" >&2; return 2; }
  if [ -n "$scope" ]; then echo "$type($scope): $subject"; else echo "$type: $subject"; fi
}

selftest() {
  build_header bogus "" "x"      2>/dev/null && { echo "FAIL: bad type accepted"; exit 1; } || true
  build_header feat "" ""        2>/dev/null && { echo "FAIL: empty subject accepted"; exit 1; } || true
  build_header feat "" "ends."   2>/dev/null && { echo "FAIL: trailing period accepted"; exit 1; } || true
  [ "$(build_header feat auth 'add token')" = "feat(auth): add token" ] || { echo "FAIL: scoped header"; exit 1; }
  [ "$(build_header fix '' 'patch it')" = "fix: patch it" ] || { echo "FAIL: scopeless header"; exit 1; }
  # Regex-y bogus types must be rejected as fixed strings, not matched as patterns.
  for bogus in "doc." "f..t" ".*"; do
    build_header "$bogus" "" "x" 2>/dev/null && { echo "FAIL: regex-y type accepted: $bogus"; exit 1; } || true
  done
  # Every real type must still validate.
  for t in $TYPES; do
    [ "$(build_header "$t" '' 'ok')" = "$t: ok" ] || { echo "FAIL: real type rejected: $t"; exit 1; }
  done
  # Control characters and header-corrupting scopes must be rejected.
  build_header feat "" "$(printf 'a\nEvil: header')" 2>/dev/null && { echo "FAIL: newline subject accepted"; exit 1; } || true
  build_header feat "$(printf 'a\tb')" "x" 2>/dev/null && { echo "FAIL: tab scope accepted"; exit 1; } || true
  build_header feat "a)b" "x" 2>/dev/null && { echo "FAIL: paren scope accepted"; exit 1; } || true
  echo "git-commit selftest: ok"
}

main() {
  if [ "${1:-}" = "--selftest" ]; then selftest; exit 0; fi
  if [ "$#" -ne 3 ]; then
    echo "usage: git-commit.sh <type> <scope> <subject>   (scope may be \"\")" >&2
    echo "       git-commit.sh --selftest" >&2
    echo "types: $TYPES" >&2
    exit 2
  fi
  local header
  header="$(build_header "$1" "$2" "$3")"
  git commit -m "$header"
  echo "committed: $header"
}

main "$@"
