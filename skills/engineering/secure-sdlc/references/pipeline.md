# The secure-SDLC pipeline

The judgment behind the secure-sdlc steps. A gate run is cheap; a defect that reaches
production is not, so the discipline is built around catching each class of defect at the
earliest gate that can see it and then *attesting* what was checked. The gates
(`skill-gate`) own the deterministic scanning; this page explains why each gate exists,
why the order is fixed, what the attestation proves, and where the pipeline quietly lies
to you.

## The seven gates and the defects they catch

Each category targets one class of defect. A green gate is a claim that one class is
absent at this revision; the claims compose into the attestation.

| Gate | Tool (example) | Defect class it catches |
|------|----------------|-------------------------|
| **format** | the language formatter | diff noise, inconsistent style that hides real changes in review |
| **lint** | the language linter | bug-prone constructs, dead code, anti-patterns the compiler permits |
| **types** | the type checker | contract violations, null misuse, shape mismatches across call sites |
| **sast** | Semgrep | injection, unsafe deserialization, hard-coded crypto, dangerous sinks in *first-party* code |
| **sca** | trivy, pip-audit | known-vulnerable *dependencies* — a CVE in code the project did not write |
| **secrets** | gitleaks | committed credentials: API keys, tokens, private keys in the diff or history |
| **test** | the project test runner | behavioral regressions — logic that no longer does what the suite asserts |

The split between **sast** and **sca** matters: sast reads the code the team wrote, while
sca reads the manifest of code the team imported. A SQL-injection sink is a sast finding;
a vulnerable `requests` version is an sca finding. Neither gate sees the other's defect
class, so both run.

## Why the order is fixed

The order is cheapest-and-broadest first, narrowest-and-slowest last. Three reasons drive
it:

1. **Fast feedback.** Format and lint finish in seconds and reject the largest share of
   trivial defects, so a developer learns about a style or lint break before a minutes-long
   SAST scan even starts.
2. **No wasted scans.** A type error often means the code cannot run, which makes a test
   run meaningless until the type gate is green; types therefore precede tests.
3. **Stable diffs for the security gates.** Formatting first means the SAST and secrets
   scanners read a normalized tree, so a finding points at real code rather than at a line
   that the formatter was about to move.

Quality gates (format → lint → types) come before security gates (sast → sca → secrets)
because a security finding on code that is about to be reformatted or retyped is a finding
on a moving target. The **test** gate runs after the static gates because a passing suite
on code that fails type checking proves nothing durable. The final **`--strict`** pass
runs last because a missing-tool failure is only meaningful once the present tools are all
green.

## When a finding blocks, and when it may be waived

The default for a critical or high finding is **block**. A finding drops below blocking
only through a recorded waiver — never through silence, and never by editing a threshold to
duck the alarm.

A waiver is legitimate in a bounded set of cases:

- A confirmed false positive: the flagged sink is unreachable, or the rule misread the code.
- A vulnerable transitive dependency with no fixed version yet, where a compensating control
  (network policy, input bound) closes the path.
- A finding in test-only or fixture code with no production reach.

A waiver is **not** legitimate as a way to hit a deadline, to silence a recurring alarm
nobody wants to read, or to cover a finding the author has not actually understood.

### How a waiver is recorded

A waiver is data, not a conversation. Each waiver entry carries:

- the **rule id** and the exact **location** (path and line) being waived,
- a one-line **justification** naming the false-positive reason or the compensating control,
- the **approver** and the **date** the waiver was granted,
- an **expiry date** after which the waiver stops suppressing the finding.

`skill-gate` reads the waiver file, suppresses only the matching rule-id-and-location pair,
and copies every active waiver into the attestation. A waiver with no expiry is rejected by
the gate, so a waiver cannot become silently permanent (see the failure modes below).

## The attestation — what "secure at this level" means

The attestation is assembled once the gates are green, with the machine-readable gate record from `skill-gate --strict --format json` as its core. The
artifact is the difference between "the scans ran" and "here is proof of what the scans
covered." The attestation records four things:

