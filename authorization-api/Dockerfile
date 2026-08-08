# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.6-build.20260706@sha256:d6ef961a4a8f0b603540b06661c058d1e25da0c65273db5fd98fc202a4649fd1

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.12.3@sha256:2d890623d310b57771ce840f0da5eed5fc6d657da05ffaa45d82797b53fa3abc /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.11

COPY ./pyproject.toml ./uv.lock /app/
COPY ./authorization-api/pyproject.toml /app/authorization-api/
COPY ./guardian-lib/pyproject.toml /app/guardian-lib/
COPY ./management-api/pyproject.toml /app/management-api/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-dev \
  --no-install-workspace \
  --package authorization-api && \
  uv export --no-dev -o ./requirements.txt

COPY ./authorization-api/README.md /app/authorization-api/
COPY ./authorization-api/guardian_authorization_api /app/authorization-api/guardian_authorization_api
COPY ./guardian-lib/README.md /app/guardian-lib/
COPY ./guardian-lib/guardian_lib /app/guardian-lib/guardian_lib

RUN uv sync \
  --locked \
  --no-dev \
  --no-editable \
  --package authorization-api

###############################################
# Stage 2: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

EXPOSE 8000

ARG commit
ARG date
ARG USER=guardian

LABEL "description"="Guardian Authorization API." \
    "release date"="$date" \
    "commit"="$commit"

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/.venv/bin:$PATH \
  SERVICE_USER=${USER}

RUN apt-get --assume-yes --verbose-versions --no-install-recommends install \
  ca-certificates \
  && rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
  && touch /etc/machine.secret \
  && groupadd -r ${USER} -g 1000 \
  && useradd -r -d /app -g ${USER} -N ${USER} -u 1000 \
  && mkdir -p /guardian_service_dir/conf \
  && touch /guardian_service_dir/conf/machine.secret \
  && touch /guardian_service_dir/conf/machine.user

COPY --from=build --chown=${USER}:${USER} /app/.venv /app/.venv

USER ${USER}
WORKDIR /app/authorization-api

CMD ["gunicorn", "--log-level", "info", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "guardian_authorization_api.main:app"]

RUN \
  python3.11 -V && \
  python3.11 -m site && \
  python3.11 -c 'import guardian_authorization_api.main'
