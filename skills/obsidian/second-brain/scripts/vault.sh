#!/usr/bin/env bash
# Deterministic CRUD + correlation helper for an Obsidian second-brain vault.
# Capture life/work/project notes fast, link entities, and find them again — with
# no destructive operation beyond a single guarded, in-vault delete.
#
#   vault.sh init                     -> resolve + create the vault root, print it
#   vault.sh capture <type> <title> [key=value ...]
#                                     -> create a typed note, print its path; each
#                                        trailing key=value lands as a frontmatter field
#   vault.sh append  <note> <text>    -> append a timestamped bullet (atomic)
#   vault.sh link    <from> <to>      -> add a [[wikilink]] under "## Related"
#   vault.sh daily                    -> create-or-open today's daily note
#   vault.sh find    <query>          -> list notes matching tag/title/text
#   vault.sh index                    -> (re)generate index.md, the vault's catalog
#   vault.sh rm      <note>           -> guarded delete of one note inside the vault
#   vault.sh --selftest               -> build a temp vault, exercise all of the above
#
# Vault root resolves from $VAULT, else `skill-config path`, else ./vault. Types: person project meeting
# idea task decision daily client feedback 1on1 company. Shell, not Python: the
# job is slug + file plumbing.
# Bash is required for `set -o pipefail`; the rest stays POSIX-clean. Filenames
# never overwrite — uniqueness comes from a noclobber (`set -C`) reservation loop,
# the shell's O_EXCL, mirroring skillkit.unique_path. Deletion goes through a guard
# that refuses the vault root and anything outside it, mirroring skillkit.safe_remove.
set -euo pipefail

TYPES="person project meeting idea task decision daily client feedback 1on1 company product topic commitment procedure preference source goal journal health relationship account income investment book course concept"

# --- helpers ---------------------------------------------------------------

# Canonical absolute path of an existing directory. `CDPATH= cd` neutralizes a
# user CDPATH for this one command so resolution is deterministic.
abspath_dir() {
  # shellcheck disable=SC1007  # `CDPATH= cd` deliberately empties CDPATH here.
  CDPATH= cd -- "$1" && pwd -P
}

# Resolve the vault root: an explicit $VAULT wins, else the configured path
# (`skill-config path`), else ./vault. Created if absent. So a configured vault
# needs no manual `export VAULT` — the config file is the single source of truth.
vault_root() {
  local root="${VAULT:-}"
  if [ -z "$root" ] && command -v skill-config >/dev/null 2>&1; then
    root="$(skill-config path 2>/dev/null || true)"
  fi
  [ -n "$root" ] || root="./vault"
  mkdir -p "$root"
  abspath_dir "$root"
}

# Deterministic, filesystem-safe slug from a title: lowercase, non-alphanumerics
# to hyphens, runs collapsed, ends trimmed. Empty input yields "untitled".
slugify() {
  local s
  s=$(printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -e 's/[^a-z0-9]\{1,\}/-/g' -e 's/^-\{1,\}//' -e 's/-\{1,\}$//')
  [ -n "$s" ] && printf '%s' "$s" || printf '%s' "untitled"
}

# Map a note type to its canonical vault path under the Life OS domain structure.
# Hand-captured and compiled notes share one structure: work/<folder>, personal/<folder>,
# raw/work/, etc. Event and working types fold into raw/ (immutable provenance);
# daily notes live under personal/journal/. The default domain is "work" unless
# overridden by a `domain=<domain>` capture argument.
type_folder() {
  local type="$1" domain="${2:-work}"
  case "$type" in
    person)
      case "$domain" in personal) echo "personal/relationships" ;; *) echo "work/people" ;; esac ;;
    company)
      case "$domain" in clients) echo "clients/entities" ;; *) echo "work/companies" ;; esac ;;
    client)
      case "$domain" in work) echo "work/companies" ;; *) echo "clients/entities" ;; esac ;;
    project)
      case "$domain" in personal) echo "personal/goals" ;; clients) echo "clients/projects" ;; *) echo "work/projects" ;; esac ;;
    product) echo "work/products" ;;
    topic | idea) echo "work/topics" ;;
    decision) echo "work/decisions" ;;
    task) echo "work/projects" ;;
    commitment) echo "work/projects" ;;
    procedure) echo "work/procedures" ;;
    preference)
      case "$domain" in personal) echo "personal/preferences" ;; *) echo "work/preferences" ;; esac ;;
    source | meeting | 1on1 | feedback) echo "raw/work" ;;
    daily)
      case "$domain" in work) echo "personal/journal" ;; *) echo "personal/journal" ;; esac ;;
    goal) echo "personal/goals" ;;
    journal) echo "personal/journal" ;;
    health) echo "personal/health" ;;
    relationship) echo "personal/relationships" ;;
    account) echo "finance/accounts" ;;
    income) echo "finance/income" ;;
    investment) echo "finance/investments" ;;
    book) echo "learning/books" ;;
    course) echo "learning/courses" ;;
    concept) echo "learning/concepts" ;;
    *) echo "work/topics" ;;
  esac
}