- **SBOM** — the software bill of materials: every dependency and version that composes the
  build, so a future CVE can be matched against the exact tree that shipped.
- **CVE summary** — the sca findings at ship time: each known vulnerability, its severity,
  and whether it was fixed or waived.
- **Waiver list** — every active waiver with its rule id, justification, approver, and
  expiry, so an auditor sees what was consciously accepted.
- **Gate-version record** — the version of each scanner and ruleset that produced the
  result, so a green result is reproducible and a later ruleset upgrade is detectable.

"Secure at this level" is a precise, bounded claim: at this revision, with these scanner
versions and these rulesets, no unwaived finding of the seven defect classes remained. The
claim is **not** "this code has no vulnerabilities." A zero-day absent from every ruleset
passes every gate. The attestation states the level so that the claim is honest about its
own ceiling — a SAST tool finds the bugs its rules encode and nothing beyond them.

## Failure modes — where the pipeline lies

The gates fail safe only when their failure is visible. Two failure modes turn a green
result into a false comfort.

### A gate skipped because a tool is missing

A scanner absent from the runner is the most dangerous failure, because a skipped gate and
a passed gate can look alike in a summary. With pip-audit uninstalled, a naive run reports
"sca: skipped" and the pipeline still goes green, so the build ships with its dependencies
unscanned. The guard is the final **`--strict`** pass: under `--strict` a missing tool is a
hard failure, not a skip, which forces the runner to install the scanner or to fail loudly.
Run the merge gate under `--strict` so a missing tool stops the line (Jidoka) rather than
opening a hole.

### A waiver that becomes permanent

A waiver is meant as a dated exception, yet an undated waiver quietly hardens into policy:
the finding is suppressed forever, the compensating control rots, and the original reason is
forgotten. Two mechanics keep a waiver honest. First, the gate rejects any waiver without an
expiry, so an eternal waiver cannot be written. Second, an expired waiver stops suppressing
its finding, so the alarm returns and forces a fresh decision. A waiver that keeps getting
renewed without scrutiny is itself a finding — surface the renewal in review.

## Worked example — one change through the pipeline

A developer adds an endpoint that fetches a report by id and renders it. Walk the change
through the gates:

1. **Scope.** `skill-gate --list` reports a Python stack with all seven categories active.
   The scope is confirmed.
2. **format** → reformats two lines, exits zero on rerun.
3. **lint** → flags an unused import; the developer removes the import and the gate exits
   zero.
4. **types** → flags that the id parameter is typed `str` but indexed as `int`; the
   developer fixes the annotation and the gate exits zero.
5. **sast (Semgrep)** → flags an f-string SQL query as an injection sink (high). The
   developer rewrites the query as parameterized; the rerun exits zero. A real defect was
   caught before merge.
6. **sca (pip-audit)** → reports a high CVE in a transitive `urllib3` pin with no fixed
   release yet. The path is unreachable from the new endpoint, so a waiver is recorded:
   rule id, the package and line, justification "no fixed version; endpoint does not reach
   the affected code path," approver, today's date, and a 30-day expiry. The gate now passes
   with the waiver noted.
7. **secrets (gitleaks)** → finds a test API key in a new fixture (high). A fixture secret
   still leaks, so the developer replaces the literal with an environment lookup; the rerun
   exits zero.
8. **test** → the suite passes, including a new test that fails without the parameterized
   query.
9. **`--strict`** → every tool is present and green, so the merge gate exits zero.
10. **attestation** → the gate record from `skill-gate --strict --format json`, the SBOM (via
    supply-chain-audit), a CVE summary listing the waived `urllib3` finding, and the one
    active waiver with its 30-day expiry are collected into the attestation. The change ships "secure at this level," and the waived CVE is now tracked
    toward its expiry rather than forgotten.

The leverage is in steps 5 through 7: the injection sink, the unreachable CVE, and the
fixture secret are three distinct defect classes, each caught by the one gate that could see
it, each resolved by a fix or a dated waiver, and each recorded in an artifact that outlives
the pull request.
