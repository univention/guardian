# guardian-management-api

The Guardian is the main component of the UCS authorization engine and
contains the management of roles, permissions, etc. (Guardian Management API)
as well as the API for querying policy decisions (Guardian Authorization API).
The Guardian allows to set up complex attribute based access control (ABAC)
and enables the integration with various UCS and third party components.

This chart ships the API to manage objects of the Guardian. This includes
roles, namespaces, apps, permissions, etc.

- **Version**: 0.1.0
- **Type**: application
- **AppVersion**: 1.0.0
-

## Introduction

This chart does install the Guardian Management API as well as its UI.

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://charts.bitnami.com/bitnami | postgresql | ^13.2.24 |
| oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/common-helm/helm | ums-common(common) | ^0.6.0 |

## Values

<table>
	<thead>
		<th>Key</th>
		<th>Type</th>
		<th>Default</th>
		<th>Description</th>
	</thead>
	<tbody>
		<tr>
			<td>affinity</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>autoscaling.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>environment</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>fullnameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterAppPersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterAuthenticationPort</td>
			<td>string</td>
			<td><pre lang="json">
"fast_api_oauth"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterAuthorizationApiUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://guardian-management-api/guardian/authorization"
</pre>
</td>
			<td>URL to the Authorization API.</td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterCapabilityPersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterConditionPersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterContextPersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterNamespacePersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterPermissionPersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterResourceAuthorizationPort</td>
			<td>string</td>
			<td><pre lang="json">
"guardian"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterRolePersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"sql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementAdapterSettingsPort</td>
			<td>string</td>
			<td><pre lang="json">
"env"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementBaseUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://guardian-management"
</pre>
</td>
			<td>Defines the base URL of the API. If unset the url is generated from hostname and domainname.</td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementCorsAllowedOrigins</td>
			<td>string</td>
			<td><pre lang="json">
"*"
</pre>
</td>
			<td>Comma-separated list of hosts that are allowed to make cross-origin resource sharing (CORS) requests to the server.</td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementLoggingFormat</td>
			<td>string</td>
			<td><pre lang="json">
"\u003cgreen\u003e{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}\u003c/green\u003e | \u003clevel\u003e{level}\u003c/level\u003e | \u003clevel\u003e{message}\u003c/level\u003e | {extra}"
</pre>
</td>
			<td>Defines the format of the log output, if not structured. The possible options are described in https://loguru.readthedocs.io/en/stable/api/logger.html.</td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementLoggingLevel</td>
			<td>string</td>
			<td><pre lang="json">
"DEBUG"
</pre>
</td>
			<td>Sets the log level of the application.</td>
		</tr>
		<tr>
			<td>guardianManagementApi.guardianManagementLoggingStructured</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>If set to True, the logging output is structured as a JSON object.</td>
		</tr>
		<tr>
			<td>guardianManagementApi.home</td>
			<td>string</td>
			<td><pre lang="json">
"/guardian_service_dir"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.isUniventionAppCenter</td>
			<td>int</td>
			<td><pre lang="json">
0
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.oauthAdapterM2mSecret</td>
			<td>string</td>
			<td><pre lang="json">
"stub_client_secret"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.oauthAdapterM2mSecretFile</td>
			<td>string</td>
			<td><pre lang="json">
"/var/secrets/oauthAdapterM2mSecret"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.oauthAdapterWellKnownUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://keycloak/realms/souvap/.well-known/openid-configuration"
</pre>
</td>
			<td>Identity Provider well known URL</td>
		</tr>
		<tr>
			<td>guardianManagementApi.sqlPersistenceAdapterDbName</td>
			<td>string</td>
			<td><pre lang="json">
"postgres"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.sqlPersistenceAdapterDialect</td>
			<td>string</td>
			<td><pre lang="json">
"postgresql"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.sqlPersistenceAdapterHost</td>
			<td>string</td>
			<td><pre lang="json">
