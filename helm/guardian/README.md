# guardian

A Helm chart for the Nubus Guardian component

- **Type**: application
- **AppVersion**: 0.55.0
-

## Introduction

This chart deploys Cerbos as the Guardian policy engine.

Other pods reach the decision API at
`http://<release>-guardian:3592` (HTTP)
and `<release>-guardian:3593` (gRPC).

The chart ships no policies of its own, and Cerbos denies by default.
[`docs/kubernetes-policies.md`](../../docs/kubernetes-policies.md)
lists every way a policy set reaches the container.

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus/charts | nubus-common | 0.29.19 |

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
			<td>additionalAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>additionalLabels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>affinity</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Affinity for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity</td>
		</tr>
		<tr>
			<td>cerbos</td>
			<td>object</td>
			<td><pre lang="json">
{
  "config": {
    "schema": {
      "enforcement": "reject"
    },
    "server": {
      "apiExplorerEnabled": false,
      "playgroundEnabled": false,
      "requestLimits": {
        "maxActionsPerResource": 500,
        "maxResourcesPerRequest": 500
      }
    },
    "telemetry": {
      "disabled": true
    }
  },
  "image": {
    "pullPolicy": null,
    "registry": "",
    "repository": "nubus/images/cerbos",
    "tag": "0.55.0@sha256:4b9d3b58c4f11c1b8953bc798d8d086e64f276882253ab169625fddc7f432515"
  },
  "logLevel": "WARN",
  "policies": {},
  "policyValidation": {
    "enabled": true
  }
}
</pre>
</td>
			<td>Cerbos policy engine configuration.</td>
		</tr>
		<tr>
			<td>cerbos.config</td>
			<td>object</td>
			<td><pre lang="json">
{
  "schema": {
    "enforcement": "reject"
  },
  "server": {
    "apiExplorerEnabled": false,
    "playgroundEnabled": false,
    "requestLimits": {
      "maxActionsPerResource": 500,
      "maxResourcesPerRequest": 500
    }
  },
  "telemetry": {
    "disabled": true
  }
}
</pre>
</td>
			<td>Cerbos server configuration, written verbatim to `/config/cerbos.yaml`. Anything Cerbos accepts can be set here; Helm merges overrides key by key. `storage` is the exception: the chart owns and hard-codes it.  Ref: https://docs.cerbos.dev/cerbos/latest/configuration/index.html</td>
		</tr>
		<tr>
			<td>cerbos.config.schema</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enforcement": "reject"
}
</pre>
</td>
			<td>Cerbos schema block. Ref: https://docs.cerbos.dev/cerbos/latest/configuration/schema</td>
		</tr>
		<tr>
			<td>cerbos.config.schema.enforcement</td>
			<td>string</td>
			<td><pre lang="json">
"reject"
</pre>
</td>
			<td>What a request that violates an attribute schema does, one of "none", "warn" or "reject".</td>
		</tr>
		<tr>
			<td>cerbos.config.server</td>
			<td>object</td>
			<td><pre lang="json">
{
  "apiExplorerEnabled": false,
  "playgroundEnabled": false,
  "requestLimits": {
    "maxActionsPerResource": 500,
    "maxResourcesPerRequest": 500
  }
}
</pre>
</td>
			<td>Cerbos server block. Ref: https://docs.cerbos.dev/cerbos/latest/configuration/server</td>
		</tr>
		<tr>
			<td>cerbos.config.server.apiExplorerEnabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Serve the interactive API explorer. Off: it is a documentation UI on an endpoint that answers authorization questions.</td>
		</tr>
		<tr>
			<td>cerbos.config.server.playgroundEnabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Serve the policy playground from the server. Off: it evaluates arbitrary policies supplied by the caller.</td>
		</tr>
		<tr>
			<td>cerbos.config.server.requestLimits</td>
			<td>object</td>
			<td><pre lang="json">
{
  "maxActionsPerResource": 500,
  "maxResourcesPerRequest": 500
}
</pre>
</td>
			<td>Ceilings on a single check request, so one caller cannot ask for an unbounded amount of evaluation.</td>
		</tr>
		<tr>
			<td>cerbos.config.server.requestLimits.maxActionsPerResource</td>
			<td>int</td>
			<td><pre lang="json">
