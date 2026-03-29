# Architecture -- Guardian Lib

**Date:** 2026-03-29
**Version:** 1.8.1
**Type:** Shared Python Library

---

## Executive Summary

Guardian Lib is the shared infrastructure library used by both backend services. It provides the base port interfaces, adapter registry, authentication adapters (OAuth2/JWT), settings adapter (environment variables), and structured logging configuration. It also ships `guardian_pytest`, a test fixture package with pre-built RSA keys and JWT token generators.

---

## Architecture Pattern

**Hexagonal (Ports & Adapters)** -- provides the foundational building blocks.

```text
BasePort (provides .logger)
    ├── SettingsPort (ABC)
    │       └── EnvSettingsAdapter
    └── AuthenticationPort (Generic[RequestObject])
            ├── FastAPIAlwaysAuthorizedAdapter
            ├── FastAPINeverAuthorizedAdapter
            └── FastAPIOAuth2 (production, RS256 JWT validation)
```

---

## Key Components

### Adapter Registry (`adapter_registry.py`)

- `ADAPTER_REGISTRY`: Module-level `lazy_object_proxy.Proxy(AsyncAdapterRegistry)` singleton
- `port_dep(port_cls, adapter_cls)`: FastAPI `Depends()` factory closure
- `initialize_adapters(registry, port_classes)`: Eager initialization at startup

### Ports (`ports.py`)

- `BasePort(ABC)`: Root base with `.logger` property (loguru)
- `SettingsPort(BasePort, AsyncAdapterSettingsProvider, ABC)`: Settings access (str/int/bool only). Setting name format: `[a-zA-Z0-9._-]`, dot separates hierarchy
- `AuthenticationPort(BasePort, Generic[RequestObject])`: `get_actor_identifier(request) -> str` (not abstract, raises `NotImplementedError` by default)

### Authentication Adapters

| Adapter | Alias | Behavior |
|---------|-------|----------|
| `FastAPIAlwaysAuthorizedAdapter` | `fast_api_always_authorized` | No-op, returns `"dev"` as actor |
| `FastAPINeverAuthorizedAdapter` | `fast_api_never_authorized` | Raises 401 unconditionally |
| `FastAPIOAuth2` | `fast_api_oauth` | OIDC well-known discovery, RS256 JWT validation, audience `"guardian"`, actor from `dn` claim |

### Logging (`logging.py`)

- `configure_logger(settings_port?, setting_names?)`: Two-phase init (defaults, then settings)
- `InterceptHandler`: Redirects stdlib logging (uvicorn, fastapi) to loguru
- Configurable: format, level, structured (JSON), backtrace, diagnose

### Test Fixtures (`guardian_pytest/authentication.py`)

- 2 RSA 4096-bit key pairs (correct + wrong key for testing)
- Mock JWKS endpoint via monkeypatch
- Pre-configured `FastAPIOAuth2` adapter fixture
- 7 token fixtures: good, good_wo_dn, bad_idp, expired, bad_audience, bad_signature, wrong_key

---

## Dependencies

Core: `port-loader` 1.2.0 (pinned), `lazy-object-proxy`, `loguru`, `PyJWT`, `FastAPI`, `requests`

---
