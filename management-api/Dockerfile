# Copyright (C) 2023-2025 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-flex:5.2.4 AS builder

ARG opa_version=1.11.0
ARG opa_checksum=sha256:53451e1d1362dbb11d6703c159b05de5cd18278fa4aee0b75a0b9590d573fd0a

WORKDIR /build

# Download Open Policy Agent
ADD --checksum=${opa_checksum} \
    --chmod=555 \
    --chown=1000:1000 \
    https://github.com/open-policy-agent/opa/releases/download/v${opa_version}/opa_linux_amd64_static \
    /usr/bin/opa

# Calculate Python dependencies
FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base:5.2.4-build.20260108 AS requirements_builder
WORKDIR /build
RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED
RUN pip install poetry==2.2.1 poetry-plugin-export==1.9.0
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes

# Live edit version for development
FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base:5.2.4-build.20260108 AS dev

ARG service_dir="/guardian_service_dir"

EXPOSE 8000
WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "--reload", "--log-level", "debug", "--host", "0.0.0.0", "--port", "8000", "guardian_management_api.main:app"]
#CMD uvicorn --reload --log-level debug --host 0.0.0.0 --port 8000 guardian_management_api.main:app

ENV SERVICE_DIR $service_dir

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED

# Install OPA
COPY --chmod=555 --from=builder /usr/bin/opa /usr/bin/opa

RUN mkdir -p $service_dir
RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir poetry==2.2.1 poetry-plugin-export==1.9.0 && poetry config virtualenvs.create false
COPY management-api management-api
COPY guardian-lib guardian-lib
RUN cd management-api && poetry install && cd ..
RUN cd guardian-lib && poetry install && cd ..


FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base:5.2.4-build.20260108

EXPOSE 8000

ARG commit
ARG date
ARG service_user="guardian"
ARG service_dir="/guardian_service_dir"

LABEL "description"="Guardian Management API." \
    "release date"="$date" \
    "commit"="$commit"

WORKDIR /app/management-api

ENV SERVICE_USER $service_user
ENV SERVICE_DIR $service_dir

RUN mkdir -p /guardian_service_dir/conf; touch /guardian_service_dir/conf/m2m.secret
RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED
RUN adduser --no-create-home $service_user && mkdir -p $service_dir && chown $service_user:$service_user $service_dir

# Install OPA
COPY --chmod=555 --chown=$service_user:$service_user --from=builder /usr/bin/opa /usr/bin/opa

# Install python requirements
COPY --from=requirements_builder /build/requirements.txt .
RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir -r requirements.txt

# Install project
COPY . .
RUN pip install --no-cache-dir . && pip list
RUN mkdir -p /guardian_service_dir/conf && touch /guardian_service_dir/conf/m2m.secret

USER $service_user
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--log-level", "info", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "guardian_management_api.main:app"]
