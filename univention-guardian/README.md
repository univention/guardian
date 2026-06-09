# univention-cerbos-server — Cerbos PoC

Standalone UCS package that runs [Cerbos](https://docs.cerbos.dev/) as
a policy engine on a UCS primary. Default-off Keycloak OIDC gating via
oauth2-proxy.

> This is a Proof of Concept. The audience for this README is fellow
> developers, not operators. Install + verify steps and known PoC
> limitations live in the MR description; design rationale and
> troubleshooting live in
> [`docs/generated/architecture-cerbos-server.md`](../docs/generated/architecture-cerbos-server.md).

## Authenticating to Cerbos via Keycloak

By default the package leaves Cerbos on `127.0.0.1:3592` with no
authentication. To gate access on a Keycloak bearer:

```sh
sudo univention-app install keycloak       # if not already installed
sudo ucr set cerbos/authentication=true
sudo univention-run-join-scripts --force --run-scripts 90univention-cerbos-server.inst
```

This provisions an OIDC client `cerbos-server` in the `ucs` realm,
writes the JWKS URL / issuer URL / cookie secret into UCR, re-renders
the proxy and Cerbos configs, and restarts the service. The proxy
listens on `0.0.0.0:8593`; Cerbos stays on `127.0.0.1:3592`.

### One-time setup for service-to-service calls

The join script creates the client with `serviceAccountsEnabled: false`
(interactive flows only). To call Cerbos via the `client_credentials`
grant, enable service accounts and grab the client secret:

```sh
sudo univention-keycloak --bindpwdfile /etc/keycloak.secret \
  oidc/rp update cerbos-server '{"serviceAccountsEnabled": true}'

sudo univention-keycloak --bindpwdfile /etc/keycloak.secret \
  oidc/rp get --client-id cerbos-server --all --json \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)[0]["secret"])'
```

### Request a token and call Cerbos

```sh
ISSUER="$(ucr get cerbos/keycloak/issuer-url)"
CLIENT_ID="$(ucr get cerbos/keycloak/client-id)"
CLIENT_SECRET=…  # from the command above

TOKEN=$(curl -s --cacert /etc/univention/ssl/ucsCA/CAcert.pem \
  -X POST "$ISSUER/protocol/openid-connect/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')

curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{
    "requestId": "r1",
    "principal": {"id": "alice", "roles": ["guardian:myapp-admin"]},
    "resources": [{
      "resource": {"id": "x", "kind": "guardian.management_api",
                   "attr": {"app_name": "myapp"}},
      "actions": ["read_resource"]
    }]
  }' http://localhost:8593/api/check/resources
```

Expected: `EFFECT_ALLOW` for `app_name="myapp"`, `EFFECT_DENY` for
`app_name="otherapp"`, **HTTP 401** for any request without (or with
an invalid) bearer.
