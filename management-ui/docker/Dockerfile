# Copyright (C) 2023-2025 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM ${DOCKER_PROXY}node:24 AS builder

COPY management-ui /management-ui
WORKDIR /management-ui
RUN yarn install
RUN yarn build

FROM gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/nginx/nginx:0.7.42@sha256:bf6fae0e812d7aae9be61ef1a42bdbd1ed6e8f49f0ceb90ce5e6cab9184ca300 AS final

EXPOSE 8080

ARG commit
ARG date

LABEL "description"="Guardian Management UI." \
    "release date"="$date" \
    "commit"="$commit"

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    jq \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*
COPY --from=builder /management-ui/dist /app
COPY management-ui/docker/01-generate_config.sh /entrypoint.d/01-generate_config.sh
COPY management-ui/docker/nginx.conf /etc/nginx/sites-enabled/default

FROM final AS sbom

COPY ./sbom-fs-management-ui.cdx.json /
