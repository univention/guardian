# Copyright (C) 2023-2025 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-flex:5.2.3 AS builder

ARG opa_version=1.11.0
ARG opa_checksum=sha256:53451e1d1362dbb11d6703c159b05de5cd18278fa4aee0b75a0b9590d573fd0a

WORKDIR /build

# Download Open Policy Agent
ADD --checksum=${opa_checksum} \
    --chmod=555 \
    --chown=1000:1000 \
    https://github.com/open-policy-agent/opa/releases/download/v${opa_version}/opa_linux_amd64_static \
    /usr/bin/opa

FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base:5.2.3-build.20251128

ARG commit
ARG date
ARG service_user="opa"
ARG service_dir="/var/lib/opa"

LABEL "description"="Guardian OPA service." \
    "release date"="$date" \
    "commit"="$commit"

WORKDIR $service_dir

EXPOSE 8181/tcp

ENV SERVICE_USER $service_user
ENV SERVICE_DIR $service_dir

RUN adduser --no-create-home $service_user && chown $service_user:$service_user $service_dir

# Install OPA
COPY --chmod=555 --chown=$service_user:$service_user --from=builder /usr/bin/opa /usr/bin/opa

COPY --chown=$service_user:$service_user opa_config.yaml $service_dir/opa_config.yaml

USER $service_user
ENTRYPOINT ["/entrypoint.sh"]
CMD ["opa", "run", "--disable-telemetry", "--server", "--v0-compatible", "-c", "opa_config.yaml", "--addr",  "0.0.0.0:8181"]
