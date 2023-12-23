.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _installation:

************
Installation
************

.. _installation-on-ucs-primary-node:

Installation on a UCS primary node
==================================

The different components of the Guardian can be installed from the Univention App Center. A prerequisite for using
the Guardian is a working Keycloak installation in the UCS domain. How to install and configure Keycloak in a UCS
domain can be found `here <https://docs.software-univention.de/keycloak-app/latest/index.html>`_.

To install all required components on a UCS primary node, run:

.. code-block:: bash

   univention-app install \
       guardian-management-api \
       guardian-authorization-api \
       guardian-management-ui

Most of the settings are configured automatically, but since this is a preview version, some manual configuration steps
remain.

``KEYCLOAK_SECRET`` can be obtained by running the following command:

.. code-block:: bash

   KEYCLOAK_SECRET=$(univention-keycloak oidc/rp secret --client-name guardian-cli | sed -n 2p | sed "s/.*'value': '\([[:alnum:]]*\)'.*/\1/")

Update settings for the :term:`Management UI`:

.. code-block:: bash

   univention-app configure guardian-management-api --set \
       "guardian-management-api/oauth/keycloak-client-secret=$KEYCLOAK_SECRET"

Then set your ``USERNAME`` and ``PASSWORD`` to credentials for a user which
has access to the UDM REST API:

.. code-block:: bash

   USERNAME=Administrator
   PASSWORD=password

Then update settings for the Guardian :term:`Authorization API`:

.. code-block:: bash

   univention-app configure guardian-authorization-api --set \
       "guardian-authorization-api/udm_data/username=$USERNAME" \
       "guardian-authorization-api/udm_data/password=$PASSWORD"

To be able to use the Guardian Management UI, it is also necessary to give the user the required permissions. For this the Management UI already utilizes the Guardian.
This means the user needs to get the proper ``guardianRole`` assigned. To make the Administrator account the :term:`Guardian super user <guardian administrator>`, who has all privileges, execute:

.. code-block:: bash

   udm users/user modify --dn uid=Administrator,cn=users,$(ucr get ldap/base) \
       --set guardianRole=guardian:builtin:super-admin

With these steps the Guardian setup is complete and the Management UI should be available from the Univention Portal.

.. _configuring-keycloak-for-join-scripts:

Configuring Keycloak for join scripts
-------------------------------------

When installing an :term:`app` that uses the Guardian, it will need a special
Keycloak client that is configured specifically for join scripts.

Run the following command on the server with the Guardian Management API installed:

.. code-block:: bash

   GUARDIAN_SERVER="$(hostname).$(ucr get domainname)"
   univention-keycloak oidc/rp create \
       --name guardian-scripts \
       --app-url https://$GUARDIAN_SERVER \
       --redirect-uri "https://$GUARDIAN_SERVER/univention/guardian/*" \
       --add-audience-mapper guardian-scripts

Then configure the new client using the Keycloak web interface.
Choose :menuselection:`ucs` from the realm drop-down list at the top of the left navigation bar.
Then click on :menuselection:`Clients` in the left navigation bar, and choose :menuselection:`guardian-scripts`.

Configure password login for scripts and remove the client secret:

#. Go to the :guilabel:`Settings` tab.
#. Navigate to the :guilabel:`Capability config` section.
#. Turn :guilabel:`Client authentication` off.
#. Under :guilabel:`Authentication flow`, check the checkbox for :guilabel:`Direct access grants`.

Click the :guilabel:`Save` button at the bottom of the screen.

Configure the correct audience for the Guardian:

#. Go to the :guilabel:`Client scopes` tab.
#. Click on :guilabel:`guardian-scopes-dedicated`.
#. Choose :menuselection:`Add mapper --> By configuration`.
    #. Select :guilabel:`Audience`.
    #. For the :guilabel:`Name`, use ``guardian-audience``.
    #. For the :guilabel:`Included Client Audience`, choose ``guardian``.
#. Choose :menuselection:`Add mapper --> By configuration`.
    #. Select :guilabel:`User Attribute`.
    #. For the :guilabel:`Name`, use ``dn``.
    #. For the :guilabel:`User Attribute`, use ``LDAP_ENTRY_DN``.
    #. For the :guilabel:`Token Claim Name`, use ``dn``.
    #. Turn :guilabel:`Add to ID Token` off.
    #. Turn :guilabel:`Add to userinfo` off.
    #. Verify that :guilabel:`Add to access token` is on.

Click the :guilabel:`Save` button at the bottom of the screen.

.. _installation-on-different-ucs-server-roles:

Installation on different UCS server roles
==========================================

This setup assumes that all Guardian components are installed on the same host and that Keycloak as well as the UDM
REST API are running on that host as well. This is usually the UCS primary node.
The Guardian supports the installation of its components on any UCS server role as well as distributing the individual
components on different hosts. For that to work though, multiple settings
regarding URLs for Keycloak, the UDM REST API and the different Guardian components themselves have to be configured manually.
Please check the chapter Configuration for a full reference of all the app settings.

.. _load-balancing-and-multiple-instances:

Load balancing and multiple instances
=====================================

The Guardian was developed with the capability of running multiple instances of each component in mind. It is possible
to deploy multiple instances of the Guardian Management UI and Guardian Authorization API apps in the UCS domain without
any problems, as long as they are properly configured.

The Management API should only be deployed once in any UCS domain due to the limitations mentioned in :ref:`app-center-database-limitations`.
