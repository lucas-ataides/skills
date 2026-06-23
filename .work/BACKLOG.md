# Skills backlog — the loop's resumable state

Source of truth for the mega-batch. Work top-down in lint-gated parallel waves; commit
per wave; update status here each wave. Resume by reading this file + `git log`.

Legend: `[x]` done & lint-green · `[~]` in progress · `[ ]` todo · `[!]` blocked

## Done (foundation + first domains)
- [x] toolchain: skill-lint, skill-new, skill-gate, skill-changelog, skill-docs, skill-update, skillkit
- [x] meta: foundation, creating-skills, setup
- [x] engineering: secure-sdlc, tdd, code-review, supply-chain-audit, changelog-gen, docs-sync, app-completion-loop, engineering
- [x] productivity: grill-me, least-code

## Wave 0 — directives + cross-cutting (manual)
- [x] merge devops + qa INTO engineering (delete standalone; move references)
- [x] deterministic git: scripts/git-commit.sh (shell) + engineering/git-guardrails
- [x] install mechanism: marketplace.json + installer skill triggered by "install ldatb skills"
- [x] productivity: caveman, caveman-review
- [x] meta: cavecrew (rule: every non-user-facing subagent follows it)

## Wave 1 — marketing cluster (coreyhaines31 ports → marketing/) ✅
- [x] copywriting · [x] copy-editing · [x] ad-creative · [x] cold-email
- [x] social-content · [x] sales-enablement · [x] churn-prevention
- [x] site-architecture · [x] marketing-psychology · [x] marketing-ideas · [x] revops

## Wave 2 — design + quality cluster ✅
- [x] design/: web-design-guidelines · ui-ux-pro-max · design-taste-frontend · gpt-taste · brandkit · industrial-brutalist-ui
- [x] quality/: polish · overdrive · full-output-enforcement

## Wave 3 — process/writing/architecture cluster ✅
- [x] engineering/: to-issues · software-architecture · subagent-driven-development
- [x] quality/: verification-before-completion
- [x] productivity/: handoff · teach · simple
- [x] marketing/: public-relations

## Wave 4 — documents cluster (documents/) ✅
- [x] pptx · [x] pdf · [x] docx · [x] xlsx (python-pptx/openpyxl/python-docx/WeasyPrint+reportlab)

## Wave 5 — cloud cluster (cloud/) ✅
- [x] aws-toolkit · [x] azure-toolkit · [x] gcp-toolkit · [x] cloud-best-practices (SOC2)

## Wave 6 — agent-infra ports ✅ (ralph-vault → wave 7)
- [x] ralph (autonomous loop) · [x] autoguardrails (POLICY.md + scripts/check-policy.sh, no LLM, --selftest)

## Wave 7 — second brain / obsidian + management ✅
- [x] obsidian/: obsidian-vault (compiler + 6 _tools validator scripts) · second-brain-crud (vault.sh CRUD) · ralph-vault
- [x] management/: project-management · client-satisfaction · employee-management

## Wave 8 — social ✅
- [x] social/: social-media-viral (IG + X viral research via Chrome; research+draft only, posting gated)

