# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.3-build.20251030@sha256:36f081b5f57553bb1b5d714cca5f4853d985ba09ed03a5f3ef7e0042acc47963

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}
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
  UV_PYTHON=python3.11 \
  UV_PROJECT_ENVIRONMENT=/opt/venv

COPY ./pyproject.toml ./uv.lock /app/
COPY ./authorization-api/pyproject.toml /app/authorization-api/
COPY ./guardian-lib/pyproject.toml /app/guardian-lib/
COPY ./management-api/pyproject.toml /app/management-api/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-install-workspace

ENV PATH=/opt/venv/bin:$PATH \
  PYTHONUNBUFFERED=1
