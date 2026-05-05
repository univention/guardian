FROM docker-registry.knut.univention.de/python:3.12-slim@sha256:4386a385d81dba9f72ed72a6fe4237755d7f5440c84b417650f38336bbc43117 AS builder

WORKDIR /build

RUN pip install --upgrade pip

WORKDIR /
FROM docker-registry.knut.univention.de/python:3.12-slim@sha256:4386a385d81dba9f72ed72a6fe4237755d7f5440c84b417650f38336bbc43117

RUN pip install python-keycloak
RUN mkdir -p /keycloak/provisioning
COPY /keycloak/provisioning /keycloak/provisioning

ENTRYPOINT ["python3","/keycloak/provisioning/configure.py"]
