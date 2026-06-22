# Supply-chain audit

The judgment behind the supply-chain-audit steps. The gates (`skill-gate`) run the
scanners and emit findings; this page is what the scanners cannot decide for you — which
finding is real, which is reachable, and what a defensible response looks like. A modern
application ships far more code from its dependency tree than from its own repository, so
the dependency tree is the attack surface. Treat every package as untrusted input that
executes with your privileges until an audit says otherwise.

## The threat model — five ways the tree turns hostile

An attacker rarely breaks your code. The attacker ships you theirs, through one of these:

- **Typosquatting.** A malicious package takes a name one keystroke from a popular one
  (`reqeusts` for `requests`, `colourama` for `colorama`). A fat-fingered install or a
  copy-pasted command pulls the impostor, and the impostor runs install hooks with the
  developer's credentials. The defense is verifying the package name and source against
  the real project, never the registry search ranking.
- **Dependency confusion.** A build resolves an internal package name (`acme-internal-auth`)
  against a public registry because the public index is searched alongside the private
  one. An attacker publishes that exact name publicly at a higher version, and the
  resolver prefers the higher version. The defense is scoped registries, an explicit index
  priority, and namespace ownership on every public registry.
- **Compromised maintainer.** A legitimate package gains a malicious version after a
  maintainer's account is phished, a token leaks, or the project is sold. The name and the
  download stats look trustworthy because, until that release, they were. The defense is
  pinning (below) plus a delay before adopting brand-new releases, so a yanked-within-hours
  compromise never reaches your build.
- **Malicious postinstall.** A package declares a lifecycle script (`postinstall`,
  `setup.py` execution, a build plugin) that runs arbitrary code at install time, before any
  of your tests or review. Credential theft and crypto-miners ride in here because install
  runs on developer laptops and CI runners with broad access. The defense is disabling
  install scripts by default and auditing the few packages that genuinely need them.
- **Leaked credentials.** A token, a cloud key, or a database password is committed to the
  repository, baked into an image layer, or printed into a build log. A leak is not a
  dependency flaw, yet it belongs in the same audit because the blast radius is identical: an
  attacker with the credential owns whatever the credential owns. The defense is secret
  scanning on every commit and on history, plus rotation the moment a secret is found.

Read every CVE finding through this model. A vulnerability in a package you pulled by
mistake is a different problem from the same CVE in a package you depend on deliberately.

## Pinning and lockfiles — the defense that does the most

A floating version range (`^1.2.0`, `>=2,<3`, `latest`) means the resolver picks a version
at install time, so two builds of the same commit can ship different code. That gap is the
hole every compromised-maintainer and dependency-confusion attack drives through. Close it:

- **Pin transitively, not just at the top.** A lockfile (`package-lock.json`,
  `poetry.lock`, `Cargo.lock`, `requirements.txt` with hashes, `go.sum`) records the exact
  resolved version of every package in the tree, direct and transitive. The manifest states
  intent; the lockfile states reality. The lockfile is the artifact an audit trusts.
- **Pin by hash where the ecosystem allows it.** A version number can be re-pointed by a
  registry; a content hash cannot. Hash-pinning (`--require-hashes`, `go.sum`,
  `Cargo.lock` checksums) means a swapped artifact fails the install instead of
  silently entering the build.
- **Commit the lockfile and install from it.** A reproducible install (`npm ci`,
  `poetry install` against the lock, `pip install --require-hashes`) reads the lockfile and
  refuses to drift. An install that regenerates the lockfile in CI has defeated its own
  purpose.
- **Treat a lockfile change as a code change.** A diff that bumps a transitive dependency
  is reviewed like any other diff, because it is new code entering the artifact. An
  unexplained lockfile churn in an unrelated PR is a red flag, not noise.

Without a committed lockfile, an SBOM and a CVE scan describe one build that no one can
reproduce — the audit is theater. Pinning is the precondition, not an optional hardening.

## SBOM — what it is and what it is for

A Software Bill of Materials is the ingredient list of the build: every component, its
exact version, and ideally its supplier and license. An SBOM is not a security scan and
finds nothing by itself. Its value is answering one question fast: *am I affected?* When
the next `log4shell` lands, the team with a current SBOM greps it and has the answer in
seconds; the team without one spends the incident reconstructing what they shipped.

Two formats dominate, and a useful audit can emit either:

- **CycloneDX** — security-first, from OWASP. Compact, models the dependency graph and
  vulnerability data well, and is the common default for application scanning. Generated by
  `syft`, `trivy`, and most language tooling.
- **SPDX** — a Linux Foundation / ISO standard, license-and-compliance-first. Richer
  provenance and licensing fields, the format procurement and legal teams expect.

Pick by audience: CycloneDX for the security pipeline, SPDX when a contract or compliance
regime names it. An SBOM is only as honest as its inputs, so generate it from the same
locked tree the build ships — an SBOM built from floating manifests lists components that
were never installed.

## Triaging a CVE finding — severity is a label, not a verdict

A scanner reports a vulnerability against a package and version. Raw, that report is noise;
triage turns it into a decision. Work these dimensions in order:

### Severity versus CVSS versus context

The CVSS score (and the Critical / High / Medium / Low band derived from it) is the
*intrinsic* severity of the flaw in the abstract — assuming the worst-case deployment.
The score is an input, not the answer. A CVSS 9.8 in a parser you never feed untrusted
input ranks below a CVSS 6.5 on your internet-facing auth path. Read the vector string, not
just the number: network-attackable with no privileges and no user interaction is a
different animal from local-only requiring an authenticated admin.

### Reachability and exploitability

The decisive question: *does my code reach the vulnerable function under attacker-influenced
input?* A CVE in a code path your application never calls is present but not exploitable.
Reachability analysis (some scanners flag it directly) separates the dependency you merely
*contain* from the one you actually *invoke*. The presence of an exploit in the wild
(KEV-listed, a public PoC) sharply raises the real-world priority regardless of CVSS,
because exploitability has stopped being theoretical.

### Direct versus transitive

A direct dependency is one your manifest names, so you control its version outright. A
transitive dependency is pulled by something else, so the fix path runs through the
intermediate package. A CVE in a transitive dependency often cannot be bumped in isolation:
the parent pins a vulnerable range, and forcing the child to a fixed version (an override,
a resolution, a `replace` directive) risks breaking the parent's assumptions. Identify the
full path from a root dependency to the vulnerable package before deciding the fix — the
path determines whether you upgrade one line or several.

### Is there a fixed version

A finding with a published fixed version is a routine upgrade. A finding with no fix yet
(a zero-day, or an unmaintained package) is a containment problem, not an upgrade problem,
and the response shifts to mitigation or replacement. Confirm the fixed version actually
resolves the specific CVE before claiming the finding closed — advisories sometimes split a
flaw across several releases.

## What to do on a finding — four defensible responses

Every confirmed finding resolves to exactly one of these, each with a written reason:

- **Upgrade.** A fixed version exists and the bump is compatible — take it, regenerate the
  lockfile, and rerun the scan to confirm the finding clears. The upgrade is the default and
  the preferred outcome.
- **Pin or override.** The vulnerable package is transitive and no clean upgrade path
  exists — pin the child to a fixed version through the ecosystem's override mechanism, then
  test that the parent still behaves. The override is documented so a future reader knows
  why the lockfile disagrees with the manifest.
- **Patch.** No upstream fix exists but the flaw is reachable and serious — apply a vetted
  local patch (a vendored fix, a `patch-package` overlay, a backport) as a stopgap, and
  track the upstream issue so the patch is removed once a real release lands.
- **Accept with justification.** The finding is not reachable, or the residual risk is
  below the bar — record an explicit, signed-off exception that names the CVE, states why it
  is accepted (not reachable / no fix / compensating control), and sets a review date. A
  suppression without a justification is a hidden risk that the next audit cannot
  distinguish from an oversight.

The unacceptable fifth option is silent dismissal. A finding that vanishes from the report
with no upgrade, no override, no patch, and no recorded acceptance is the one that becomes
an incident.

## A worked triage — one transitive CVE

A `trivy` scan of a Node service reports **CVE-2023-XXXXX, Critical, CVSS 9.8** against
`minimatch@3.0.4` — a ReDoS (regular-expression denial of service). The package is not in
the manifest. Walk the triage:

1. **Trace the path.** `npm ls minimatch` shows the chain
   `app -> glob@7.1.6 -> minimatch@3.0.4`. The dependency is transitive, pulled by `glob`,
   pulled by a build-time test runner. The finding is real; the band is Critical.
2. **Test reachability and context.** The vulnerable code path is the glob matcher, and it
   runs only at build time against repository paths the team controls — never against
   request input in production. Attacker-controlled input does not reach the vulnerable
   regex, so the *real-world* severity is far below the CVSS 9.8 the band advertises.
3. **Check the fix path.** `minimatch@3.0.5` resolves the CVE. The direct parent `glob@7.1.6`
   pins `^3.0.2`, which already admits `3.0.5`, so the fix is a lockfile refresh rather than
   a parent upgrade — no override is required.
4. **Choose and record the response.** Regenerate the lockfile to pull `minimatch@3.0.5`,
   then rerun the scan to confirm the finding clears. Record the decision: upgraded
   transitively, reachability was build-time-only, no production exposure, fix verified
   against the named CVE. The audit now shows a resolved finding with a reason a reviewer
   can check, not a number that vanished.

That trail — path, reachability, fix, recorded decision — is the deliverable. The CVSS
number was the alarm; the triage was the work.

## Real tools, one role each

The audit references these; the exact commands live behind `skill-gate`, never inlined here.

- **`trivy`**, **`grype`** — scan a tree (or an image) against vulnerability databases and
  emit CVE findings with severity.
- **`pip-audit`** (Python), **`npm audit`** (Node) — ecosystem-native vulnerability scans
  reading the lockfile.
- **`syft`** — generate the SBOM (CycloneDX or SPDX) from the source tree or image.
- **`gitleaks`** — scan the working tree and history for leaked credentials.

The scanner is the easy half. The triage and the recorded decision are the audit.