# Reject an unknown note type at the boundary with a clear message.
require_type() {
  echo "$TYPES" | grep -qw -- "$1" \
    || { echo "unknown type: $1 (allowed: $TYPES)" >&2; return 2; }
}

# Render one `key=value` capture argument as a safe YAML frontmatter line, echoed
# without a trailing newline so callers control line joining. The key must be a
# simple identifier ([a-z_]+); anything else is rejected at the boundary. The
# value is emitted bare unless it could break the YAML — a value containing `:`,
# `#`, a leading/trailing space, or a double quote is wrapped in double quotes
# with embedded backslashes and quotes escaped, so the frontmatter stays valid.
render_field() {
  local pair="$1" key value
  case "$pair" in
    *=*) : ;;
    *) echo "invalid field (expected key=value): $pair" >&2; return 2 ;;
  esac
  key=${pair%%=*}
  value=${pair#*=}
  case "$key" in
    *[!a-z_]* | "") echo "invalid field key (allowed [a-z_]+): $key" >&2; return 2 ;;
  esac
  case "$value" in
    *:* | *"#"* | *'"'* | *\\* | " "* | *" ")
      value=${value//\\/\\\\}
      value=${value//\"/\\\"}
      printf '%s: "%s"' "$key" "$value"
      ;;
    *)
      printf '%s: %s' "$key" "$value"
      ;;
  esac
}

# Reserve a brand-new path under a directory, never overwriting. `set -C`
# (noclobber) makes the `>` redirect fail if the candidate exists — the shell's
# O_EXCL — so a uniqueness loop appends -2, -3, ... until a name is won.
# Echoes the reserved (now-empty) path. Mirrors skillkit.unique_path semantics.
reserve_path() {
  local dir="$1" base="$2" ext="$3" n=1 candidate
  mkdir -p "$dir"
  while :; do
    if [ "$n" -eq 1 ]; then
      candidate="$dir/$base$ext"
    else
      candidate="$dir/$base-$n$ext"
    fi
    if (set -C; : > "$candidate") 2>/dev/null; then
      printf '%s' "$candidate"
      return 0
    fi
    n=$((n + 1))
    [ "$n" -le 10000 ] || { echo "could not reserve a unique path in $dir" >&2; return 1; }
  done
}

# Write data to a path atomically: temp file in the same directory, then mv. A
# reader sees the old file or the new, never a half-written one.
atomic_write() {
  local target="$1" data="$2" dir tmp
  dir=$(dirname -- "$target")
  mkdir -p "$dir"
  tmp=$(mktemp "$dir/.vault.XXXXXX")
  printf '%s' "$data" > "$tmp"
  mv -f "$tmp" "$target"
}

# Resolve a note reference to an existing file path inside the vault. Accepts an
# absolute path, a vault-relative path, a bare filename, or a title/slug. Echoes
# the path, or returns 3 when no single match is found.
resolve_note() {
  local root="$1" ref="$2" cand slug hit
  if [ -f "$ref" ]; then printf '%s' "$ref"; return 0; fi
  cand="$root/$ref"
  [ -f "$cand" ] && { printf '%s' "$cand"; return 0; }
  cand="$root/$ref.md"
  [ -f "$cand" ] && { printf '%s' "$cand"; return 0; }
  slug=$(slugify "$ref")
  hit=$(find "$root" -type f -name "$slug.md" 2>/dev/null | head -n 1)
  [ -n "$hit" ] && { printf '%s' "$hit"; return 0; }
  hit=$(find "$root" -type f -name "$slug-*.md" 2>/dev/null | sort | head -n 1)
  [ -n "$hit" ] && { printf '%s' "$hit"; return 0; }
  echo "note not found: $ref" >&2
  return 3
}