500
</pre>
</td>
			<td>Maximum actions asked about per resource.</td>
		</tr>
		<tr>
			<td>cerbos.config.server.requestLimits.maxResourcesPerRequest</td>
			<td>int</td>
			<td><pre lang="json">
500
</pre>
</td>
			<td>Maximum resources asked about per request.</td>
		</tr>
		<tr>
			<td>cerbos.config.telemetry</td>
			<td>object</td>
			<td><pre lang="json">
{
  "disabled": true
}
</pre>
</td>
			<td>Cerbos telemetry block.</td>
		</tr>
		<tr>
			<td>cerbos.config.telemetry.disabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Report anonymous usage statistics upstream.</td>
		</tr>
		<tr>
			<td>cerbos.image</td>
			<td>object</td>
			<td><pre lang="json">
{
  "pullPolicy": null,
  "registry": "",
  "repository": "nubus/images/cerbos",
  "tag": "0.55.0@sha256:4b9d3b58c4f11c1b8953bc798d8d086e64f276882253ab169625fddc7f432515"
}
</pre>
</td>
			<td>Container image section.</td>
		</tr>
		<tr>
			<td>cerbos.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. Higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>cerbos.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Container registry address. Higher precedence than global.imageRegistry.</td>
		</tr>
		<tr>
			<td>cerbos.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus/images/cerbos"
</pre>
</td>
			<td>Container image repository.</td>
		</tr>
		<tr>
			<td>cerbos.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"0.55.0@sha256:4b9d3b58c4f11c1b8953bc798d8d086e64f276882253ab169625fddc7f432515"
</pre>
</td>
			<td>Container image tag.</td>
		</tr>
		<tr>
			<td>cerbos.logLevel</td>
			<td>string</td>
			<td><pre lang="json">
"WARN"
</pre>
</td>
			<td>Cerbos log level: one of DEBUG, INFO, WARN, ERROR. A command line flag, not part of the server configuration file.</td>
		</tr>
		<tr>
			<td>cerbos.policies</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Policies supplied through this chart, one file per key, mounted at `/policies/chart`. Empty by default: Cerbos denies everything until something puts policies in front of it.  cerbos:   policies:     resource_myapp.yaml: |       apiVersion: api.cerbos.dev/v1       resourcePolicy:         resource: myapp.thing         version: "default"         rules:           - actions: ["read"]             effect: EFFECT_ALLOW             roles: ["*"]</td>
		</tr>
		<tr>
			<td>cerbos.policyValidation</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true
}
</pre>
</td>
			<td>Policy validation before the server starts.</td>
		</tr>
		<tr>
			<td>cerbos.policyValidation.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Run `cerbos compile` in an init container before the server starts, so an invalid policy tree stalls the rollout instead of crash-looping Cerbos.</td>
		</tr>
		<tr>
			<td>containerSecurityContext</td>
			<td>object</td>
			<td><pre lang="json">
{
  "allowPrivilegeEscalation": false,
  "capabilities": {
    "drop": [
      "ALL"
    ]
  },
  "enabled": true,
  "privileged": false,
  "readOnlyRootFilesystem": true,
  "runAsGroup": 64110,
  "runAsNonRoot": true,
  "runAsUser": 64110,
  "seccompProfile": {
    "type": "RuntimeDefault"
  }
}
</pre>
</td>
			<td>Security Context. Cerbos ships as a "scratch" image and runs as the fixed guardian-server uid/gid 64110. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/</td>
		</tr>
		<tr>
			<td>containerSecurityContext.allowPrivilegeEscalation</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Enable container privileged escalation.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities</td>
			<td>object</td>
			<td><pre lang="json">
{
  "drop": [
    "ALL"
  ]
}
</pre>
</td>
			<td>Security capabilities for container.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities.drop</td>
			<td>list</td>
			<td><pre lang="json">
