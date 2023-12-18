FROM node:18 AS builder

COPY management-ui /management-ui
WORKDIR /management-ui
RUN yarn install
RUN yarn build

FROM nginx:1.25.2

ADD https://github.com/jqlang/jq/releases/download/jq-1.7/jq-linux-amd64 /usr/local/bin/jq
RUN chmod +x /usr/local/bin/jq
COPY --from=builder /management-ui/dist /app
COPY docker/guardian-management-ui/startup.sh /startup.sh
COPY docker/guardian-management-ui/nginx.conf /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/startup.sh"]
STOPSIGNAL SIGQUIT
CMD ["nginx", "-g", "daemon off;"]
