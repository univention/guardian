.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _installation:

************
Installation
************

This section is for :term:`Guardian administrators <guardian administrator>`
and covers the installation of the Guardian on UCS systems.
If you're upgrading the Guardian to a new version, refer to the upgrade guide :ref:`upgrade-on-ucs-primary-node`.

.. _installation-on-ucs-primary-node:

Installation on a UCS Primary Directory Node
============================================

This section describes the installation of the Guardian on a
:external+uv-ucs-manual:ref:`domain-ldap-primary-directory-node`.
For other server roles, see :ref:`installation-various-ucs-server-roles`.

:term:`Guardian administrators <guardian administrator>`
install the different components of the Guardian from the Univention App Center.
A prerequisite for using the Guardian is a working Keycloak installation in the UCS domain.
For information about how to install and configure Keycloak in a UCS,
refer to
:external+uv-keycloak-app:ref:`Installation of Keycloak app <app-installation>`.

To install all required components on a UCS primary node,
run the following command:

.. code-block:: bash
   :caption: Install Guardian apps from command line

   $ univention-app install \
       guardian-management-api \
       guardian-authorization-api \
       guardian-management-ui

The installation procedure automatically configures most of the settings,
but some manual configuration steps remain,
as described in the following sections.

You need to obtain the ``KEYCLOAK_SECRET`` by running the following command:

.. code-block:: bash
   :caption: Retrieve ``KEYCLOAK_SECRET``

   $ KEYCLOAK_SECRET=$(univention-keycloak \
      oidc/rp secret \
      --client-name guardian-management-api \
      | sed -n 2p \
      | sed "s/.*'value': '\([[:alnum:]]*\)'.*/\1/")

Create the machine-to-machine secret file for the :term:`Management API` and adjust the access permissions:

.. code-block:: bash
   :caption: Create machine-to-machine secret file

   $ touch /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret
   $ chmod 600 /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret

Write the contents of ``KEYCLOAK_SECRET`` to the machine-to-machine secret file:

.. code-block:: bash
   :caption: Write ``KEYCLOAK_SECRET`` to the machine-to-machine secret file

   $ echo $KEYCLOAK_SECRET > /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret

To apply the new secret file, run:

.. code-block:: bash
   :caption: Configure and restart the :term:`Management API`

   $ univention-app configure guardian-management-api
   $ univention-app restart guardian-management-api

The configuration and restart is also necessary for the :term:`Authorization API`:

.. code-block:: bash
   :caption: Configure and restart the :term:`Authorization API`

   $ univention-app configure guardian-authorization-api
   $ univention-app restart guardian-authorization-api

To use the Guardian *Management UI*,
it's also necessary to give the user the required permissions.
For this step the *Management UI* already utilizes the Guardian.
The user needs to get the proper ``guardianRole`` assigned.
To make the ``Administrator`` account the :term:`Guardian super user <guardian administrator>`,
who has all privileges, run the following command:

.. code-block:: bash
   :caption: Assign Guardian super user role to ``Administrator`` user

   $ udm users/user modify \
      --dn uid=Administrator,cn=users,$(ucr get ldap/base) \
      --set guardianRole=guardian:builtin:super-admin

You have completed the Guardian setup.
You can reach the *Management UI* from the
:external+uv-ucs-manual:ref:`Univention Portal <central-portal>`.

.. _upgrade-on-ucs-primary-node:

Upgrading the Guardian
======================

For minor and patch level version changes, use the command ``univention-app upgrade``:

.. code-block:: bash
   :caption: Install Guardian apps from command line

   $ univention-app upgrade \
       guardian-management-api \
       guardian-authorization-api \
       guardian-management-ui

Upgrading from major version 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the command ``univention-app upgrade`` to upgrade the Guardian:

.. code-block:: bash
   :caption: Install Guardian apps from command line

   $ univention-app upgrade \
       guardian-management-api \
       guardian-authorization-api \
       guardian-management-ui

The previous major version used a different Keycloak client for the :term:`Management API`,
so the secret file for the client must be updated.
Obtain the ``KEYCLOAK_SECRET`` for the new client with the following command,
using the server where Keycloak is installed:

.. code-block:: bash
   :caption: Retrieve ``KEYCLOAK_SECRET``

   $ KEYCLOAK_SECRET=$(univention-keycloak \
      oidc/rp secret \
      --client-name guardian-management-api \
      | sed -n 2p \
      | sed "s/.*'value': '\([[:alnum:]]*\)'.*/\1/")

On the server where the Management API is located:

.. code-block:: bash
   :caption: Write ``KEYCLOAK_SECRET`` to the machine-to-machine secret file

   $ echo $KEYCLOAK_SECRET > /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret
   $ chmod 600 /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret

If you are unsure whether the Guardian was set up correctly during the previous installation,
follow the configuration steps described in :ref:`installation-on-ucs-primary-node` to complete the upgrade.
Otherwise, the only additionally needed configuration steps are:

.. code-block:: bash
   :caption: Additional configure and restart step

   $ univention-app configure guardian-authorization-api
   $ univention-app restart guardian-authorization-api
   $ univention-app configure guardian-management-api
   $ univention-app restart guardian-management-api

.. _installation-various-ucs-server-roles:

Installation on various UCS server roles
========================================

This setup assumes that you have all Guardian components installed on the same UCS system,
and that Keycloak and the UDM REST API are also running on that system.
This system is usually the
:external+uv-ucs-manual:ref:`domain-ldap-primary-directory-node`.

The Guardian supports the installation of the :term:`Management API` on any UCS server role,
as well as the distribution of the individual components on different systems.
For this to work, however,
you must manually configure several settings regarding URLs for
:external+uv-keycloak-app:doc:`Keycloak <index>`,
the :external+uv-dev-ref:ref:`UDM REST API <udm-rest-api>`,
and the various :ref:`Guardian components <guardian-apps>` themselves.
For a full reference of all the app settings, refer to the section :ref:`conf`.
The installation of the :term:`Authorization API` is restricted to the UCS server role :external+uv-ucs-manual:ref:`domain-ldap-primary-directory-node` and :external+uv-ucs-manual:ref:`domain-ldap-backup-directory-node`.

.. _load-balancing-and-multiple-instances:

Load balancing and multiple instances
=====================================

A design goal for the Guardian was the ability to run multiple instances of each component.
It's possible to deploy multiple instances of
the Guardian :term:`Management UI` and Guardian :term:`Authorization API` apps
in the UCS domain with no known issues,
as long as they're configured properly.

Only deploy the :term:`Management API` once in each UCS domain
due to the limitations mentioned in :ref:`limits-app-center-database`.
