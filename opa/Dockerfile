# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520:latest AS builder

ARG opa_version=0.53.0

WORKDIR /build

# Download Open Policy Agent
ADD https://github.com/open-policy-agent/opa/releases/download/v${opa_version}/opa_linux_amd64_static /usr/bin/opa
RUN chmod +x /usr/bin/opa


FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520:latest

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
COPY --from=builder /usr/bin/opa /usr/bin/opa

COPY --chown=$service_user:$service_user opa_config.yaml $service_dir/opa_config.yaml

USER $service_user
ENTRYPOINT ["/entrypoint.sh"]
CMD ["opa", "run", "--disable-telemetry", "--server", "-c", "opa_config.yaml", "--addr",  "0.0.0.0:8181"]
