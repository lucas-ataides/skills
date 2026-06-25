#!/bin/sh
# ataides-skills skill router — a UserPromptSubmit hook.
#
# The problem it solves: Claude Code skills are model-invoked suggestions, and with
# hundreds of installed skills competing, the right one often never fires. This hook is
# deterministic insurance: it lowercases the prompt, matches task keywords, and prints a
# nudge naming the ataides-skills skill(s) to invoke. Plain POSIX sh writing to stdout
# (the Claude Code hook contract) — no interpreter dependency, and it can never break a
# prompt: on any doubt it prints nothing and exits 0.
#
# When a task matches, it also nudges the second-brain prime — pull context on the way in,
# feed the outcome on the way out — so the read/write loop fires deterministically, not only
# when the model remembers the protocol.
#
# It only nudges; the model still chooses, and the user's instructions still win.
# Self-check:  sh skill-router.sh --selftest

set -u

out=""
lc=""

m() { printf '%s' "$lc" | grep -Eq "$1"; }
hit() {
	out="${out}- ataides-skills:$1 — $2
"
}

route() {
	lc=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
	out=""
	m 'pipeline|ci/cd|deploy|terraform|docker|kubernetes|infrastructure|gitlab|github action|implement |build a feature|new endpoint|new api' &&
		hit engineering 'build/change code or infra, test-first, behind the appsec gate'
	m 'commit|pull request|git push|rebase|cherry-pick|open a pr|create a pr' &&
		hit git-guardrails 'safe commits and PRs'
	m 'review this|review the|review my|review our|review that|code review' &&
		hit code-review 'review a diff against the lenses'
	m 'tdd|test-first|unit test|write a test|write tests' &&
		hit tdd 'the test-first loop'
	m 'architecture|system design|design the system|refactor' &&
		hit software-architecture 'judge the design and the seam first'
	m 'agents\.md|claude\.md|onboard|project context|todo list|project brain' &&
		hit project-context 'keep AGENTS.md, the TODO, and the project brain current'
	m 'security review|vulnerability|appsec|owasp|secret scan|threat model' &&
		hit appsec 'the security gate'
	m 'content strategy|content engine|what to post|what should i post|tweet|instagram|tiktok|carousel|viral|trend|caption' &&
		hit content 'the content engine and daily trend radar'
	m 'obsidian|second brain|vault|daily note|capture this' &&
		hit second-brain 'the Obsidian second brain'
	m 'linear|ticket|issue board|next task' &&
		hit linear 'the Linear task workflow'
	printf '%s' "$out"
}

if [ "${1:-}" = "--selftest" ]; then
	fail=0
	expect() {
		echo "$2" | grep -q "ataides-skills:$1" || {
			echo "FAIL: '$3' -> expected $1"
			fail=1
		}
	}
	expect engineering "$(route 'update the deploy pipeline to trunk-based')" "deploy pipeline"
	expect git-guardrails "$(route 'commit this and open a PR')" "commit/PR"
	expect code-review "$(route 'review my diff before I push')" "review"
	expect content "$(route 'what should I post today, any viral trend?')" "post/trend"
	expect second-brain "$(route 'capture this into my obsidian vault')" "obsidian"
	expect linear "$(route 'grab the next linear ticket')" "linear"
	[ -z "$(route 'the weather is nice today')" ] || {
		echo "FAIL: off-topic prompt should not route"
		fail=1
	}
	echo "update the deploy pipeline" | sh "$0" | grep -q "prime from it first" || {
		echo "FAIL: a matched task should also nudge the second-brain prime"
		fail=1
	}
	[ -z "$(echo 'the weather is nice today' | sh "$0")" ] || {
		echo "FAIL: off-topic prompt should stay silent end-to-end (no prime either)"
		fail=1
	}
	[ "$fail" = 0 ] && echo "skill-router selftest: ok" || echo "skill-router selftest: FAIL"
	exit "$fail"
fi

payload=$(cat 2>/dev/null) || exit 0
nudge=$(route "$payload")
if [ -n "$nudge" ]; then
	printf 'ataides-skills router — this task matches installed skills. Invoke the most relevant via the Skill tool before proceeding (the user'\''s own instructions still take precedence):\n%s\n' "$nudge"
	printf -- '- if a second-brain vault is configured, prime from it first via ataides-skills:second-brain (`vault.sh find`), then feed the outcome after.\n'
fi
exit 0
