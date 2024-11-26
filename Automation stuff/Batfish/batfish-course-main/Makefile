.DEFAULT_GOAL := help

help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | \
	sort | \
	awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

### Format (Check only) ###

fmt-chk-black:
	@echo "## black (check) ##"
	@$(FMT_LINT_CD_COMMAND) black . --check
	@echo

fmt-chk-autoflake:
	@echo "## autoflake (check) ##"
	@$(FMT_LINT_CD_COMMAND) autoflake -r . --exclude venv --expand-star-imports \
	--remove-unused-variables --remove-all-unused-imports
	@echo

fmt-chk-isort:
	@echo "## isort (check) ##"
	@$(FMT_LINT_CD_COMMAND) isort . -c
	@echo

fmt-chk: ## Format (check)
fmt-chk:   fmt-chk-black fmt-chk-isort fmt-chk-autoflake

### Format ###

fmt-black:
	@echo "## black ##"
	$(FMT_LINT_CD_COMMAND) black .
	@echo

fmt-autoflake:
	@echo "## autoflake ##"
	@$(FMT_LINT_CD_COMMAND) autoflake -vri . --exclude venv --expand-star-imports \
	--remove-unused-variables --remove-all-unused-imports
	@echo

fmt-isort:
	@echo "## isort ##"
	@$(FMT_LINT_CD_COMMAND) isort .
	@echo

fmt: ## Format
fmt:  fmt-black fmt-isort fmt-autoflake

### Linting ###

lint-bandit:
	@echo "## bandit ##"
	@$(FMT_LINT_CD_COMMAND) bandit -r . -c "pyproject.toml"
	@echo

lint-flake8:
	@echo "## flake8 ##"
	@$(FMT_LINT_CD_COMMAND) flake8 .
	@echo

lint-pydoc:
	@echo "## pydocstyle ##"
	@$(FMT_LINT_CD_COMMAND) pydocstyle .
	@echo

lint-yaml:
	@echo "## yamllint ##"
	@$(FMT_LINT_CD_COMMAND) yamllint .
	@echo ""

lint-mypy:
	@echo "## mypy ##"
	@$(FMT_LINT_CD_COMMAND) mypy .
	@echo ""

lint: ## Lint
lint:  lint-bandit lint-flake8 lint-pydoc lint-yaml lint-mypy