## Final — stress test ALL skills to a Japanese quality bar ✅ (round 1)
- [x] Round 1: 6 adversarial critics over all 62 skills. marketing + cloud/obsidian/social: clean.
      11 blocker/major defects found + fixed + re-verified:
      - secure-sdlc/supply-chain-audit: SBOM now via `syft` (skill-gate had no SBOM); waivers reframed as a reviewer-checked log (skill-gate doesn't enforce).
      - autoguardrails: fixed unrunnable script path; real NUL-safe `git ls-files -z`.
      - docx: fixed crashing `add_style("Caption")` (built-in) → fetch-and-modify.
      - brandkit: corrected wrong WCAG contrast figures (verified by computation).
      - ralph: reset working tree from VCS on a red gate before retry.
      - changelog-gen: `--date` added so the dated header is reproducible.
      - creating-skills: `skill-new --invocation model` directly (Makefile passes no flag).
      - management trio + vault.sh: extended capture with key=value + types (client/feedback/1on1/company); fixed broken cross-ref.
- [ ] Round 2 (optional): re-run critics; expect few/none given round 1 + deterministic gates.

## Remaining polish
- [x] README reflects full library + "install ldatb skills" flow.

# ============ REFACTOR (round 2, 2026-06-22) — user consolidation pass ============
Decisions: marketing→4 (copywriting/content/growth/outreach). Config: ~/.config/skills/skills.toml
(global) + per-project ./skills.toml (NO "ldatb" prefix). Second-brain feed: OPT-OUT default,
present on EVERY skill, graceful if no vault configured, agent decides relevance + ASKS when unsure,
deterministic (script + manual). Per-skill docs: generated README.md per skill (a skill-readme tool).

## R-merges (settle the skill set)
- [x] remove caveman-review
- [x] marketing 13→4: copywriting · content · growth · outreach. social/ removed.
- [x] design 5→1 `frontend-design` (Swiss editorial + brutalism) + absorbed site-architecture; brandkit separate.
- [x] `agent-loop` ← ralph + app-completion-loop (checkpointed + autonomous; subagent-driven-development composes).
- [x] obsidian 3→1 `second-brain` (capture + compile + retrieve + maintain; 7 scripts moved in; checkpoints/gates preserved).
- [x] secure-sdlc ← absorbed supply-chain-audit (references/supply-chain.md is now canonical there).
- [x] renamed docs-sync → `documentation`; simple → `brainstorm`.
- [x] least-code imbued into foundation (subtraction ladder + references/subtraction.md); standalone removed. (full-output-enforcement + verification-before-completion kept standalone; imbue note in foundation pending.)

## R-behavior ✅ (skill-level)
- [x] autoguardrails: description conveys the auto pre-commit/CI gate it installs.
- [x] documentation: "Run after every code change" trigger. (PostToolUse hook = per-user settings, documented in skill.)
- [x] git-guardrails: "Applies to every git action" trigger.

# ===== R-merges + R-behavior + R-content + R-systems + README — ALL DONE. =====

## R-content ✅
- [x] AWS/Azure/GCP rewritten to each cloud's philosophy + managed-first (Well-Architected / WAF+CAF / Arch Framework+SRE), with managed-service decision tables + worked reference architectures.
- [x] software-architecture: + cloud architecture + C4/sequence/ER diagrams (Mermaid) + ADR/design-doc outputs.
- [x] NEW soc-siem: Wazuh + Suricata + Grafana for cloud + VMs (detection engineering, MITRE ATT&CK, SOC2 evidence).
- [x] NEW project-context: AGENTS.md/CLAUDE.md + TODO per project; engineering wired.

## R-systems ✅
- [x] config: skillkit.config (layered ~/.config/skills/skills.toml + ./skills.toml); `skill-config`; install.sh seeds it.
- [x] second-brain feed: imbued into the foundation doctrine (opt-out, graceful, agent-decides + asks).
- [x] per-skill README: `skill-readme` generator + README.md in all 45 skills; --check wired into pre-commit + CI + `make ci`.

## README ✅
- [x] root README refreshed to 45 skills / 10 domains / current layout + toolchain.

## Remaining / optional
- [ ] wire project-context reference into the other dev skills (agent-loop, secure-sdlc, tdd, code-review, software-architecture, documentation) — incremental.
- [ ] explicit per-skill "record to second brain" step (beyond the doctrine imbue) — incremental.
- [ ] R-content/R-systems adversarial stress-test round (like the earlier round 1) — optional.

## Notes
- Every SKILL.md must pass `skill-lint --strict`; every cross-link must resolve (`skill-docs`).
- Skills self-contained; references/ carry depth (decision procedure, failure modes, red flags, worked example).
- cavecrew governs non-user-facing subagents; caveman governs terse output.
- Prefer shell scripts over Python where simpler (user directive).
