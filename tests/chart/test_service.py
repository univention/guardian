# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
The Cerbos ports are hard-coded rather than configurable, which trades one
values entry for the same literal in three templates.
"""

DEPLOYMENT = 'templates/deployment.yaml'
SERVICE = 'templates/service.yaml'


def test_the_cerbos_ports_agree_across_every_template(helm, chart_path):
    """
    3592 and 3593 are written as literals in the Deployment and the Service. A
    typo in one of them is invisible in a diff and breaks routing.
    """
    deployment = helm.helm_template(chart_path, {}, DEPLOYMENT).get_resource()
    service = helm.helm_template(chart_path, {}, SERVICE).get_resource()

    container_ports = {
        p['name']: p['containerPort'] for p in deployment.findone('spec.template.spec.containers[0].ports')
    }
    assert container_ports == {'http': 3592, 'grpc': 3593}

    assert {p['name']: p['port'] for p in service.findone('spec.ports')} == container_ports
    # targetPort refers to the container port by name, so the names have to match too.
    assert {p['name']: p['targetPort'] for p in service.findone('spec.ports')} == {'http': 'http', 'grpc': 'grpc'}
