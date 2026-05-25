# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.3-build.20251030@sha256:36f081b5f57553bb1b5d714cca5f4853d985ba09ed03a5f3ef7e0042acc47963

ARG DISTROLESS_IMAGE=gcr.io/distroless/python3-debian12
ARG DISTROLESS_IMAGE_TAG=nonroot@sha256:7d1042ce588ab97019fe95c24ffca7bc5a82ccdac572511d5e09bda4435c89c5

# UID/GID of the prebuilt `nonroot` user in the distroless final stage.
ARG GUARDIAN_UID=65532

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]
ARG GUARDIAN_UID

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
  --no-install-workspace && \
  uv export --no-dev -o ./requirements.txt

COPY ./management-api/README.md /app/management-api/
COPY ./management-api/guardian_management_api /app/management-api/guardian_management_api
COPY ./authorization-api/README.md /app/authorization-api/
COPY ./authorization-api/guardian_authorization_api /app/authorization-api/guardian_authorization_api
COPY ./guardian-lib/README.md /app/guardian-lib/
COPY ./guardian-lib/guardian_lib /app/guardian-lib/guardian_lib

RUN uv sync \
  --locked \
  --no-dev \
  --no-editable \
  --all-packages

# Stage the runtime config dir with ownership matching the distroless `nonroot` user.
RUN mkdir -p /staging/app/conf \
  && touch /staging/app/conf/m2m.secret \
  && chown -R ${GUARDIAN_UID}:${GUARDIAN_UID} /staging/app/conf

###############################################
# Stage 2: final image (distroless)
FROM ${DISTROLESS_IMAGE}:${DISTROLESS_IMAGE_TAG} AS final
ARG GUARDIAN_UID

EXPOSE 8000

ARG commit
ARG date

LABEL "description"="Guardian server (management-api, authorization-api, opa)." \
    "release date"="$date" \
    "commit"="$commit"

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/.venv/bin:$PATH \
  SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
  HOME=/app/conf

COPY --from=build --chmod=555 /usr/local/bin/opa /usr/local/bin/opa
COPY --from=build --chown=${GUARDIAN_UID}:${GUARDIAN_UID} /app/.venv /app/.venv
COPY --from=build --chown=${GUARDIAN_UID}:${GUARDIAN_UID} /staging/app/conf /app/conf

COPY --chown=${GUARDIAN_UID}:${GUARDIAN_UID} ./management-api/alembic /app/management-api/alembic
COPY --chown=${GUARDIAN_UID}:${GUARDIAN_UID} ./management-api/alembic.ini /app/management-api/alembic.ini
COPY --chown=${GUARDIAN_UID}:${GUARDIAN_UID} ./management-api/rego_policy_bundle_template /app/management-api/rego_policy_bundle_template
COPY ./opa/opa_config.yaml /etc/opa/opa_config.yaml

USER ${GUARDIAN_UID}
WORKDIR /app/management-api

# Reset the distroless base ENTRYPOINT (which is python3.11) so CMD overrides
# from compose/Helm (gunicorn, opa, ...) execute directly instead of being
# passed to Python as script names.
ENTRYPOINT []
CMD ["gunicorn", "--log-level", "info", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "guardian_management_api.main:app"]

# Smoke test: sets the required env var in-process (no shell available) and imports both apps.
RUN ["python3.11", "-c", "import os; os.environ['GUARDIAN__MANAGEMENT__BASE_URL']='foobar'; import guardian_management_api.main; import guardian_authorization_api.main"]
