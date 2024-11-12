FROM node:18 AS builder

COPY management-ui /management-ui
WORKDIR /management-ui
RUN yarn install
RUN yarn build

FROM gitregistry.knut.univention.de/univention/customers/dataport/upx/container-nginx/nginx:0.3.0

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
