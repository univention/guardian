# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
Nubus packaged integrations ship Cerbos policies in a `guardian-policies`
plugin directory. The chart never sees their content, so what has to hold is
structural: the files reach the directory Cerbos reads, and the validator sees
them before the server does.
"""

import copy

import pytest
from pytest_helm.utils import load_yaml


DEPLOYMENT = 'templates/deployment.yaml'

ALL_EXTENSION_KEYS = (
    'extensions',
    'systemExtensions',
    'global.extensions',
    'global.systemExtensions',
)

STUB_EXTENSION = """
name: "stub-test"
image:
  registry: "stub-registry"
  repository: "stub-repository"
  pullPolicy: "stub-image-pull-policy"
  tag: "stub-tag"
"""


@pytest.fixture
def stub_extension():
    return load_yaml(STUB_EXTENSION)


def _pod_spec(helm, chart_path, values):
    deployment = helm.helm_template(chart_path, values, DEPLOYMENT).get_resource()
    return deployment.findone('spec.template.spec')


def _extension_containers(pod):
    return [c for c in pod.get('initContainers', []) if c['name'].endswith('-extension')]


def _set_dot_path_value(target, key, value):
    scope = target
    key_path = key.split('.')
    for fragment in key_path[:-1]:
        scope = scope.setdefault(fragment, {})
    scope[key_path[-1]] = value


def _values_with_extension(key, extension):
    values = {}
    _set_dot_path_value(values, key, [extension])
    return values


def test_no_extensions_by_default(helm, chart_path):
    """The directory is always there, empty; nothing loads into it unasked."""
    pod = _pod_spec(helm, chart_path, {})

    assert _extension_containers(pod) == []
    assert {'name': 'plugin-targets', 'emptyDir': {}} in pod['volumes']


@pytest.mark.parametrize('key', ALL_EXTENSION_KEYS)
def test_extension_configured(helm, chart_path, key, stub_extension):
    pod = _pod_spec(helm, chart_path, _values_with_extension(key, stub_extension))

    containers = _extension_containers(pod)
    assert len(containers) == 1
    assert containers[0]['name'] == 'load-stub-test-extension'


def test_custom_and_system_extensions_are_joined(helm, chart_path, stub_extension):
    """Nubus' own integrations load first, so a customer one can build on them."""
    stub_system_extension = copy.deepcopy(stub_extension)
    stub_system_extension['name'] = 'stub-system'
    values = {'extensions': [stub_extension], 'systemExtensions': [stub_system_extension]}

    pod = _pod_spec(helm, chart_path, values)

    names = [container['name'] for container in _extension_containers(pod)]
    assert names == ['load-stub-system-extension', 'load-stub-test-extension']


@pytest.mark.parametrize('key', ALL_EXTENSION_KEYS)
def test_extension_image(helm, chart_path, key, stub_extension):
    pod = _pod_spec(helm, chart_path, _values_with_extension(key, stub_extension))

    assert _extension_containers(pod)[0]['image'] == 'stub-registry/stub-repository:stub-tag'


@pytest.mark.parametrize('key', ALL_EXTENSION_KEYS)
def test_extension_image_falls_back_to_the_global_registry(helm, chart_path, key, stub_extension):
    del stub_extension['image']['registry']
    values = _values_with_extension(key, stub_extension)
    values['global'] = {**values.get('global', {}), 'imageRegistry': 'stub-global-registry'}

    pod = _pod_spec(helm, chart_path, values)

    assert _extension_containers(pod)[0]['image'] == 'stub-global-registry/stub-repository:stub-tag'


@pytest.mark.parametrize('key', ['extensions', 'systemExtensions'])
def test_local_configuration_overrides_global_configuration(helm, chart_path, key, stub_extension):
    values = {
        'global': {key: [{**stub_extension, 'name': 'stub-global'}]},
        key: [stub_extension],
    }

    pod = _pod_spec(helm, chart_path, values)

    containers = _extension_containers(pod)
    assert len(containers) == 1
    assert containers[0]['name'] == 'load-stub-test-extension'


def test_extension_policies_reach_the_directory_cerbos_reads(helm, chart_path, stub_extension):
    """
    The loader writes to `/target/<plugin-type>` and Cerbos reads `/policies`.
    Both ends have to name the same volume, or the policies are copied into an
    emptyDir nothing ever looks at.
    """
    pod = _pod_spec(helm, chart_path, {'extensions': [stub_extension]})

    loader = _extension_containers(pod)[0]
    assert [(m['name'], m['mountPath']) for m in loader['volumeMounts']] == [
        ('plugin-targets', '/target/guardian-policies'),
    ]

    server = pod['containers'][0]
    served = [m for m in server['volumeMounts'] if m['name'] == 'plugin-targets']
    assert served == [{'name': 'plugin-targets', 'mountPath': '/policies/extensions', 'readOnly': True}]

    assert {'name': 'plugin-targets', 'emptyDir': {}} in pod['volumes']


def test_extension_policies_are_mounted_without_a_subpath(helm, chart_path, stub_extension):
    """
    A `subPath` directory is created by the kubelet as root, after fsGroup has
    been applied, so the non-root loader could not write into it. The emptyDir
    root is the writable one.
    """
    pod = _pod_spec(helm, chart_path, {'extensions': [stub_extension]})

    for container in _extension_containers(pod) + [pod['containers'][0]]:
        for mount in container['volumeMounts']:
            assert 'subPath' not in mount


def test_extension_policies_are_validated_before_the_server_starts(helm, chart_path, stub_extension):
    """
    A packaged integration is third-party content. If it does not compile, the
    rollout has to stall on the validator rather than crash-loop the server,
    which means the loaders have to run first and the validator has to see
    their output.
    """
    pod = _pod_spec(helm, chart_path, {'extensions': [stub_extension]})

    names = [container['name'] for container in pod['initContainers']]
    assert names == ['load-stub-test-extension', 'validate-policies']

    validator = pod['initContainers'][-1]
    mounted = {m['mountPath'] for m in validator['volumeMounts']}
    assert '/policies/extensions' in mounted
