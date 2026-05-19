# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.3-build.20251030@sha256:36f081b5f57553bb1b5d714cca5f4853d985ba09ed03a5f3ef7e0042acc47963

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ARG opa_version=1.11.0
ARG opa_checksum=sha256:53451e1d1362dbb11d6703c159b05de5cd18278fa4aee0b75a0b9590d573fd0a

ADD --checksum=${opa_checksum} \
    --chmod=555 \
    https://github.com/open-policy-agent/opa/releases/download/v${opa_version}/opa_linux_amd64_static \
    /usr/local/bin/opa

COPY --from=ghcr.io/astral-sh/uv:0.11.14@sha256:1025398289b62de8269e70c45b91ffa37c373f38118d7da036fb8bb8efc85d97 /uv /usr/local/bin/uv

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
  --package management-api && \
  uv export --no-dev -o ./requirements.txt

COPY ./management-api/README.md /app/management-api/
COPY ./management-api/guardian_management_api /app/management-api/guardian_management_api
COPY ./guardian-lib/README.md /app/guardian-lib/
COPY ./guardian-lib/guardian_lib /app/guardian-lib/guardian_lib

RUN uv sync \
  --locked \
  --no-dev \
  --no-editable \
  --package management-api

###############################################
# Stage 2: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

EXPOSE 8000

ARG commit
ARG date
ARG USER=guardian

LABEL "description"="Guardian Management API." \
    "release date"="$date" \
    "commit"="$commit"

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/.venv/bin:$PATH \
  SERVICE_USER=${USER}

RUN apt-get --assume-yes --verbose-versions --no-install-recommends install \
  ca-certificates \
  && rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
  && groupadd -r ${USER} -g 1000 \
  && useradd -r -d /app -g ${USER} -N ${USER} -u 1000 \
  && mkdir -p /guardian_service_dir/conf \
  && touch /guardian_service_dir/conf/m2m.secret

COPY --from=build --chmod=555 /usr/local/bin/opa /usr/local/bin/opa
COPY --from=build --chown=${USER}:${USER} /app/.venv /app/.venv

COPY --chown=${USER}:${USER} ./management-api/alembic /app/management-api/alembic
COPY --chown=${USER}:${USER} ./management-api/alembic.ini /app/management-api/alembic.ini
COPY --chown=${USER}:${USER} ./management-api/rego_policy_bundle_template /app/management-api/rego_policy_bundle_template

USER ${USER}
WORKDIR /app/management-api

CMD ["gunicorn", "--log-level", "info", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "guardian_management_api.main:app"]

RUN \
  python3.11 -V && \
  python3.11 -m site && \
  GUARDIAN__MANAGEMENT__BASE_URL="foobar" \
  python3.11 -c 'import guardian_management_api.main'
