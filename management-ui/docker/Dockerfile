FROM node:18 AS builder

# This is only for local development.
# Don't include this setting in the docker file for the AppCenter.
ENV VITE__MANAGEMENT_UI__TESTING__ENABLE_TEST_ROUTES=1

COPY management-ui /management-ui
WORKDIR /management-ui
RUN yarn install
RUN yarn build

FROM nginx:1.25.2

ADD https://github.com/jqlang/jq/releases/download/jq-1.7/jq-linux-amd64 /usr/local/bin/jq
RUN chmod +x /usr/local/bin/jq
COPY --from=builder /management-ui/dist /app
COPY management-ui/docker/startup.sh /startup.sh
COPY management-ui/docker/nginx.conf /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/startup.sh"]
STOPSIGNAL SIGQUIT
CMD ["nginx", "-g", "daemon off;"]
