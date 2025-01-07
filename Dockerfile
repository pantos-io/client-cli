# SPDX-License-Identifier: GPL-3.0-only
FROM python:3.12-alpine AS build

RUN apk update && apk add gcc libc-dev libffi-dev \
  && apk cache clean

RUN python3 -m pip install 'poetry<2.0.0'

WORKDIR /pantos-cli

COPY . .

RUN poetry build

FROM python:3.12-alpine AS production

WORKDIR /pantos-cli

COPY --from=build /pantos-cli/dist/*.whl .

RUN python3 -m pip install *.whl

RUN pip cache purge && rm -rf ~/.cache/pip

RUN rm *.whl

ENTRYPOINT ["pantos-cli"]
