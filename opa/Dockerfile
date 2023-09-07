# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM docker-registry.knut.univention.de/debian:11 as builder

ARG S6_OVERLAY_VERSION="3.1.5.0"
ARG opa_version=0.53.0

WORKDIR /build

# Download and decompress s6
RUN apt-get update -y && apt-get install xz-utils -y
RUN mkdir /_s6
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN ls /tmp/ && tar -C /_s6 -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C /_s6 -Jxpf /tmp/s6-overlay-x86_64.tar.xz

# Download Open Policy Agent
ADD https://github.com/open-policy-agent/opa/releases/download/v${opa_version}/opa_linux_amd64_static /usr/bin/opa
RUN chmod +x /usr/bin/opa


FROM docker-registry.knut.univention.de/debian:11

ARG commit
ARG date
ARG service_user="opa"
ARG service_dir="/var/lib/opa"

LABEL "description"="Guardian OPA service." \
    "release date"="$date" \
    "commit"="$commit"

WORKDIR $service_dir
ENTRYPOINT ["/init"]

EXPOSE 8181/tcp

ENV SERVICE_USER $service_user
ENV SERVICE_DIR $service_dir

RUN adduser --no-create-home $service_user && chown $service_user:$service_user $service_dir

# Install s6
COPY --from=builder /_s6 /
COPY s6-rc.d /etc/s6-overlay/s6-rc.d

# Install OPA
COPY --from=builder /usr/bin/opa /usr/bin/opa

COPY --chown=$service_user:$service_user BaseBundle $service_dir/BaseBundle
COPY --chown=$service_user:$service_user opa_config.yaml $service_dir/opa_config.yaml