# Render the YAML-frontmatter + body template for a note type. Frontmatter is
# uniform across types (so correlation queries stay simple); the type drives the
# tag, the heading set, and the type-specific fields. Any extra arguments are
# `key=value` pairs (already validated by the caller) written as frontmatter
# fields, so a capture can set custom fields (e.g. `sensitivity=private`,
# `owner=lucas`) inline without a follow-up edit. A user field whose key matches
# a type default *replaces* that default (so `project ... owner=lucas` yields a
# single `owner: lucas`, never a duplicate `owner:` key); a new key is appended.
render_template() {
  local type="$1" title="$2" today="$3" defaults pair key
  shift 3
  # Type-specific default fields, one per line, collected so user overrides can
  # drop the matching default before emission.
  case "$type" in
    person)   defaults=$'company:\nrole:' ;;
    project)  defaults=$'status: active\nowner:' ;;
    meeting)  defaults=$(printf 'date: %s\nattendees: []' "$today") ;;
    decision) defaults=$(printf 'date: %s\nstatus: proposed' "$today") ;;
    task)     defaults=$'status: todo\ndue:' ;;
    idea)     defaults='status: seed' ;;
    daily)    defaults=$(printf 'date: %s' "$today") ;;
    client)   defaults=$'status: green\ncompany:' ;;
    feedback) defaults=$(printf 'date: %s' "$today") ;;
    1on1)     defaults=$(printf 'date: %s' "$today") ;;
    company)  defaults='industry:' ;;
    goal)     defaults=$'status: active\nconfidence: medium' ;;
    journal)  defaults=$(printf 'date: %s' "$today") ;;
    health)   defaults='status: active' ;;
    book)     defaults=$'status: reading\nrating: /5\nauthor:' ;;
    course)   defaults=$'status: enrolled' ;;
    concept)  defaults='status: draft' ;;
    account)  defaults=$'status: active\ntype: checking' ;;
    *)        defaults='' ;;
  esac
  # Drop any default line whose key is overridden by a user-supplied field.
  for pair in "$@"; do
    key=${pair%%=*}
    [ -n "$defaults" ] && defaults=$(printf '%s\n' "$defaults" \
      | grep -v -- "^$key:" || true)
  done
  printf '%s\n' '---'
  printf 'title: "%s"\n' "$title"
  printf 'type: %s\n' "$type"
  printf 'created: %s\n' "$today"
  printf 'tags: [%s]\n' "$type"
  [ -n "$defaults" ] && printf '%s\n' "$defaults"
  for pair in "$@"; do
    render_field "$pair"
    printf '\n'
  done
  printf '%s\n\n' '---'
  printf '# %s\n\n' "$title"
  case "$type" in
    meeting)  printf '## Notes\n\n## Decisions\n\n## Action items\n\n' ;;
    decision) printf '## Context\n\n## Decision\n\n## Consequences\n\n' ;;
    daily)    printf '## Log\n\n## Tasks\n\n' ;;
    1on1)     printf '## Notes\n\n## Action items\n\n' ;;
    *)        printf '## Notes\n\n' ;;
  esac
  printf '## Related\n\n'
}

# --- subcommands -----------------------------------------------------------

# capture <type> <title> [key=value ...]: create a typed note with a
# deterministic slug and a collision-free filename. Each trailing key=value is
# written as a frontmatter field (key validated [a-z_]+, value safely quoted).
# Never overwrites; prints the created path. Fields are validated before any path
# is reserved, so a bad field aborts without leaving an empty note behind.
cmd_capture() {
  [ "$#" -ge 2 ] || { echo "usage: vault.sh capture <type> <title> [key=value ...]" >&2; return 2; }
  local type="$1" title="$2" root slug today path pair key domain
  shift 2
  require_type "$type" || return 2
  # Extract domain from key=value args (default: work). A domain= arg sets the domain
  # prefix for the folder path (work/, personal/, finance/, clients/, learning/).
  # It is consumed internally and NOT written as a frontmatter field.
  domain="work"
  local remaining=() field_count=0
  for pair in "$@"; do
    key=${pair%%=*}
    if [ "$key" = "domain" ]; then
      domain=${pair#*=}
      case "$domain" in
        work|personal|finance|clients|learning) : ;;
        *) echo "invalid domain: $domain (allowed: work personal finance clients learning)" >&2; return 2 ;;
      esac
    else
      remaining+=("$pair")
    fi
  done
  # Validate every field up front (fail fast, before reserving a path). Reserved
  # structural keys are off-limits — overriding them would break correlation
  # queries that depend on uniform title/type/created/tags frontmatter.
  for pair in "${remaining[@]}"; do
    render_field "$pair" >/dev/null || return 2
    key=${pair%%=*}
    case "$key" in
      title | type | created | tags)
        echo "reserved field key (set by the template): $key" >&2; return 2 ;;
    esac
  done
  root=$(vault_root)
  slug=$(slugify "$title")
  today=$(date +%Y-%m-%d)
  path=$(reserve_path "$root/$(type_folder "$type" "$domain")" "$slug" ".md")
  atomic_write "$path" "$(render_template "$type" "$title" "$today" "${remaining[@]}")"
  printf '%s\n' "$path"
}

