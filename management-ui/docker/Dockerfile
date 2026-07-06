# Copyright (C) 2023-2025 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM ${DOCKER_PROXY}node:24 AS builder

COPY management-ui /management-ui
WORKDIR /management-ui
RUN yarn install
RUN yarn build

FROM gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/nginx/nginx:0.7.45@sha256:55b68cde332a3e4abbb70080eccb6fdb60f2377a7750e3e82c096cd60c86d038 AS final

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
