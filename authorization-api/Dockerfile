# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM docker-registry.knut.univention.de/python:3.11-slim as s6_builder

ARG S6_OVERLAY_VERSION="3.1.5.0"
ARG POETRY_VERSION="1.5.1"

WORKDIR /build

# Download and decompress s6
RUN apt-get update -y && apt-get install xz-utils -y
RUN mkdir /_s6
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN ls /tmp/ && tar -C /_s6 -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C /_s6 -Jxpf /tmp/s6-overlay-x86_64.tar.xz

# Calculate Python dependencies
FROM docker-registry.knut.univention.de/python:3.11-slim as requirements_builder
WORKDIR /build
RUN pip install poetry==${POETRY_VERSION}
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --dev --without-hashes

# Live edit version for development
FROM docker-registry.knut.univention.de/python:3.11-slim as dev

EXPOSE 8000
WORKDIR /app
CMD sleep 60 && uvicorn --reload --log-level debug --host 0.0.0.0 --port 8000 guardian_authorization_api.main:app

RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir poetry==1.5.1 && poetry config virtualenvs.create false
COPY authorization-api authorization-api
COPY guardian-lib guardian-lib
RUN cd authorization-api && poetry install
RUN cd guardian-lib && poetry install


FROM docker-registry.knut.univention.de/python:3.11-slim

EXPOSE 8000

ARG commit
ARG date
ARG service_user="guardian"
ARG service_dir="/guardian_service_dir"

LABEL "description"="Guardian Authorization API." \
    "release date"="$date" \
    "commit"="$commit"

WORKDIR /app
ENTRYPOINT ["/init"]

ENV SERVICE_USER $service_user
ENV SERVICE_DIR $service_dir

RUN adduser --no-create-home $service_user && mkdir -p $service_dir && chown $service_user:$service_user $service_dir

# Install s6
COPY --from=s6_builder /_s6 /
COPY s6-rc.d /etc/s6-overlay/s6-rc.d

# Install python requirements
COPY --from=requirements_builder /build/requirements.txt .
RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir -r requirements.txt

# Install project
COPY . .
RUN pip install --no-cache-dir . && pip list