# append <note> <text>: add a timestamped bullet under the note's "## Log"
# section, atomically. The bullet lands at the top of Log (newest first) so
# captured entries never bleed into "## Related"; a missing Log is created after
# the H1 title.
cmd_append() {
  [ "$#" -eq 2 ] || { echo "usage: vault.sh append <note> <text>" >&2; return 2; }
  local root note text stamp body bullet
  root=$(vault_root)
  note=$(resolve_note "$root" "$1")
  text="$2"
  stamp=$(date +%Y-%m-%dT%H:%M)
  bullet="- $stamp $text"
  body=$(cat -- "$note")
  if printf '%s' "$body" | grep -q '^## Log'; then
    atomic_write "$note" "$(printf '%s' "$body" \
      | awk -v b="$bullet" '
          /^## Log/ { print; print b; next }
          { print }
        ')"
  elif printf '%s' "$body" | grep -q '^# '; then
    atomic_write "$note" "$(printf '%s' "$body" \
      | awk -v b="$bullet" '
          !done && /^# / { print; print ""; print "## Log"; print b; done=1; next }
          { print }
        ')"
  else
    atomic_write "$note" "$(printf '%s\n\n## Log\n%s\n' "$body" "$bullet")"
  fi
  printf '%s\n' "$note"
}

# link <from> <to>: add a [[wikilink]] to <to> in <from> under "## Related",
# creating the section when absent. Idempotent: an existing link is not doubled.
cmd_link() {
  [ "$#" -eq 2 ] || { echo "usage: vault.sh link <from> <to>" >&2; return 2; }
  local root from to_path to_slug wikilink body
  root=$(vault_root)
  from=$(resolve_note "$root" "$1")
  if to_path=$(resolve_note "$root" "$2" 2>/dev/null); then
    to_slug=$(basename -- "$to_path" .md)
  else
    to_slug=$(slugify "$2")
  fi
  wikilink="- [[$to_slug]]"
  body=$(cat -- "$from")
  if printf '%s' "$body" | grep -qF -- "[[$to_slug]]"; then
    printf '%s\n' "$from"
    return 0
  fi
  if printf '%s' "$body" | grep -q '^## Related'; then
    atomic_write "$from" "$(printf '%s' "$body" \
      | awk -v link="$wikilink" '
          /^## Related/ { print; print link; next }
          { print }
        ')"
  else
    atomic_write "$from" "$(printf '%s\n\n## Related\n%s\n' "$body" "$wikilink")"
  fi
  printf '%s\n' "$from"
}

# daily: create-or-open today's daily note. Idempotent — an existing note for
# today is returned untouched, so re-running never duplicates or overwrites.
cmd_daily() {
  local root today path
  root=$(vault_root)
  today=$(date +%Y-%m-%d)
  path="$root/Daily/$today.md"
  if [ -f "$path" ]; then
    printf '%s\n' "$path"
    return 0
  fi
  mkdir -p "$root/Daily"
  atomic_write "$path" "$(render_template daily "$today" "$today")"
  printf '%s\n' "$path"
}

# init: resolve and create the vault root, then print it. The per-type folders are
# made on demand by capture; init exists so a first run resolves the configured
# vault and has somewhere to write. Idempotent — a second run reports the same root.
cmd_init() {
  local root
  root=$(vault_root)
  printf 'vault ready: %s\n' "$root"
}

# find <query>: list vault notes whose tag, title, or text matches the query, plus the notes
# that match any name or alias the matched notes declare — so a customer filed under one
# spelling still surfaces notes that used another. Prints matching paths; exit 0 even on no
# match (an empty result is not an error). Paths only, so no note contents are ever read.
cmd_find() {
  [ "$#" -eq 1 ] || { echo "usage: vault.sh find <query>" >&2; return 2; }
  local root seed terms moar all
  root=$(vault_root)
  # Pass 1 — direct substring hits (case-insensitive, fixed-string). The trailing `|| true`
  # keeps a no-match (grep exit 1) from tripping `set -euo pipefail`.
  seed=$(grep -rliIF -- "$1" "$root" --include='*.md' 2>/dev/null || true)
  [ -n "$seed" ] || return 0
  # Pass 2 — widen by the name and aliases the matched notes declare. The entity note carries
  # the alias list; a term with no such note simply adds nothing.
  terms=$(printf '%s\n' "$seed" | while IFS= read -r f; do
            sed -nE 's/^name:[[:space:]]*"?([^"]+)"?[[:space:]]*$/\1/p; s/^aliases:[[:space:]]*\[(.*)\].*$/\1/p' "$f" 2>/dev/null || true
          done | tr ',' '\n' | sed -E 's/^[[:space:]"]*//; s/[[:space:]"]*$//' | grep -vE '^$' | sort -u || true)
  all=$seed
  if [ -n "$terms" ]; then
    moar=$(printf '%s\n' "$terms" | while IFS= read -r t; do
             grep -rliIF -- "$t" "$root" --include='*.md' 2>/dev/null || true
           done)
    all=$(printf '%s\n%s' "$seed" "$moar")
  fi
  printf '%s\n' "$all" | grep -vE '^$' | sort -u || true
}

