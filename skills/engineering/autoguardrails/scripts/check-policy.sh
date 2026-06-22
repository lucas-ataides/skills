#!/usr/bin/env bash
# Deterministic policy scanner. Reads DENY <regex> -- <message> rules from one or
# more policy files, scans the repo's git-tracked files, and fails on any match.
# No LLM in this path: the same regex yields the same verdict on every run.
#   check-policy.sh                 -> scan git-tracked files against the policy
#   check-policy.sh POLICY.md a.md  -> scan against an explicit policy file list
#   check-policy.sh --selftest      -> self-check, no real git or repo needed
#
# Shell, not Python: the job is line parsing plus a grep loop. Bash is required
# for `set -o pipefail`; the rest stays POSIX-clean. No destructive operation
# runs here — the scanner only reads.
set -euo pipefail

SEP=' -- '

# Resolve the directory holding this script, so the default global policy is
# found regardless of the caller's working directory.
script_dir() {
  # shellcheck disable=SC1007  # `CDPATH= cd` deliberately neutralizes CDPATH for this one command.
  CDPATH= cd -- "$(dirname -- "$0")" && pwd -P
}

# Default policy file list: the global POLICY.md beside this skill, plus a
# repo-local ./POLICY.md when one exists at the current working directory.
default_policies() {
  local global_policy="$1"
  [ -f "$global_policy" ] && printf '%s\n' "$global_policy"
  [ -f "./POLICY.md" ] && printf '%s\n' "./POLICY.md"
}

# Extract DENY rules from the given policy files as TAB-separated regex<TAB>message.
# Blank lines and comment lines are skipped; a non-DENY line is ignored.
parse_rules() {
  local file line rest regex message
  for file in "$@"; do
    [ -f "$file" ] || { echo "policy file not found: $file" >&2; return 2; }
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        ''|\#*) continue ;;
        DENY\ *) : ;;
        *) continue ;;
      esac
      rest=${line#DENY }
      case "$rest" in
        *"$SEP"*) : ;;
        *) echo "malformed DENY (missing '$SEP'): $line" >&2; return 2 ;;
      esac
      regex=${rest%%"$SEP"*}    # before the first separator
      message=${rest#*"$SEP"}   # after the first separator
      [ -n "$regex" ] || { echo "empty regex in: $line" >&2; return 2; }
      printf '%s\t%s\n' "$regex" "$message"
    done < "$file"
  done
}

# Scan a newline-separated list of files against TAB-separated rules on stdin.
# Prints each hit as path:line: <message>. Returns 1 if any hit, 0 if clean.
scan_files() {
  local files_list="$1"
  local rules regex message hits hit
  rules=$(cat)
  hits=0
  [ -n "$rules" ] || { echo "no DENY rules loaded" >&2; return 2; }
  while IFS="$(printf '\t')" read -r regex message; do
    [ -n "$regex" ] || continue
    # grep -nE over the file list; -I skips binary files, --no-messages hushes
    # unreadable paths. xargs feeds NUL-safe when files come from git ls-files -z.
    while IFS= read -r hit; do
      [ -n "$hit" ] || continue
      printf '%s: %s\n' "$hit" "$message"
      hits=1
    done <<EOF
$(printf '%s\n' "$files_list" | grep -v '^$' | tr '\n' '\0' \
    | xargs -0 grep -nIE --no-messages -- "$regex" 2>/dev/null || true)
EOF
  done <<EOF
$rules
EOF
  [ "$hits" -eq 0 ]
}

# Full run against the real repository: parse policy, list git-tracked files, scan.
run_repo() {
  local global_policy policies files
  global_policy="$(script_dir)/../POLICY.md"
  if [ "$#" -gt 0 ]; then
    policies=$(printf '%s\n' "$@")
  else
    policies=$(default_policies "$global_policy")
  fi
  [ -n "$policies" ] || { echo "no policy file found (looked for $global_policy and ./POLICY.md)" >&2; return 2; }

  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "not inside a git work tree; run at the repo root" >&2; return 2; }
  files=$(git ls-files)
  [ -n "$files" ] || { echo "no git-tracked files to scan"; return 0; }

  local rules
  # shellcheck disable=SC2046
  rules=$(parse_rules $(printf '%s\n' "$policies"))
  printf '%s\n' "$rules" | scan_files "$files"
}

# Self-check with no real git: build a temp policy + temp files in a temp dir,
# assert a known-bad line is caught and a known-good file is clean, then clean up
# only that temp dir via `mktemp`-owned path.
selftest() {
  local tmp policy bad good rules out rc
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/autoguardrails.XXXXXX")
  trap 'test -n "${tmp:-}" && test -d "$tmp" && find "$tmp" -mindepth 0 -maxdepth 3 -delete' EXIT

  policy="$tmp/POLICY.md"
  {
    printf '%s\n' '# selftest policy'
    printf '%s\n' 'DENY AKIA[0-9A-Z]{16} -- AWS key'
    printf '%s\n' 'DENY eval\( -- eval sink'
    printf '%s\n' ''
  } > "$policy"

  bad="$tmp/bad.txt"
  # Assemble a fake key from fragments so no literal AWS-key string lives in this
  # file (a real secret scanner would flag it). The DENY regex still matches it.
  fake_key="AK""IA""1234567890ABCDEF"
  printf 'token = "%s"\n' "$fake_key" > "$bad"
  good="$tmp/good.txt"
  printf '%s\n' 'token = read_secret("aws")' > "$good"

  rules=$(parse_rules "$policy")

  # rule count: exactly two DENY rules parsed.
  [ "$(printf '%s\n' "$rules" | grep -c .)" -eq 2 ] \
    || { echo "FAIL: expected 2 parsed rules"; exit 1; }

  # known-bad must match.
  set +e
  out=$(printf '%s\n' "$rules" | scan_files "$bad"); rc=$?
  set -e
  [ "$rc" -ne 0 ] || { echo "FAIL: known-bad not flagged"; exit 1; }
  case "$out" in *"AWS key"*) : ;; *) echo "FAIL: wrong message for known-bad"; exit 1 ;; esac

  # known-good must be clean.
  set +e
  out=$(printf '%s\n' "$rules" | scan_files "$good"); rc=$?
  set -e
  [ "$rc" -eq 0 ] || { echo "FAIL: known-good flagged ($out)"; exit 1; }

  # malformed rule must be rejected.
  set +e
  printf '%s\n' 'DENY no_separator_here' > "$policy"
  parse_rules "$policy" >/dev/null 2>&1; rc=$?
  set -e
  [ "$rc" -ne 0 ] || { echo "FAIL: malformed DENY accepted"; exit 1; }

  echo "check-policy selftest: ok"
}

usage() {
  echo "usage: check-policy.sh [policy-file ...]   (default: global POLICY.md + ./POLICY.md)" >&2
  echo "       check-policy.sh --selftest" >&2
}

main() {
  case "${1:-}" in
    --selftest) selftest; exit 0 ;;
    -h|--help) usage; exit 0 ;;
  esac
  if run_repo "$@"; then
    echo "check-policy: clean"
    exit 0
  else
    exit 1
  fi
}

main "$@"
