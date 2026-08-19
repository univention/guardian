# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
Cerbos loads `/policies` recursively, one subdirectory per source. Two are
fixed (`chart` for whatever `cerbos.policies` holds, `extensions` for packaged
integrations) and the rest arrive as plain extraVolumes, which is what lets
another component ship policies without this chart knowing their content.
"""

from pytest_helm.utils import load_yaml


DEPLOYMENT = 'templates/deployment.yaml'
POLICIES_CONFIGMAP = 'templates/configmap-policies.yaml'
CONFIGMAP = 'templates/configmap.yaml'

INLINE_POLICY = """
cerbos:
  policies:
    resource_myapp.yaml: |
      apiVersion: api.cerbos.dev/v1
      resourcePolicy:
        resource: myapp.thing
        version: "default"
        rules:
          - actions: ["read"]
            effect: EFFECT_ALLOW
            roles: ["*"]
"""

EXTRA_SOURCE = """
extraVolumes:
  - name: "portal-policies"
    configMap:
      name: "{{ .Release.Name }}-portal-policies"
extraVolumeMounts:
  - name: "portal-policies"
    mountPath: "/policies/portal"
    readOnly: true
"""


def _pod_spec(helm, chart_path, values):
    deployment = helm.helm_template(chart_path, values, DEPLOYMENT).get_resource()
    return deployment.findone('spec.template.spec')


def _cerbos_config(helm, chart_path, values):
    configmap = helm.helm_template(chart_path, values, CONFIGMAP).get_resource()
    return load_yaml(configmap['data']['cerbos.yaml'])


def test_the_chart_ships_no_policies_of_its_own(helm, chart_path):
    """The slot exists and is empty; nothing is authorized by installing this."""
    configmap = helm.helm_template(chart_path, {}, POLICIES_CONFIGMAP).get_resource()

    assert configmap.get('data') in (None, {})


def test_policies_from_values_become_files_in_the_chart_directory(helm, chart_path):
    values = load_yaml(INLINE_POLICY)
    configmap = helm.helm_template(chart_path, values, POLICIES_CONFIGMAP).get_resource()
    pod = _pod_spec(helm, chart_path, values)

    assert 'resource_myapp.yaml' in configmap['data']

    volume = next(v for v in pod['volumes'] if v['name'] == 'policies')
    assert volume['configMap']['name'] == 'release-name-guardian-cerbos-policies'


def test_the_validator_sees_exactly_what_the_server_loads(helm, chart_path):
    """
    Validation that runs against a different tree than the server loads proves
    nothing, so every policy mount has to reach both containers. That includes
    extraVolumeMounts, which is the only way another component adds a source.
    """
    pod = _pod_spec(helm, chart_path, load_yaml(EXTRA_SOURCE))
    server = pod['containers'][0]
    validator = next(c for c in pod['initContainers'] if c['name'] == 'validate-policies')

    expected = {
        'policies': '/policies/chart',
        'plugin-targets': '/policies/extensions',
        'portal-policies': '/policies/portal',
    }
    for container in (server, validator):
        mounted = {m['name']: m['mountPath'] for m in container['volumeMounts']}
        assert {k: v for k, v in mounted.items() if v.startswith('/policies/')} == expected


def test_extra_volumes_are_templated(helm, chart_path):
    """So a component can refer to the release it is deployed with."""
    pod = _pod_spec(helm, chart_path, load_yaml(EXTRA_SOURCE))

    volume = next(v for v in pod['volumes'] if v['name'] == 'portal-policies')
    assert volume['configMap']['name'] == 'release-name-portal-policies'


def test_the_policies_directory_is_what_cerbos_is_told_to_read(helm, chart_path):
    """
    `/policies` is a literal in both deployment.yaml and configmap.yaml. A mount
    below a directory Cerbos does not read is silently ignored, so the two have
    to be checked against each other.
    """
    pod = _pod_spec(helm, chart_path, {})
    validator = next(c for c in pod['initContainers'] if c['name'] == 'validate-policies')
    config = _cerbos_config(helm, chart_path, {})

    assert config['storage']['disk']['directory'] == '/policies'
    assert validator['args'][-1] == '/policies'
    for mount in pod['containers'][0]['volumeMounts']:
        if mount['name'] in ('policies', 'plugin-targets'):
            assert mount['mountPath'].startswith('/policies/')


def test_storage_configuration_cannot_be_overridden_from_values(helm, chart_path):
    """
    The chart mounts the policy sources and compiles that tree itself, so a
    different driver or directory would deploy a server that reads nothing.
    `watchForChanges` goes with it: live reload would let a policy change reach
    the server without passing validate-policies.
    """
    config = _cerbos_config(
        helm,
        chart_path,
        load_yaml("""
        cerbos:
          config:
            storage:
              driver: "git"
              disk:
                directory: "/somewhere-else"
                watchForChanges: true
        """),
    )

    assert config['storage']['driver'] == 'disk'
    assert config['storage']['disk']['directory'] == '/policies'
    assert config['storage']['disk']['watchForChanges'] is False


def test_the_rest_of_the_cerbos_configuration_passes_through(helm, chart_path):
    """`cerbos.config` is raw Cerbos configuration, not a modelled schema."""
    config = _cerbos_config(
        helm,
        chart_path,
        load_yaml("""
        cerbos:
          config:
            server:
              logRequestPayloads: true
            audit:
              enabled: true
        """),
    )

    assert config['audit']['enabled'] is True
    assert config['server']['logRequestPayloads'] is True
    # Merged, not replaced.
    assert config['server']['playgroundEnabled'] is False
