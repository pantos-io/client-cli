.PHONY: dist
dist: wheel docker

.PHONY: code
code: check format lint sort bandit test

.PHONY: check
check:
	mypy pantos/client/cli

.PHONY: format
format:
	yapf --in-place --recursive pantos/client/cli tests

.PHONY: lint
lint:
	flake8 pantos/client/cli tests

.PHONY: sort
sort:
	isort --force-single-line-imports pantos/client/cli tests

.PHONY: bandit
bandit:
	bandit -r pantos/client/cli tests --quiet --configfile=.bandit

.PHONY: test
test:
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
docker: dist/pantos_client_cli-$(PANTOS_CLIENT_CLI_VERSION).docker

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
clean:
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
