FROM python:3.12-alpine AS build

RUN apk update && apk add gcc libc-dev libffi-dev \
  && apk cache clean

RUN python3 -m pip install poetry

WORKDIR /pantos-cli

COPY . .

RUN poetry build

FROM python:3.12-alpine AS production

WORKDIR /pantos-cli

COPY --from=build /pantos-cli/dist/*.whl .

RUN python3 -m pip install *.whl

ENTRYPOINT ["pantos-cli"]
