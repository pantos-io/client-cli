PANTOS_CLIENT_CLI_VERSION := $(shell poetry version -s)
PYTHON_FILES := pantos/cli tests

.PHONY: dist
dist: wheel docker

.PHONY: build
build:
	poetry build

.PHONY: code
code: check format lint sort bandit test

.PHONY: check
check:
	poetry run mypy $(PYTHON_FILES)

.PHONY: format
format:
	poetry run yapf --in-place --recursive $(PYTHON_FILES)

.PHONY: format-check
format-check:
	poetry run yapf --diff --recursive $(PYTHON_FILES)

.PHONY: lint
lint:
	poetry run flake8 $(PYTHON_FILES)

.PHONY: sort
sort:
	poetry run isort --force-single-line-imports $(PYTHON_FILES)

.PHONY: sort-check
sort-check:
	poetry run isort --force-single-line-imports $(PYTHON_FILES) --check-only

.PHONY: bandit
bandit:
	poetry run bandit -r $(PYTHON_FILES) --quiet --configfile=.bandit

.PHONY: bandit-check
bandit-check:
	poetry run bandit -r $(PYTHON_FILES) --configfile=.bandit

.PHONY: test
test:
	poetry run python3 -m pytest tests

.PHONY: coverage
coverage:
	poetry run python3 -m pytest --cov-report term-missing --cov=pantos tests

.PHONY: wheel
wheel:
	poetry build

.PHONY: docker
docker: dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker

dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker: Dockerfile pantos/ client-cli.yml client-library.yml client-library.publish.env submodules/client-library/pantos/client/library/ pyproject.toml submodules/common/pantos/common/
	docker build -t pantosio/pantos-client .
	mkdir -p dist
	docker save pantosio/pantos-client > dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker

.PHONY: install
install: dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION)-py3-none-any.whl
	poetry run python3 -m pip install dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	poetry run python3 -m pip uninstall -y pantos-client-cli

.PHONY: clean
clean:
	rm -r -f build/
	rm -r -f dist/
	rm -r -f pantos_client_cli.egg-info/
ifneq ($(shell docker images -q pantosio/pantos-client 2>/dev/null),)
	docker rmi -f pantosio/pantos-client
endif
