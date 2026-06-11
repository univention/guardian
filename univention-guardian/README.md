# univention-guardian-server - Cerbos PoC

Standalone UCS package that runs [Cerbos](https://docs.cerbos.dev/) as
a local policy (PDP) engine on a UCS Server, reachable on `127.0.0.1:3593` (gRPC).

> This is a Proof of Concept. The audience for this README is fellow
> developers, not operators.
> Design rationale and troubleshooting live in
> [`docs/generated/architecture-cerbos-server.md`](../docs/generated/architecture-cerbos-server.md).

## Current limitations

- No authentication
- Not exposed outside the Server, only reachable on `localhost`
- No policy distribution across the UCS domain.
This will be handled in
[#288](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/work_items/288).

## Installation

The debian package can be installed on all UCS server roles.

```bash
echo 'deb [trusted=yes] http://omar.knut.univention.de/build2/git/guardian cerbos main' | sudo tee /etc/apt/sources.list.d/guardian-cerbos-poc.list
sudo apt update
sudo apt install univention-guardian-server
```

## Integrate your own policies

The package ships its builtin policies under `policies/default/` and
examples under `policies/examples/`. To add your own, copy your Cerbos
policy files into a *separate*, per-app subdirectory:

```bash
/usr/share/univention-guardian-server/policies/<app-name>/<policy-name>.yaml
```

This manual step is only necessary until we've implemented [policy distribution across the UCS domain](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/work_items/291)

## UCR variables this package owns

| Variable | Default | Notes |
|---|---|---|
| `guardian/cerbos/log-level` | `WARN` | One of `DEBUG`, `INFO`, `WARN`, `ERROR`. Change with `ucr set` then `systemctl restart univention-guardian-server.service`. |

## Tests

```sh
sudo systemctl is-active univention-guardian-server.service    # active
sudo docker ps                                           # guardian-cerbos healthy
```

Manually run the initial set of integration tests:

1. Copy the `univention-guardian-test` directory to the UCS VM
2. Install pytest & cerbos: `apt install python3-pip && pip install cerbos pytest --break-system-packages`
3. Run the tests `pytest univention-guardian-test`
