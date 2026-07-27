<!--
SPDX-FileCopyrightText: 2026 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
-->

# Reaching the Cerbos endpoint

Read the endpoint from `guardian/cerbos/url`:

```sh
ucr get guardian/cerbos/url        # -> http://cerbos:3592
```

One value covers every deployment target: `cerbos` resolves to the loopback
interface on the host and to the Cerbos container inside the shared `guardian`
Docker network. A native process on the host needs nothing else. HTTP/REST on
`3592` is the standardised endpoint; gRPC on `3593` is enabled but not part of
this contract.

A working example is in
[`../univention-guardian/examples/consumer/`](../univention-guardian/examples/consumer/).

## Docker container on the same UCS host

Join the `guardian` network, or the name will not resolve:

```yaml
# your service's docker-compose.yaml
services:
  my-service:
    environment:
      CERBOS_URL: http://cerbos:3592
    networks:
      - guardian
      - default        # keep your own services reachable
networks:
  guardian:
    external: true
```

`univention-guardian-server.service` creates the network and leaves it in place,
so your service can start while Cerbos is down.

## App Center Docker app

The App Center passes only a fixed set of host UCR variables into an app
container, and `guardian/cerbos/url` is not one of them. Template it into the
app's `env` file instead:

```text
CERBOS_URL=@%@guardian/cerbos/url@%@
```

How the container joins the network depends on the app type:

- **Single container** - no ini setting covers this. Set the docker parameters
  from the app's host-side `preinst`, which runs before the container is created:

  ```sh
  ucr set appcenter/apps/<app-id>/docker/params='--network guardian'
  ```

- **Multi container** - declare the network in the app's `docker-compose.yml` as
  above. Any top-level `networks:` makes the App Center skip its own
  `appcenter_net` and per-service addresses, so the app then owns all of its
  networking.

## Kubernetes pod in N4K

Same `CERBOS_URL`, value supplied by the chart
([guardian#290](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/work_items/290)).

## Name collisions

The static hosts entry makes `cerbos` resolve to the loopback interface on this
machine, shadowing a domain host of that name for local lookups. Override
`guardian/cerbos/url` if that clashes.
