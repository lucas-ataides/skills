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

## Wave 4 — documents cluster (documents/) — "extremely beautiful" output
- [ ] pptx · [ ] pdf · [ ] docx · [ ] xlsx

## Wave 5 — cloud cluster (cloud/) — best-practices, SOC2
- [ ] aws-toolkit · [ ] azure-toolkit · [ ] gcp-toolkit · [ ] cloud-best-practices

## Wave 6 — agent-infra ports
- [ ] ralph (loop; relate to app-completion-loop) · [ ] ralph-vault (ralph + obsidian)
- [ ] autoguardrails (global POLICY.md + per-repo; NO extra LLM — pure skill + script)

## Wave 7 — second brain / obsidian (obsidian/) — major, script-backed
- [ ] obsidian-vault (the full compiler spec: orientation, connector gate, _tools scripts, validation gates)
- [ ] second-brain-crud (fast CRUD + correlation into the vault)
- [ ] project-management · [ ] client-satisfaction · [ ] employee-management (feed the vault)

## Wave 8 — social (social/)
- [ ] social-media-viral (IG + X viral research via Chrome; logged-in accounts)

## Wave 9 — impeccable polish pass
- [ ] polish · [ ] overdrive (if not done in Wave 2)

## Final — stress test ALL skills to a Japanese quality bar; fix; repeat until clean
- [ ] adversarial stress-test pass (one critic agent per skill) → fix → re-verify

## Notes
- Every SKILL.md must pass `skill-lint --strict`; every cross-link must resolve (`skill-docs`).
- Skills self-contained; references/ carry depth (decision procedure, failure modes, red flags, worked example).
- cavecrew governs non-user-facing subagents; caveman governs terse output.
- Prefer shell scripts over Python where simpler (user directive).
