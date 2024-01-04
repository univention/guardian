.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _installation:

************
Installation
************

This section is for :term:`Guardian administrators <guardian administrator>`
and covers the installation of the Guardian on UCS systems.

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
      --client-name guardian-cli \
      | sed -n 2p \
      | sed "s/.*'value': '\([[:alnum:]]*\)'.*/\1/")

You need the secret to enable the *Management API* to access Keycloak.
Add the ``KEYCLOAK_SECRET`` to the setting
:envvar:`guardian-management-api/oauth/keycloak-client-secret`
for the :term:`Management API`:

.. code-block:: bash
   :caption: Add ``KEYCLOAK_SECRET`` to :term:`Management API`

   $ univention-app \
      configure guardian-management-api \
      --set \
      "guardian-management-api/oauth/keycloak-client-secret=$KEYCLOAK_SECRET"

Then set your ``USERNAME`` and ``PASSWORD`` to credentials for a user which
has access to the
:external+uv-dev-ref:ref:`UDM REST API <udm-rest-api>`:

.. code-block:: bash
   :caption: Define credentials for user access to UDM REST API

   $ USERNAME="Administrator"
   $ PASSWORD="password"

Then update settings for the Guardian :term:`Authorization API`:

.. code-block:: bash
   :caption: Configure :term:`Authorization API` for access to UDM REST API

   $ univention-app \
      configure guardian-authorization-api \
      --set \
      "guardian-authorization-api/udm_data/username=$USERNAME" \
      "guardian-authorization-api/udm_data/password=$PASSWORD"

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

.. _configuring-keycloak-for-join-scripts:

Configuring Keycloak for join scripts
-------------------------------------

When installing an :term:`app` that uses the Guardian,
it needs a dedicated Keycloak client specifically for join scripts.

Create Keycloak client for join scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following command on the UCS system with the Guardian :term:`Management API` installed:

.. code-block:: bash
   :caption: Create Keycloak client specifically for join scripts

   $ GUARDIAN_SERVER="$(hostname).$(ucr get domainname)"
   $ univention-keycloak oidc/rp create \
       --name guardian-scripts \
       --app-url https://$GUARDIAN_SERVER \
       --redirect-uri "https://$GUARDIAN_SERVER/univention/guardian/*" \
       --add-audience-mapper guardian-scripts

Configure created Keycloak client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then configure the created client using the
:external+uv-keycloak-app:ref:`Keycloak Admin Console <keycloak-admin-console>`.
In the *Keycloak Admin Console* use the following steps:

#. Select :menuselection:`ucs` from the realm drop-down list at the top of the left sidebar navigation.

#. Click :guilabel:`Clients` in the left sidebar navigation.

#. Select :menuselection:`guardian-scripts`.

Activate password login for scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the password login for scripts and remove the client secret,
use the following steps:

#. Go to the :menuselection:`Settings → Capability config`.

#. Deactivate :guilabel:`Client authentication`.

#. In the section :menuselection:`Authentication flow`,
   activate :guilabel:`Direct access grants`.

#. Click :guilabel:`Save` at the bottom of the screen.

Configure audience for Guardian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the correct audience for the Guardian,
use the following steps:

#. Go to :guilabel:`Client scopes` tab.

#. Click :guilabel:`guardian-scopes-dedicated`.

#. Select :menuselection:`Add mapper --> By configuration --> Audience`:

   :Name: ``guardian-audience``
   :Included Client Audience: ``guardian``

#. Select :menuselection:`Add mapper --> By configuration --> User Attribute`:

   :Name: ``dn``
   :User Attribute*: ``LDAP_ENTRY_DN``
   :Token Claim Name*: ``dn``
   :Add to ID Token: Deactivate
   :Add to userinfo: Deactivate
   :Add to access token: Activate

#. Click :guilabel:`Save` at the bottom of the screen.

.. _installation-various-ucs-server-roles:

Installation on various UCS server roles
========================================

This setup assumes that you have all Guardian components installed on the same UCS system,
and that Keycloak and the UDM REST API are also running on that system.
This system is usually the
:external+uv-ucs-manual:ref:`domain-ldap-primary-directory-node`.

The Guardian supports the installation of its components on any UCS server role,
as well as the distribution of the individual components on different systems.
For this to work, however,
you must manually configure several settings regarding URLs for
:external+uv-keycloak-app:doc:`Keycloak <index>`,
the :external+uv-dev-ref:ref:`UDM REST API <udm-rest-api>`,
and the various :ref:`Guardian components <guardian-apps>` themselves.
For a full reference of all the app settings, refer to the section :ref:`conf`.

.. _load-balancing-and-multiple-instances:

Load balancing and multiple instances
=====================================

A design goal for the Guardian was the ability to run multiple instances of each component.
It's possible to deploy multiple instances of
the Guardian :term:`Management UI` and Guardian :term:`Authorization API` apps
in the UCS domain with no known issues,
as long as they're configured properly.

Only deploy the :term:`Management API` once in each UCS domain
due to the limitations mentioned in :ref:`app-center-database-limitations`.
