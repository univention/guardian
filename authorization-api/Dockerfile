# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

ARG POETRY_VERSION="1.5.1"

# Calculate Python dependencies
FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520:latest as requirements_builder

ARG POETRY_VERSION

WORKDIR /build
RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED
RUN pip install poetry==${POETRY_VERSION}
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --dev --without-hashes

# Live edit version for development
FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520:latest as dev
ARG POETRY_VERSION

EXPOSE 8000
WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "--reload", "--log-level", "debug", "--host", "0.0.0.0", "--port", "8000", "guardian_authorization_api.main:app"]

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED

RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir poetry==${POETRY_VERSION} && poetry config virtualenvs.create false
COPY authorization-api authorization-api
COPY guardian-lib guardian-lib
RUN cd authorization-api && poetry install
RUN cd guardian-lib && poetry install


FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520:latest

EXPOSE 8000

ARG commit
ARG date
ARG service_user="guardian"
ARG service_dir="/guardian_service_dir"

LABEL "description"="Guardian Authorization API." \
    "release date"="$date" \
    "commit"="$commit"

WORKDIR /app

ENV SERVICE_USER $service_user
ENV SERVICE_DIR $service_dir

RUN touch /etc/machine.secret
RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED

RUN adduser --no-create-home $service_user && mkdir -p $service_dir && chown $service_user:$service_user $service_dir

# Install python requirements
COPY --from=requirements_builder /build/requirements.txt .
RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir -r requirements.txt

# Install project
COPY . .
RUN pip install --no-cache-dir . && pip list

USER $service_user
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--log-level", "info", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "guardian_authorization_api.main:app"]