"db"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.sqlPersistenceAdapterPassword</td>
			<td>string</td>
			<td><pre lang="json">
"stub_password"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.sqlPersistenceAdapterPort</td>
			<td>int</td>
			<td><pre lang="json">
5432
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianManagementApi.sqlPersistenceAdapterUsername</td>
			<td>string</td>
			<td><pre lang="json">
"postgres"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.registry</td>
			<td>string</td>
			<td><pre lang="json">
"docker.software-univention.de"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"guardian-management-api-management-api"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.sha256</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define image sha256 as an alternative to `tag`</td>
		</tr>
		<tr>
			<td>image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"2.0.0"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Set this to `true` in order to enable the installation on Ingress related objects.</td>
		</tr>
		<tr>
			<td>ingress.host</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.ingressClassName</td>
			<td>string</td>
			<td><pre lang="json">
"nginx"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.paths[0].backend.service.name</td>
			<td>string</td>
			<td><pre lang="json">
"guardian-management-api"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.paths[0].backend.service.port.number</td>
			<td>int</td>
			<td><pre lang="json">
8000
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.paths[0].path</td>
			<td>string</td>
			<td><pre lang="json">
"/guardian/management"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.paths[0].pathType</td>
			<td>string</td>
			<td><pre lang="json">
"Prefix"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.tls.secretName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Set this to `true` in order to enable the installation on Istio related objects.</td>
		</tr>
		<tr>
			<td>istio.gateway.annotations</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.externalGatewayName</td>
			<td>string</td>
			<td><pre lang="json">
"swp-istio-gateway"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.selectorIstio</td>
			<td>string</td>
			<td><pre lang="json">
"ingressgateway"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.tls.httpsRedirect</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.tls.secretName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.host</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The hostname. This parameter has to be supplied. Example `portal.example`.</td>
		</tr>
		<tr>
			<td>istio.virtualService.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.virtualService.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.virtualService.paths</td>
			<td>list</td>
			<td><pre lang="json">
[
  {
    "match": "prefix",
    "path": "/guardian/management/",
    "rewrite": "/guardian/management/"
  }
]
</pre>
</td>
			<td>The paths configuration. The default only grabs what is known to be handled by the UMC server.</td>
		</tr>
		<tr>
			<td>nameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nodeSelector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>persistence.data.size</td>
			<td>string</td>
			<td><pre lang="json">
"1Gi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>persistence.data.storageClass</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>postgresql</td>
			<td>object</td>
			<td><pre lang="json">
{
  "auth": {
    "database": "guardian",
    "password": "guardian",
    "postgresPassword": "guardian",
    "username": "guardian"
  },
  "bundled": true,
  "connection": {
    "host": null,
    "port": null
  }
}
</pre>
</td>
			<td>PostgreSQL settings.  The bitnami helm chart does contain all details of what can be configured: https://github.com/bitnami/charts/tree/main/bitnami/postgresql</td>
		</tr>
		<tr>
			<td>postgresql.bundled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Set to `true` if you want PostgreSQL to be installed as well.</td>
		</tr>
		<tr>
			<td>postgresql.connection</td>
			<td>object</td>
			<td><pre lang="json">
{
  "host": null,
  "port": null
}
</pre>
</td>
			<td>Connection parameters. These are required if you use an external database.</td>
		</tr>
		<tr>
			<td>probes.liveness.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
120
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>replicaCount</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Deployment resources for the listener container</td>
		</tr>
		<tr>
			<td>resourcesWaitForDependency</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Deployment resources for the dependency waiters</td>
		</tr>
		<tr>
			<td>securityContext</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.http.containerPort</td>
			<td>int</td>
			<td><pre lang="json">
8000
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.http.port</td>
			<td>int</td>
			<td><pre lang="json">
80
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.http.protocol</td>
			<td>string</td>
			<td><pre lang="json">
"TCP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.sessionAffinity.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.sessionAffinity.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
10800
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.type</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
	</tbody>
</table>

