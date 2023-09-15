FROM docker-registry.knut.univention.de/python:3.11-slim as builder

WORKDIR /build

RUN pip install --upgrade pip

WORKDIR /
FROM docker-registry.knut.univention.de/python:3.11-slim

RUN pip install python-keycloak
RUN mkdir -p /keycloak/provisioning
COPY /keycloak/provisioning /keycloak/provisioning

ENTRYPOINT ["python3","/keycloak/provisioning/configure.py"]