[
  "ALL"
]
</pre>
</td>
			<td>List of capabilities to be dropped.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.privileged</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Run the container in privileged mode.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.readOnlyRootFilesystem</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Mounts the container's root filesystem as read-only.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsGroup</td>
			<td>int</td>
			<td><pre lang="json">
64110
</pre>
</td>
			<td>Process group id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsNonRoot</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Run container as a user.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsUser</td>
			<td>int</td>
			<td><pre lang="json">
64110
</pre>
</td>
			<td>Process user id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile</td>
			<td>object</td>
			<td><pre lang="json">
{
  "type": "RuntimeDefault"
}
</pre>
</td>
			<td>Set Seccomp profile.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile.type</td>
			<td>string</td>
			<td><pre lang="json">
"RuntimeDefault"
</pre>
</td>
			<td>Disallow custom Seccomp profile by setting it to RuntimeDefault.</td>
		</tr>
		<tr>
			<td>extensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Extensions to load. This will override the configuration in `global.extensions`. Cerbos policies are read from the `guardian-policies` plugin directory of each image.  extensions:   - name: "my-integration"     image:       registry: "artifacts.example.com"       repository: "path/to/repository"       pullPolicy: "IfNotPresent"       tag: "1.1.10"</td>
		</tr>
		<tr>
			<td>extraEnvVars</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar"</td>
		</tr>
		<tr>
			<td>extraVolumeMounts</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumeMounts. Mounted into the Cerbos container and the policy validation init container alike, so policies added here are compiled before the server starts.  extraVolumeMounts:   - name: "portal-policies"     mountPath: "/policies/portal"     readOnly: true</td>
		</tr>
		<tr>
			<td>extraVolumes</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumes. This is how another component ships its own policies, as a ConfigMap mounted below `/policies`.  extraVolumes:   - name: "portal-policies"     configMap:       name: "{{ .Release.Name }}-portal-policies"</td>
		</tr>
		<tr>
			<td>fullnameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Provide a name to substitute for the full names of resources.</td>
		</tr>
		<tr>
			<td>global</td>
			<td>object</td>
			<td><pre lang="json">
{
  "extensions": [],
  "imagePullPolicy": null,
  "imagePullSecrets": [],
  "imageRegistry": "artifacts.software-univention.de",
  "systemExtensions": []
}
</pre>
</td>
			<td>Global values, shared with the umbrella chart and its other subcharts.</td>
		</tr>
		<tr>
			<td>global.extensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Allows to configure extensions globally.</td>
		</tr>
		<tr>
			<td>global.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails.</td>
		</tr>
		<tr>
			<td>global.imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>global.imageRegistry</td>
			<td>string</td>
			<td><pre lang="json">
"artifacts.software-univention.de"
</pre>
</td>
			<td>Container registry address.</td>
		</tr>
		<tr>
			<td>global.systemExtensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Allows to configure system extensions globally.</td>
		</tr>
		<tr>
			<td>imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>lifecycleHooks</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Lifecycle to automate configuration before or after startup.</td>
		</tr>
		<tr>
			<td>livenessProbe</td>
			<td>object</td>
			<td><pre lang="json">
{
  "failureThreshold": 10,
  "httpGet": {
    "path": "/_cerbos/health",
    "port": "http"
  },
  "initialDelaySeconds": 15,
  "periodSeconds": 20,
  "successThreshold": 1,
  "timeoutSeconds": 5
}
</pre>
</td>
			<td>Configure extra options for container liveness probes.</td>
		</tr>
		<tr>
			<td>livenessProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>livenessProbe.httpGet</td>
			<td>object</td>
			<td><pre lang="json">
{
  "path": "/_cerbos/health",
  "port": "http"
}
</pre>
</td>
			<td>The Cerbos health endpoint.</td>
		</tr>
		<tr>
			<td>livenessProbe.httpGet.path</td>
			<td>string</td>
			<td><pre lang="json">
