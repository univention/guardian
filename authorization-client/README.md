# Guardian Authorization Client

A Python client library for the Guardian authorization and management APIs.

## Installation

```bash
pip install guardian-authorization-client
```

Or with Poetry:

```bash
poetry add guardian-authorization-client
```

## Usage

### Authorization Client

```python
from guardian_authorization_client import GuardianAuthorizationClient

# Create a client (uses HTTPS by default)
client = GuardianAuthorizationClient(
    fqdn="guardian.example.com",
    keycloak_fqdn="keycloak.example.com",
    username="admin",
    password="secret",
    realm="ucs"
)

# Create a client with HTTP (e.g., for local development)
client = GuardianAuthorizationClient(
    fqdn="localhost:8000",
    keycloak_fqdn="localhost:8080",
    username="admin",
    password="secret",
    realm="ucs",
    scheme="http"  # Uses HTTP for both Guardian and Keycloak
)

# Use different schemes for Guardian and Keycloak
client = GuardianAuthorizationClient(
    fqdn="guardian.example.com",
    keycloak_fqdn="localhost:8080",
    username="admin",
    password="secret",
    realm="ucs",
    scheme="https",           # HTTPS for Guardian
    keycloak_scheme="http"    # HTTP for Keycloak
)

# Check permissions
result = client.check_permissions(
    actor={"id": "user-123", "roles": ["app:namespace:role"], "attributes": {}},
    targets=[{"old_target": None, "new_target": {"id": "target-456", "attributes": {}, "roles": []}}],
    contexts=None,
    namespaces=["app:namespace"],
    targeted_permissions_to_check=["app:namespace:read"]
)
```

### Local Authorization Client

For offline/local authorization using JSON capability files:

```python
from guardian_authorization_client import LocalGuardianAuthorizationClient

client = LocalGuardianAuthorizationClient(base_path="/path/to/capabilities")
result = client.check_permissions(...)
```

### Management Client

```python
from guardian_authorization_client import GuardianManagementClient

client = GuardianManagementClient(
    management_url="https://guardian.example.com/guardian/management",
    username="admin",
    password="secret",
    oidc_token_endpoint_url="https://keycloak.example.com/realms/ucs/protocol/openid-connect/token",
    oidc_client_id="guardian-scripts"
)

# Create resources
client.create_app("my-app", "My Application")
client.create_namespace("my-app", "default", "Default Namespace")
client.create_role("my-app", "default", "admin", "Administrator")
client.create_permission("my-app", "default", "read", "Read Permission")
```
