# Conventional Commits and SemVer

How `skill-changelog` turns a commit range into a changelog section, and how the same
commits decide the next version. The tool is the source of truth: it reads commit
**subject lines only** (`git log --pretty=%s`), parses each against the Conventional
Commits grammar, drops anything that does not match, groups the rest by type, and renders
a Keep-a-Changelog section. The version bump is a human-or-agent decision the tool does
not compute — this page makes that decision deterministic.

## The grammar

Each subject is matched against one shape:

```
type(scope)!: subject
```

- **type** — a lowercase word, required. Only the ten types below are tracked; an
  unrecognized type (`wip`, `merge`) is dropped, not rendered.
- **(scope)** — optional, in parentheses, naming the area touched (`api`, `parser`). The
  scope renders as a bold prefix on the line: `- **api**: drop legacy field`.
- **!** — optional, immediately before the colon. The breaking-change marker.
- **: subject** — a colon, a space, then the description. The description is required.

The match is anchored to the whole line. A subject missing the colon, missing the type,
or leading with prose (`fixed the bug`) does not parse and is silently ignored. Parsing
is case-insensitive on the type (`Feat:` becomes `feat`) but the description is preserved
verbatim.

## Types and the sections they surface

The tracked types and their changelog section titles, in render order:

| Type       | Section title    | Surfaces? |
|------------|------------------|-----------|
| `feat`     | Features         | yes       |
| `fix`      | Bug Fixes        | yes       |
| `perf`     | Performance      | yes       |
| `refactor` | Refactors        | yes       |
| `docs`     | Documentation    | yes       |
| `test`     | Tests            | yes       |
| `build`    | Build            | yes       |
| `ci`       | CI               | yes       |
| `chore`    | Chores           | yes       |
| `style`    | Style            | yes       |

Every tracked type surfaces — the tool renders one section per type that holds at least
one commit, in the table's order, which is the insertion order of the `TYPES` map in
`core.py`. A type with no commits in the range produces no section. The order is fixed:
Features always precede Bug Fixes, which precede Performance, down the table. The order
does not depend on commit timestamps, so the same range always renders identically.

A type outside this table (a typo like `feet:`, or a non-standard `wip:`) fails the
membership check and is dropped. Dropping the stragglers is the determinism guarantee:
the rendered section is a pure function of the parsed subjects, the version, and the date.

## Breaking changes

The tool recognizes a breaking change **only** through the `!` marker before the colon:

```
feat!: drop the v1 endpoint
fix(api)!: rename the response field
```

A breaking commit is rendered twice. First it is listed in a dedicated
`### ⚠ BREAKING CHANGES` section, which renders **before** every type section. Then the
same commit also appears under its own type section (a `feat!` shows up under both
BREAKING CHANGES and Features). The breaking list collects every commit whose subject
carried `!`, in commit order within the range.

Limitation to know: the tool sees subjects only, so the Conventional Commits
`BREAKING CHANGE:` *footer* in a commit body is invisible to it. A footer-only breaking
change will not surface. Per a breaking change that must appear, the subject carries the
`!` marker — the footer alone is not enough.

## Versioning decision (SemVer)

`skill-changelog --version X.Y.Z` takes the version as a literal label and writes exactly
that into the header. Choosing `X.Y.Z` is the decision this section governs. Read the
parsed commits in the range, then climb to the highest bump any single commit forces:

1. **Major (`X`)** — any breaking change in the range. A single commit with the `!`
   marker forces a major bump and resets minor and patch to zero (`1.4.2` becomes
   `2.0.0`). Breaking always wins, whatever its type.
2. **Minor (`Y`)** — at least one `feat` and no breaking change. A new feature bumps the
   minor and resets patch (`1.4.2` becomes `1.5.0`).
3. **Patch (`Z`)** — a `fix` (or `perf`) and no `feat` and no breaking change. A bug fix
   bumps the patch (`1.4.2` becomes `1.4.3`).

Types that document or maintain the codebase — `docs`, `refactor`, `test`, `build`, `ci`,
`chore`, `style` — surface in the changelog but do **not**, on their own, force any bump.
A range containing only those types is a judgment call: keep the patch number or skip the
release. The rule is monotone: take the single highest bump the range justifies, never
the sum. Three features and one breaking change is one major bump, not a major plus three
minors. Pre-`1.0.0` projects may treat a breaking change as a minor bump, but the tool
imposes no such policy — the version string is whatever you pass.

## Edge cases

- **Non-conventional commits are ignored.** A subject that does not match the grammar
  (`update stuff`, `WIP`) parses to nothing and never reaches the output. The section is
  silent about it — review the rendered groups against the raw range to catch a dropped
  commit that was meant to count.
- **Merge commits** (`Merge branch 'main' into feature`) are non-conventional and so are
  ignored. Generate from a linear range, or expect merges to drop out.
- **Reverts** are rendered only when the subject is itself conventional. `revert: ...` is
  not a tracked type and is dropped; `fix: revert the broken migration` parses as a `fix`
  and surfaces under Bug Fixes. A revert that should appear in the log carries a tracked
  type.
- **Empty range.** A range with no commits, or one where every commit was filtered out,
  renders the header and date alone with no type sections. An empty body is the correct,
  deterministic output, not an error — when this happens, the range or the commit
  discipline is the thing to inspect.
- **Duplicate subjects** each render as their own line; the tool does not deduplicate.

## Worked example

The range `v1.4.2..HEAD` contains these subjects, in commit order:

```
feat(parser): support nested scopes
fix: handle an empty commit range
feat!: drop the deprecated --legacy flag
docs: document the breaking change
chore: bump dev dependencies
Merge branch 'release' into main
wip: scratch work
update the readme quickly
```

Parsing keeps five of the eight: the two `feat`, the `fix`, the `docs`, and the `chore`.
The merge line, the `wip` line (unknown type), and the bare-prose line are dropped. One
`feat` carries `!`, so it is also a breaking change. The rendered section is:

```markdown
## [2.0.0] - 2026-06-22

### ⚠ BREAKING CHANGES

- drop the deprecated --legacy flag

### Features

- **parser**: support nested scopes
- drop the deprecated --legacy flag

### Bug Fixes

- handle an empty commit range

### Documentation

- document the breaking change

### Chores

- bump dev dependencies
```

The version is `2.0.0`: the breaking `feat!` forces a major bump from `1.4.2`, resetting
minor and patch. Without that one commit the range would be a minor bump (`1.5.0`) on the
strength of the surviving `feat`. The breaking commit appears in both the BREAKING
CHANGES section and Features; the sections follow the fixed type order; the dropped lines
leave no trace.
