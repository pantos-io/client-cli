FROM python:3.12-alpine

ARG environment=testnet
ARG version=1.1.0

ENV PANTOS_CLIENT_VERSION=${version}

RUN apk update && apk add gcc libc-dev libffi-dev

WORKDIR /pantos-cli

COPY pyproject.toml poetry.lock ./

RUN python3 -m pip install poetry

RUN poetry install --only main --no-interaction --no-cache --no-root

RUN mkdir -p ./pantos/cli

COPY pantos/cli ./pantos/cli
COPY client-cli.yml .
COPY client-library.yml .
COPY client-cli.publish.env client-cli.env
COPY client-library.env client-library.env

ENTRYPOINT ["poetry", "run", "python3", "-m", "pantos.cli"]