# index: (re)generate index.md — a catalog of the vault's canonical notes grouped
# by domain and folder, each linked with a one-line summary. This is the cheap top-level entry
# point retrieval reads FIRST (memory-architecture: "read index.md first"), before a
# Context Pack or a find. Retrieval entry points (Maps, Context Packs) lead; then the
# declarative and procedural folders. Sources are summarized by count, not listed
# (they are the provenance layer, not navigation). Deterministic; written atomically.
cmd_index() {
  [ "$#" -eq 0 ] || { echo "usage: vault.sh index" >&2; return 2; }
  local root out folder dir notes f base summary count nsrc
  root=$(vault_root)
  count=0
  out=$'# Index\n\nCatalog of this vault, generated by `vault.sh index`. Read this first, then\nload a Context Pack or a Map, then follow a note\'s links and `## Sources`.\n'
  # Scan the Life OS domain structure: work/, personal/, finance/, clients/, learning/
  local domains="work personal finance clients learning"
  for domain in $domains; do
    [ -d "$root/$domain" ] || continue
    out+=$'\n## '"${domain^}"$'\n'
    # Walk second-level directories within each domain
    for dir in "$root/$domain"/*/; do
      [ -d "$dir" ] || continue
      folder=$(basename "$dir")
      notes=$(find "$dir" -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort)
      [ -n "$notes" ] || continue
      out+=$'\n### '"${domain}/${folder}"$'\n'
      while IFS= read -r f; do
        [ -n "$f" ] || continue
        base=$(basename -- "$f" .md)
        # First non-empty, non-heading body line (after frontmatter), trimmed to 100 chars.
        summary=$(awk '
          NR==1 && $0=="---" { fm=1; next }
          fm==1 && $0=="---" { fm=0; next }
          fm==1 { next }
          /^#/ { next }
          /^[-*][[:space:]]/ { next }
          /^[[:space:]]*$/ { next }
          { gsub(/^[[:space:]]+/,""); print; exit }
        ' "$f" 2>/dev/null | sed 's/\[\[//g; s/\]\]//g' | cut -c1-100)
        if [ -n "$summary" ]; then
          out+="- [[$base]] — $summary"$'\n'
        else
          out+="- [[$base]]"$'\n'
        fi
        count=$((count + 1))
      done <<EOF
$notes
EOF
    done
  done
  # Also scan root-level Maps and Context Packs if they exist (legacy support)
  for folder in Maps "Context Packs"; do
    dir="$root/$folder"
    [ -d "$dir" ] || continue
    notes=$(find "$dir" -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort)
    [ -n "$notes" ] || continue
    out+=$'\n## '"$folder"$'\n'
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      base=$(basename -- "$f" .md)
      summary=$(awk '
        NR==1 && $0=="---" { fm=1; next }
        fm==1 && $0=="---" { fm=0; next }
        fm==1 { next }
        /^#/ { next }
        /^[-*][[:space:]]/ { next }
        /^[[:space:]]*$/ { next }
        { gsub(/^[[:space:]]+/,""); print; exit }
      ' "$f" 2>/dev/null | sed 's/\[\[//g; s/\]\]//g' | cut -c1-100)
      if [ -n "$summary" ]; then
        out+="- [[$base]] — $summary"$'\n'
      else
        out+="- [[$base]]"$'\n'
      fi
      count=$((count + 1))
    done <<EOF
$notes
EOF
  done
  nsrc=$(find "$root/raw" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  out+=$'\n## Sources\n- '"$nsrc"' source notes under `raw/` — the provenance layer every claim traces to.\n'
  out+=$'\n_'"$count"' notes indexed._\n'
  atomic_write "$root/index.md" "$out"
  printf '%s\n' "$root/index.md"
}

# rm <note>: delete a single note, only inside the vault. Refuses the vault root
# itself and anything outside it (mirrors skillkit.safe_remove). The one
# destructive path in this tool, structurally guarded against mass deletion.
cmd_rm() {
  [ "$#" -eq 1 ] || { echo "usage: vault.sh rm <note>" >&2; return 2; }
  local root note note_real root_real arg_real
  root=$(vault_root)
  root_real=$(abspath_dir "$root")
  # Refuse the vault root up front, before resolution can reinterpret it.
  arg_real=$(abspath_dir "$(dirname -- "$1")" 2>/dev/null)/$(basename -- "$1") || arg_real=""
  [ "$arg_real" = "$root_real" ] && { echo "refusing to remove vault root itself" >&2; return 2; }
  note=$(resolve_note "$root" "$1")
  note_real=$(abspath_dir "$(dirname -- "$note")")/$(basename -- "$note")
  case "$note_real" in
    "$root_real") echo "refusing to remove vault root itself" >&2; return 2 ;;
    "$root_real"/*) : ;;
    *) echo "refusing to remove outside vault: $note_real" >&2; return 2 ;;
  esac
  [ -d "$note_real" ] && { echo "refusing to remove a directory: $note_real" >&2; return 2; }
  rm -- "$note_real"
  printf 'removed: %s\n' "$note_real"
}

# --- selftest --------------------------------------------------------------

# Assert that a note's YAML frontmatter block parses. Dependency-free and
# deterministic (no interpreter, so it cannot be tripped by a wrapped/shimmed
# python on the host): extract the block between the first two `---` lines, then
# require every line to be blank, a `- ` list item, or `key: value` whose value
# is double-quoted, an inline `[...]` list, or free of the YAML-breaking bare
# `:`/`#`. Returns 0 when the frontmatter is valid, 1 otherwise. Selftest only.
assert_valid_frontmatter() {
  local file="$1" block
  block=$(awk 'NR==1 && $0!="---"{exit 1} NR==1{next} $0=="---"{exit} {print}' "$file") \
    || return 1
  printf '%s\n' "$block" | awk '
    /^[[:space:]]*$/ { next }
    /^- / { next }
    {
      i = index($0, ":")
      if (i == 0) { exit 1 }
      val = substr($0, i + 1)
      sub(/^[[:space:]]+/, "", val)
      sub(/[[:space:]]+$/, "", val)
      if (val == "") { next }                       # bare key (e.g. owner:)
      if (val ~ /^".*"$/) { next }                  # quoted value is safe
      if (val ~ /^\[.*\]$/) { next }                # inline list is safe
      if (val ~ /[:#]/) { exit 1 }                  # bare special char breaks YAML
      next
    }
    END { exit 0 }
  '
}

# Build a throwaway vault, exercise every subcommand, and assert structure (not
# exact timestamps). Cleans up only the mktemp-owned directory. Exit 0 on success.
selftest() {
  local tmp out person project meeting client before after

  tmp=$(mktemp -d "${TMPDIR:-/tmp}/second-brain.XXXXXX")
  trap 'test -n "${tmp:-}" && test -d "$tmp" && find "$tmp" -mindepth 0 -maxdepth 4 -delete' EXIT
  export VAULT="$tmp/vault"

  # slugify is deterministic and filesystem-safe.
  [ "$(slugify 'Ada Lovelace!')" = "ada-lovelace" ] || { echo "FAIL: slugify basic"; exit 1; }
  [ "$(slugify '  Q3   Roadmap  ')" = "q3-roadmap" ] || { echo "FAIL: slugify spaces"; exit 1; }
  [ "$(slugify '@@@')" = "untitled" ] || { echo "FAIL: slugify empty"; exit 1; }

  # init resolves and creates the vault root, reports it, and is idempotent.
  out=$(cmd_init)
  case "$out" in "vault ready: "*) : ;; *) echo "FAIL: init output ($out)"; exit 1 ;; esac
  [ -d "$VAULT" ] || { echo "FAIL: init did not create the vault root"; exit 1; }
  [ "$(cmd_init)" = "$out" ] || { echo "FAIL: init not idempotent"; exit 1; }

  # unknown type is rejected.
  cmd_capture bogus "x" 2>/dev/null && { echo "FAIL: bad type accepted"; exit 1; } || true

  # capture creates a typed note with frontmatter and a slug filename.
  person=$(cmd_capture person "Ada Lovelace")
  [ -f "$person" ] || { echo "FAIL: person note not created"; exit 1; }
  case "$person" in */work/people/ada-lovelace.md) : ;; *) echo "FAIL: person path ($person)"; exit 1 ;; esac
  grep -q '^type: person$' "$person" || { echo "FAIL: person frontmatter type"; exit 1; }
  grep -q '^## Related$' "$person" || { echo "FAIL: person Related section"; exit 1; }

  # capture never overwrites: a second person of the same title gets a -2 name.
  out=$(cmd_capture person "Ada Lovelace")
  case "$out" in */work/people/ada-lovelace-2.md) : ;; *) echo "FAIL: collision suffix ($out)"; exit 1 ;; esac
  [ "$out" != "$person" ] || { echo "FAIL: collision overwrote"; exit 1; }

  project=$(cmd_capture project "Q3 Roadmap")
  grep -q '^status: active$' "$project" || { echo "FAIL: project status field"; exit 1; }

  meeting=$(cmd_capture meeting "Kickoff sync")
  grep -q '^## Action items$' "$meeting" || { echo "FAIL: meeting headings"; exit 1; }

  # an added type (client) captures into work/companies by default.
  client=$(cmd_capture client "Acme Corp")
  [ -f "$client" ] || { echo "FAIL: client note not created"; exit 1; }
  case "$client" in */work/companies/acme-corp.md) : ;; *) echo "FAIL: client path ($client)"; exit 1 ;; esac
  grep -q '^type: client$' "$client" || { echo "FAIL: client frontmatter type"; exit 1; }
  grep -q '^tags: \[client\]$' "$client" || { echo "FAIL: client tag"; exit 1; }

  # key=value capture args land as frontmatter fields, and the YAML stays valid.
  out=$(cmd_capture feedback "SBI for Ada" sensitivity=private owner=lucas)
  grep -q '^sensitivity: private$' "$out" || { echo "FAIL: key=value sensitivity field"; exit 1; }
  grep -q '^owner: lucas$' "$out" || { echo "FAIL: key=value owner field"; exit 1; }
  assert_valid_frontmatter "$out" || { echo "FAIL: key=value frontmatter not valid YAML"; exit 1; }

  # a value carrying YAML-special characters is quoted so the frontmatter parses.
  out=$(cmd_capture project "Migration" 'note=phase: 1 #urgent')
  grep -q '^note: "phase: 1 #urgent"$' "$out" || { echo "FAIL: special value not quoted"; exit 1; }
  assert_valid_frontmatter "$out" || { echo "FAIL: quoted value frontmatter not valid YAML"; exit 1; }

  # a user field overriding a type default replaces it — no duplicate key.
  out=$(cmd_capture project "Owned" owner=lucas company=acme cadence=weekly)
  [ "$(grep -c '^owner:' "$out")" -eq 1 ] || { echo "FAIL: owner key duplicated"; exit 1; }
  grep -q '^owner: lucas$' "$out" || { echo "FAIL: owner override value"; exit 1; }
  grep -q '^company: acme$' "$out" || { echo "FAIL: company field"; exit 1; }
  grep -q '^cadence: weekly$' "$out" || { echo "FAIL: cadence field"; exit 1; }
  assert_valid_frontmatter "$out" || { echo "FAIL: override frontmatter not valid YAML"; exit 1; }

  # reserved structural keys cannot be overridden via key=value.
  cmd_capture idea "Reserved" type=person 2>/dev/null && { echo "FAIL: reserved key accepted"; exit 1; } || true

  # a bad field key is rejected and leaves no note behind.
  before=$({ find "$tmp/vault/work/topics" -type f 2>/dev/null || true; } | wc -l)
  cmd_capture idea "Bad field" "Bad Key=x" 2>/dev/null && { echo "FAIL: bad field key accepted"; exit 1; } || true
  after=$({ find "$tmp/vault/work/topics" -type f 2>/dev/null || true; } | wc -l)
  [ "$before" = "$after" ] || { echo "FAIL: bad field left an orphan note"; exit 1; }

  # append adds a timestamped bullet under ## Log (assert bullet + text + section,
  # not the exact time), and never below ## Related.
  cmd_append "$meeting" "agreed on scope" >/dev/null
  grep -q -- '- .* agreed on scope$' "$meeting" || { echo "FAIL: append bullet"; exit 1; }
  grep -q '^## Log$' "$meeting" || { echo "FAIL: append Log section"; exit 1; }
  awk '/^## Log$/{l=NR} /agreed on scope/{b=NR} /^## Related$/{r=NR}
       END{exit !(l<b && b<r)}' "$meeting" \
    || { echo "FAIL: append bullet not between Log and Related"; exit 1; }

  # link adds a [[wikilink]] under ## Related, and is idempotent.
  cmd_link "$meeting" "$person" >/dev/null
  grep -qF -- '[[ada-lovelace]]' "$meeting" || { echo "FAIL: link to person"; exit 1; }
  cmd_link "$meeting" "Q3 Roadmap" >/dev/null
  grep -qF -- '[[q3-roadmap]]' "$meeting" || { echo "FAIL: link to project by title"; exit 1; }
  cmd_link "$meeting" "$person" >/dev/null
  [ "$(grep -cF -- '[[ada-lovelace]]' "$meeting")" -eq 1 ] || { echo "FAIL: link not idempotent"; exit 1; }

  # link creates the ## Related section when a note lacks one.
  printf '%s\n' '# bare' > "$tmp/vault/bare.md"
  cmd_link "$tmp/vault/bare.md" "Ada Lovelace" >/dev/null
  grep -q '^## Related$' "$tmp/vault/bare.md" || { echo "FAIL: Related not created"; exit 1; }
  grep -qF -- '[[ada-lovelace]]' "$tmp/vault/bare.md" || { echo "FAIL: link into bare note"; exit 1; }

  # daily is idempotent: same path twice, no duplicate.
  local d1 d2
  d1=$(cmd_daily); d2=$(cmd_daily)
  [ "$d1" = "$d2" ] || { echo "FAIL: daily not idempotent"; exit 1; }
  [ -f "$d1" ] || { echo "FAIL: daily note missing"; exit 1; }
  grep -q '^## Log$' "$d1" || { echo "FAIL: daily template"; exit 1; }

  # find locates a note by its content.
  out=$(cmd_find "agreed on scope")
  case "$out" in *"$meeting"*) : ;; *) echo "FAIL: find by text"; exit 1 ;; esac
  # find by tag matches the project frontmatter.
  out=$(cmd_find "tags: [project]")
  case "$out" in *"$project"*) : ;; *) echo "FAIL: find by tag"; exit 1 ;; esac

  # find expands a name's aliases — a note that used a variant spelling still surfaces, so a
  # customer filed under one name is never lost to a search that used another.
  local variant
  cmd_capture client "IndySoft" 'aliases=[Indy Soft, ISoft]' >/dev/null
  variant=$(cmd_capture meeting "Indy Soft kickoff")
  out=$(cmd_find "IndySoft")
  case "$out" in *"$variant"*) : ;; *) echo "FAIL: find did not expand aliases to the variant note"; exit 1 ;; esac

  # index builds a catalog: the file exists, groups by folder, links a known note, counts notes.
  out=$(cmd_index)
  case "$out" in */index.md) : ;; *) echo "FAIL: index path ($out)"; exit 1 ;; esac
  [ -f "$VAULT/index.md" ] || { echo "FAIL: index.md not created"; exit 1; }
  grep -q '^## Projects$' "$VAULT/index.md" || { echo "FAIL: index missing folder heading"; exit 1; }
  grep -qF -- '[[q3-roadmap]]' "$VAULT/index.md" || { echo "FAIL: index missing a known note link"; exit 1; }
  grep -q 'notes indexed' "$VAULT/index.md" || { echo "FAIL: index missing count footer"; exit 1; }

  # rm guard: the root guard fires with its own message, not a generic miss.
  out=$(cmd_rm "$tmp/vault" 2>&1) && { echo "FAIL: rm accepted vault root"; exit 1; } || true
  case "$out" in *"vault root"*) : ;; *) echo "FAIL: rm root message ($out)"; exit 1 ;; esac
  cmd_rm "$tmp/outside.md" 2>/dev/null && { echo "FAIL: rm accepted missing/outside"; exit 1; } || true
  cmd_rm "$person" >/dev/null
  [ -f "$person" ] && { echo "FAIL: rm did not delete note"; exit 1; } || true

  echo "vault selftest: ok"
}

# --- dispatch --------------------------------------------------------------

usage() {
  echo "usage: vault.sh <init|capture|append|link|daily|find|index|rm> [args]" >&2
  echo "       vault.sh capture <type> <title> [key=value ...]" >&2
  echo "       vault.sh --selftest" >&2
  echo "types: $TYPES" >&2
  echo "vault root: \$VAULT, else \`skill-config path\`, else ./vault" >&2
}

main() {
  case "${1:-}" in
    --selftest) selftest; exit 0 ;;
    -h|--help) usage; exit 0 ;;
  esac
  [ "$#" -ge 1 ] || { usage; exit 2; }
  local sub="$1"; shift
  case "$sub" in
    init)    cmd_init "$@" ;;
    capture) cmd_capture "$@" ;;
    append)  cmd_append "$@" ;;
    link)    cmd_link "$@" ;;
    daily)   cmd_daily "$@" ;;
    find)    cmd_find "$@" ;;
    index)   cmd_index "$@" ;;
    rm)      cmd_rm "$@" ;;
    *) echo "unknown subcommand: $sub" >&2; usage; exit 2 ;;
  esac
}

main "$@"
