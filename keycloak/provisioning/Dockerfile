FROM docker-registry.knut.univention.de/python:3.12-slim@sha256:0bbd3d5f3abb2024c1b92ce69e8bdfefa17c248999827c34e2ed52ba0772da1b AS builder

WORKDIR /build

RUN pip install --upgrade pip

WORKDIR /
FROM docker-registry.knut.univention.de/python:3.12-slim@sha256:0bbd3d5f3abb2024c1b92ce69e8bdfefa17c248999827c34e2ed52ba0772da1b

RUN pip install python-keycloak
RUN mkdir -p /keycloak/provisioning
COPY /keycloak/provisioning /keycloak/provisioning

ENTRYPOINT ["python3","/keycloak/provisioning/configure.py"]
