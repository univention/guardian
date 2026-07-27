# Example: a Dockerized Cerbos consumer

A container that discovers the endpoint the way any service should, joins the
shared `guardian` network and asks Cerbos one question.

Run it on a UCS host with `univention-guardian-server` installed:

```bash
export CERBOS_URL="$(ucr get guardian/cerbos/url)"
docker-compose run --rm consumer
```

`request.json` asks whether `alice`, holding the role `user`, may `view` a
`document`. The shipped `policies/examples/base.yaml` allows it:

```json
{"results":[{"resource":{"id":"r-1","kind":"document"},"actions":{"view":"EFFECT_ALLOW"}}],"cerbosCallId":"..."}
```

See [`docs/endpoint-access.md`](../../../docs/endpoint-access.md) for the other
deployment targets.
