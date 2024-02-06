.PHONY: check-mypy
check-mypy:
	@which mypy > /dev/null || (echo "mypy is not installed, please install it to continue" && false)

.PHONY: check-yapf
check-yapf:
	@which yapf > /dev/null || (echo "yapf is not installed, please install it to continue" && false)

.PHONY: check-flake8
check-flake8:
	@which flake8 > /dev/null || (echo "flake8 is not installed, please install it to continue" && false)

.PHONY: check-isort
check-isort:
	@which isort > /dev/null || (echo "isort is not installed, please install it to continue" && false)

.PHONY: check-bandit
check-bandit:
	@which bandit > /dev/null || (echo "bandit is not installed, please install it to continue" && false)

.PHONY: check-pytest
check-pytest:
	@which pytest > /dev/null || (echo "pytest is not installed, please install it to continue" && false)

.PHONY: check-docker
check-docker:
	@which docker > /dev/null || (echo "Docker is not installed, please install it to continue" && false)

.PHONY: dist
dist: wheel docker

.PHONY: code
code: check format lint sort bandit test

.PHONY: check
check: check-mypy
	mypy pantos/client/cli

.PHONY: format
format: check-yapf
	yapf --in-place --recursive pantos/client/cli tests

.PHONY: lint
lint: check-flake8
	flake8 pantos/client/cli tests

.PHONY: sort
sort: check-isort
	isort --force-single-line-imports pantos/client/cli tests

.PHONY: bandit
bandit: check-bandit
	bandit -r pantos/client/cli tests --quiet --configfile=.bandit

.PHONY: test
test: check-pytest
	python -m pytest tests

.PHONY: coverage
coverage:
	python3 -m pytest --cov-report term-missing --cov=pantos tests
	rm .coverage

.PHONY: wheel
wheel: dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION)-py3-none-any.whl

dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION)-py3-none-any.whl: environment-variables pantos/ pantos-client-cli.conf.$(PANTOS_CLIENT_CLI_ENVIRONMENT) pantos-client-library.conf.$(PANTOS_CLIENT_CLI_ENVIRONMENT) setup.py submodules/client-library/pantos/client/library/ submodules/common/pantos/common/
	cp pantos-client-cli.conf.$(PANTOS_CLIENT_CLI_ENVIRONMENT) pantos/pantos-client-cli.conf
	cp pantos-client-library.conf.$(PANTOS_CLIENT_CLI_ENVIRONMENT) pantos/pantos-client-library.conf
	python3 setup.py bdist_wheel
	rm pantos/pantos-client-cli.conf
	rm pantos/pantos-client-library.conf

.PHONY: docker
docker: check-docker dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker

dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker: environment-variables Dockerfile pantos/ pantos-client-cli.conf.$(PANTOS_CLIENT_CLI_ENVIRONMENT) pantos-client-library.conf.$(PANTOS_CLIENT_CLI_ENVIRONMENT) requirements.txt submodules/client-library/pantos/client/library/ submodules/common/pantos/common/
	docker build -t pantosio/pantos-client --build-arg environment=$(PANTOS_CLIENT_CLI_ENVIRONMENT) .
	mkdir -p dist
	docker save pantosio/pantos-client > dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker

.PHONY: install
install: environment-variables dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION)-py3-none-any.whl
	python3 -m pip install dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	python3 -m pip uninstall -y pantos-client-cli

.PHONY: clean
clean: check-docker
	rm -r -f build/
	rm -r -f dist/
	rm -r -f pantos_client_cli.egg-info/
ifneq ($(shell docker images -q pantosio/pantos-client 2>/dev/null),)
	docker rmi -f pantosio/pantos-client
endif

.PHONY: environment-variables
environment-variables:
ifndef PANTOS_CLIENT_CLI_ENVIRONMENT
	$(error PANTOS_CLIENT_CLI_ENVIRONMENT is undefined)
endif
ifndef PANTOS_CLIENT_CLI_VERSION
	$(error PANTOS_CLIENT_CLI_VERSION is undefined)
endif

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  dist       - Build both the wheel package and the Docker image."
	@echo "  code       - Run checks, formatting, linting, sorting, security analysis, and tests."
	@echo "  check      - Perform type checks on the code."
	@echo "  format     - Format the codebase using yapf."
	@echo "  lint       - Lint the codebase using flake8."
	@echo "  sort       - Sort import statements using isort."
	@echo "  bandit     - Perform security analysis using bandit."
	@echo "  test       - Run tests using pytest."
	@echo "  coverage   - Generate a test coverage report and remove the coverage file."
	@echo "  wheel      - Build a wheel package for the project."
	@echo "  docker     - Build a Docker image for the project."
	@echo "  install    - Install the project using the built wheel package."
	@echo "  uninstall  - Uninstall the project."
	@echo "  clean      - Clean the project by removing build artifacts and Docker images."
	@echo "  help       - Display this help message."
