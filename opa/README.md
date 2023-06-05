# Guardian OPA Service

This is the docker container for the Guardian OPA service.
Right now it is very simple and starts the server on port 8181
with the integrated BaseBundle and no way to extend it with external
rego code. This has to be added at a later point.

## Starting the container

```shell
# pwd == $REPO_DIR/authorization-engine/guardian/opa
docker build -t guardian-opa:dev .
docker run --rm -p 8181:8181  guardian-opa:dev
```
