FROM docker.software-univention.de/keycloak-keycloak:25.0.6-ucs2

# Configure a database vendor
ENV KC_DB=dev-file

# relative path needs to be set in build stage
ENV KC_HTTP_RELATIVE_PATH=/guardian/keycloak

# Enable health and metrics support
# This needs to be set before build is called
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

WORKDIR /opt/keycloak
# for demonstration purposes only, please make sure to use proper certificates in production instead
RUN keytool -genkeypair -storepass password -storetype PKCS12 -keyalg RSA -keysize 2048 -dname "CN=server" -alias server -ext "SAN:c=DNS:localhost,IP:127.0.0.1" -keystore conf/server.keystore

# admin credentials
ENV KEYCLOAK_ADMIN=admin
ENV KEYCLOAK_ADMIN_PASSWORD=admin

# configuring keycloak
ENV KC_HOSTNAME=traefik
ENV KC_HTTP_ENABLED=true
ENV KC_PROXY=edge
ENV KC_HOSTNAME_STRICT_HTTPS=false