"/_cerbos/health"
</pre>
</td>
			<td>Path of the health endpoint.</td>
		</tr>
		<tr>
			<td>livenessProbe.httpGet.port</td>
			<td>string</td>
			<td><pre lang="json">
"http"
</pre>
</td>
			<td>Port the health endpoint is served on.</td>
		</tr>
		<tr>
			<td>livenessProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td>Delay after container start until LivenessProbe is executed.</td>
		</tr>
		<tr>
			<td>livenessProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>livenessProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>livenessProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>nameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>String to partially override release name.</td>
		</tr>
		<tr>
			<td>nodeSelector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Node labels for pod assignment. Ref: https://kubernetes.io/docs/user-guide/node-selection/</td>
		</tr>
		<tr>
			<td>podAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Pod Annotations.</td>
		</tr>
		<tr>
			<td>podSecurityContext</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "fsGroup": 64110,
  "fsGroupChangePolicy": "Always"
}
</pre>
</td>
			<td>Pod Security Context. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/</td>
		</tr>
		<tr>
			<td>podSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroup</td>
			<td>int</td>
			<td><pre lang="json">
64110
</pre>
</td>
			<td>If specified, all processes of the container are also part of the supplementary group.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroupChangePolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td>Change ownership and permission of the volume before being exposed inside a Pod.</td>
		</tr>
		<tr>
			<td>readinessProbe</td>
			<td>object</td>
			<td><pre lang="json">
{
  "failureThreshold": 10,
  "httpGet": {
    "path": "/_cerbos/health",
    "port": "http"
  },
  "initialDelaySeconds": 15,
  "periodSeconds": 20,
  "successThreshold": 1,
  "timeoutSeconds": 5
}
</pre>
</td>
			<td>Configure extra options for container startup probes.</td>
		</tr>
		<tr>
			<td>readinessProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>readinessProbe.httpGet</td>
			<td>object</td>
			<td><pre lang="json">
{
  "path": "/_cerbos/health",
  "port": "http"
}
</pre>
</td>
			<td>The Cerbos health endpoint.</td>
		</tr>
		<tr>
			<td>readinessProbe.httpGet.path</td>
			<td>string</td>
			<td><pre lang="json">
"/_cerbos/health"
</pre>
</td>
			<td>Path of the health endpoint.</td>
		</tr>
		<tr>
			<td>readinessProbe.httpGet.port</td>
			<td>string</td>
			<td><pre lang="json">
"http"
</pre>
</td>
			<td>Port the health endpoint is served on.</td>
		</tr>
		<tr>
			<td>readinessProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td>Delay after container start until ReadinessProbe is executed.</td>
		</tr>
		<tr>
			<td>readinessProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>readinessProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>readinessProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>replicaCount</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Set the amount of replicas of deployment.</td>
		</tr>
		<tr>
			<td>resources</td>
			<td>object</td>
			<td><pre lang="json">
{
  "limits": {
    "memory": "512Mi"
  },
  "requests": {
    "cpu": "100m",
    "memory": "128Mi"
  }
}
</pre>
</td>
			<td>Configure resource requests and limits.  Ref: https://kubernetes.io/docs/user-guide/compute-resources/</td>
		</tr>
		<tr>
			<td>resources.limits</td>
			<td>object</td>
			<td><pre lang="json">
{
  "memory": "512Mi"
}
</pre>
</td>
			<td>Resource ceilings the container is held to.</td>
		</tr>
		<tr>
			<td>resources.limits.memory</td>
			<td>string</td>
			<td><pre lang="json">
"512Mi"
</pre>
</td>
			<td>Memory ceiling, above which the container is OOM-killed. No CPU limit is set, so policy compilation may burst above the request.</td>
		</tr>
		<tr>
			<td>resources.requests</td>
			<td>object</td>
			<td><pre lang="json">
{
  "cpu": "100m",
  "memory": "128Mi"
}
</pre>
</td>
			<td>Resources the container is guaranteed and scheduled with.</td>
		</tr>
		<tr>
			<td>resources.requests.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"100m"
