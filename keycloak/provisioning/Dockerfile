FROM quay.io/keycloak/keycloak:latest as builder
# COPY --from=builder /opt/keycloak/ /opt/keycloak/
COPY /keycloak/provisioning/configure.sh /configure.sh
ENTRYPOINT ["/bin/bash","configure.sh"]