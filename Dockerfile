FROM python:3.10-alpine

ARG environment

RUN apk update && apk add gcc libc-dev

WORKDIR /pantos-client

COPY setup.py ./

RUN python -m pip install --no-cache-dir .

RUN mkdir -p ./pantos/client

COPY pantos/__init__.py ./pantos/
COPY pantos/client/__init__.py ./pantos/client/
COPY submodules/common/pantos/common ./pantos/common
COPY submodules/client-library/pantos/client/library ./pantos/client/library
COPY pantos/client/cli ./pantos/client/cli
COPY pantos-client-cli.conf.${environment} ./pantos-client-cli.conf
COPY pantos-client-library.conf.${environment} ./pantos-client-library.conf

ENTRYPOINT ["python", "-m", "pantos.client.cli"]
