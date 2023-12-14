# guardian-authorization

The Guardian is the main component of the UCS authorization engine and
contains the management of roles, permissions, etc. (Guardian Management API)
as well as the API for querying policy decisions (Guardian Authorization API).
The Guardian allows to set up complex attribute based access control (ABAC)
and enables the integration with various UCS and third party components.

This chart ships the API to query for policy decisions, as well as the Open
Policy Agent, on which it relies.

- **Version**: 0.1.0
- **Type**: application
- **AppVersion**: 0.0.1
-

## Introduction

This chart does install the Guardian Authorization API as well as the Open Policy
Agent as a sidecar.

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/common-helm/helm | common | ^0.2.0 |

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
			<td>guardianAuthorizationApi.guardianAuthzAdapterAppPersistencePort</td>
			<td>string</td>
			<td><pre lang="json">
"udm_data"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzAdapterPolicyPort</td>
			<td>string</td>
			<td><pre lang="json">
"opa"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzAdapterSettingsPort</td>
			<td>string</td>
			<td><pre lang="json">
"env"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzAdapteriAuthenticationPort</td>
			<td>string</td>
			<td><pre lang="json">
"fast_api_oauth"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzCorsAllowedOrigins</td>
			<td>string</td>
			<td><pre lang="json">
"*"
</pre>
</td>
			<td>Comma-separated list of hosts that are allowed to make cross-origin resource sharing (CORS) requests to the server.</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzLoggingFormat</td>
			<td>string</td>
			<td><pre lang="json">
"\u003cgreen\u003e{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}\u003c/green\u003e | \u003clevel\u003e{level}\u003c/level\u003e | \u003clevel\u003e{message}\u003c/level\u003e | {extra}"
</pre>
</td>
			<td>Defines the format of the log output, if not structured. The possible options are described in https://loguru.readthedocs.io/en/stable/api/logger.html.</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzLoggingLevel</td>
			<td>string</td>
			<td><pre lang="json">
"DEBUG"
</pre>
</td>
			<td>Sets the log level of the application.</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.guardianAuthzLoggingStructured</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>If set to True, the logging output is structured as a JSON object.</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.home</td>
			<td>string</td>
			<td><pre lang="json">
"/guardian_service_dir"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.isUniventionAppCenter</td>
			<td>int</td>
			<td><pre lang="json">
0
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.oauthAdapterWellKnownUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://keycloak/realms/souvap/.well-known/openid-configuration"
</pre>
</td>
			<td>OIDC well-known url</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.opaAdapterUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://guardian-authorization-opa:8181/"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.udmDataAdapterPassword</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Password for authenticating against the UDM REST API</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.udmDataAdapterUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://udm-rest-api/univention/udm"
</pre>
</td>
			<td>The URL of the UDM REST API for data queries.</td>
		</tr>
		<tr>
			<td>guardianAuthorizationApi.udmDataAdapterUsername</td>
			<td>string</td>
			<td><pre lang="json">
"admin"
</pre>
</td>
			<td>Username for authenticating against the UDM REST API</td>
		</tr>
		<tr>
			<td>image.guardianAuthorizationApi.registry</td>
			<td>string</td>
			<td><pre lang="json">
"docker.software-univention.de"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.guardianAuthorizationApi.repository</td>
			<td>string</td>
			<td><pre lang="json">
"guardian-authorization-api-authorization-api"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.guardianAuthorizationApi.sha256</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define image sha256 as an alternative to `tag`</td>
		</tr>
		<tr>
			<td>image.guardianAuthorizationApi.tag</td>
			<td>string</td>
			<td><pre lang="json">
"1.0.0"
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
			<td>image.openPolicyAgent.registry</td>
			<td>string</td>
			<td><pre lang="json">
"docker.software-univention.de"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.openPolicyAgent.repository</td>
			<td>string</td>
			<td><pre lang="json">
"guardian-authorization-api-opa"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.openPolicyAgent.sha256</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define image sha256 as an alternative to `tag`</td>
		</tr>
		<tr>
			<td>image.openPolicyAgent.tag</td>
			<td>string</td>
			<td><pre lang="json">
"1.0.0"
</pre>
</td>
			<td></td>
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
			<td>openPolicyAgent.isUniventionAppCenter</td>
			<td>int</td>
			<td><pre lang="json">
0
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>openPolicyAgent.opaDataBundle</td>
			<td>string</td>
			<td><pre lang="json">
"bundles/GuardianDataBundle.tar.gz"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>openPolicyAgent.opaGuardianManagementUrl</td>
			<td>string</td>
			<td><pre lang="json">
"http://guardian-management-api/guardian/management"
</pre>
</td>
			<td>Bundle server URL</td>
		</tr>
		<tr>
			<td>openPolicyAgent.opaPolicyBundle</td>
			<td>string</td>
			<td><pre lang="json">
"bundles/GuardianPolicyBundle.tar.gz"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>openPolicyAgent.opaPollingMaxDelay</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>openPolicyAgent.opaPollingMinDelay</td>
			<td>int</td>
			<td><pre lang="json">
10
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
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
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

