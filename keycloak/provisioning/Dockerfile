FROM docker-registry.knut.univention.de/python:3.11-slim@sha256:16cb75beff0e104520a4bc4e98b08987b6978b82e37b81b87d786504e17579e7 AS builder

WORKDIR /build

RUN pip install --upgrade pip

WORKDIR /
FROM docker-registry.knut.univention.de/python:3.11-slim@sha256:16cb75beff0e104520a4bc4e98b08987b6978b82e37b81b87d786504e17579e7

RUN pip install python-keycloak
RUN mkdir -p /keycloak/provisioning
COPY /keycloak/provisioning /keycloak/provisioning

ENTRYPOINT ["python3","/keycloak/provisioning/configure.py"]
