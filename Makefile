# ldatb/skills — deterministic toolchain entrypoints.
# Every target is reproducible: same input, same result. No hidden state.
# Requires uv (https://docs.astral.sh/uv/). uv owns the venv and the lockfile.

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Sync the toolchain + dev deps and install pre-commit hooks.
	uv sync --extra dev
	uv run pre-commit install

.PHONY: lint
lint: ## Run skill-lint (strict) on every skill. Blocks on any violation.
	uv run skill-lint --strict skills/

.PHONY: lint-fix
lint-fix: ## Apply skill-lint's deterministic autofixes (frontmatter normalization).
	uv run skill-lint --fix skills/

.PHONY: docs
docs: ## Check that every Markdown link and file reference resolves.
	uv run skill-docs .

.PHONY: readme
readme: ## Regenerate the per-skill README.md files from each SKILL.md.
	uv run skill-readme skills/

.PHONY: test
test: ## Run the toolchain test suite.
	uv run pytest

.PHONY: format
format: ## Format + autofix Python tooling with ruff.
	uv run ruff check --fix tools/
	uv run ruff format tools/

.PHONY: sca
sca: ## Static analysis on the toolchain (Semgrep). Blocks on findings.
	uv run semgrep scan --error --quiet --config semgrep.yml --config p/python --config p/secrets tools/

.PHONY: new-skill
new-skill: ## Scaffold a conformant skill. Usage: make new-skill CATEGORY=engineering NAME=my-skill
	uv run skill-new --category "$(CATEGORY)" --name "$(NAME)"

.PHONY: ci
ci: lint docs test sca ## Everything CI runs, locally. Green here == green there.
	uv run ruff check tools/
	uv run skill-readme --check skills/