</pre>
</td>
			<td>CPU the container is guaranteed and scheduled with.</td>
		</tr>
		<tr>
			<td>resources.requests.memory</td>
			<td>string</td>
			<td><pre lang="json">
"128Mi"
</pre>
</td>
			<td>Memory the container is guaranteed and scheduled with.</td>
		</tr>
		<tr>
			<td>service</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {},
  "enabled": true,
  "type": "ClusterIP"
}
</pre>
</td>
			<td>Kubernetes Service for the Cerbos ports.</td>
		</tr>
		<tr>
			<td>service.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations.</td>
		</tr>
		<tr>
			<td>service.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable kubernetes service creation.</td>
		</tr>
		<tr>
			<td>service.type</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIP"
</pre>
</td>
			<td>Choose the kind of Service, one of "ClusterIP", "NodePort" or "LoadBalancer".</td>
		</tr>
		<tr>
			<td>serviceAccount</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {},
  "automountServiceAccountToken": false,
  "create": true
}
</pre>
</td>
			<td>Service account the pod runs under. Ref.: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/</td>
		</tr>
		<tr>
			<td>serviceAccount.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Annotations to add to the service account.</td>
		</tr>
		<tr>
			<td>serviceAccount.automountServiceAccountToken</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Allows auto mount of ServiceAccountToken on the serviceAccount created. Can be set to false if pods using this serviceAccount do not need to use the Kubernetes API.</td>
		</tr>
		<tr>
			<td>serviceAccount.create</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Specifies whether a service account should be created.</td>
		</tr>
		<tr>
			<td>startupProbe</td>
			<td>object</td>
			<td><pre lang="json">
{
  "failureThreshold": 10,
  "httpGet": {
    "path": "/_cerbos/health",
    "port": "http"
  },
  "initialDelaySeconds": 15,
  "periodSeconds": 20,
  "successThreshold": 1,
  "timeoutSeconds": 5
}
</pre>
</td>
			<td>Configure extra options for container probes.</td>
		</tr>
		<tr>
			<td>startupProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>startupProbe.httpGet</td>
			<td>object</td>
			<td><pre lang="json">
{
  "path": "/_cerbos/health",
  "port": "http"
}
</pre>
</td>
			<td>The Cerbos health endpoint.</td>
		</tr>
		<tr>
			<td>startupProbe.httpGet.path</td>
			<td>string</td>
			<td><pre lang="json">
"/_cerbos/health"
</pre>
</td>
			<td>Path of the health endpoint.</td>
		</tr>
		<tr>
			<td>startupProbe.httpGet.port</td>
			<td>string</td>
			<td><pre lang="json">
"http"
</pre>
</td>
			<td>Port the health endpoint is served on.</td>
		</tr>
		<tr>
			<td>startupProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td>Delay after container start until StartupProbe is executed.</td>
		</tr>
		<tr>
			<td>startupProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>startupProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>startupProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>systemExtensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Allows to configure the system extensions to load. This is intended for internal usage, prefer to use `extensions` for user configured extensions. This value will override the configuration in `global.systemExtensions`.</td>
		</tr>
		<tr>
			<td>terminationGracePeriodSeconds</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>In seconds, time given to the pod to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods</td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Tolerations for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/</td>
		</tr>
		<tr>
			<td>topologySpreadConstraints</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule</td>
		</tr>
		<tr>
			<td>updateStrategy</td>
			<td>object</td>
			<td><pre lang="json">
{
  "type": "RollingUpdate"
}
</pre>
</td>
			<td>Configure the update strategy.  Ref: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy  Example: updateStrategy:  type: RollingUpdate  rollingUpdate:    maxSurge: 25%    maxUnavailable: 25%</td>
		</tr>
		<tr>
			<td>updateStrategy.type</td>
			<td>string</td>
			<td><pre lang="json">
"RollingUpdate"
</pre>
</td>
			<td>Deployment update strategy, one of "RollingUpdate" or "Recreate".</td>
		</tr>
	</tbody>
</table>

