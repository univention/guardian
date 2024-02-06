# Copyright (C) 2024 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520:latest
LABEL description="Development image for the Guardian"

RUN apt-get update && \
    apt-get install -y sudo git python3-pip nodejs npm && \
    npm install --global yarn && \
    rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
    pip install poetry==1.5.1 pre-commit==3.6.0 reuse==3.0.1
ADD --chmod=755 https://github.com/open-policy-agent/opa/releases/download/v0.53.0/opa_linux_amd64_static /bin/opa
ADD --chmod=755 https://github.com/StyraInc/regal/releases/download/v0.8.0/regal_Linux_x86_64 /bin/regal
ENV PROJECT_DIR "/src"
ENV PYTHONPYCACHEPREFIX $PROJECT_DIR/.cache/cpython
ENV POETRY_CACHE_DIR $PROJECT_DIR/.cache/pypoetry
ENV PRE_COMMIT_HOME $PROJECT_DIR/.cache/pre-commit-home
ENV YARN_CACHE_FOLDER $PROJECT_DIR/.cache/yarn
ENV npm_config_cache $PROJECT_DIR/.cache/npm
WORKDIR $PROJECT_DIR
