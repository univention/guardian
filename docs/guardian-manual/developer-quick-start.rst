.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _developer-quick-start:

*********************
Developer quick start
*********************

.. important::

   This section covers a highly technical topic.
   It addresses :term:`app developers <app developer>`
   who want to integrate an :term:`app` with the Guardian.
   Familiarity with using the command line,
   working with an HTTP API,
   and writing code is necessary to understand this section.

   This section assumes familiarity with the following Univention documentation:

   * :external+uv-app-center:doc:`contents`
   * :external+uv-dev-ref:doc:`contents`

This section provides a walk-through of the steps necessary to integrate an :term:`app` with the Guardian.
It refers to the example outlined in :ref:`what-is-the-guardian`:

   *Example Organization* is an :term:`app developer` who creates :program:`Cake Express`,
   which allows people to order cakes for company events.
   Administrators can install the app from Univention App Center.
   They want to integrate Cake Express with the Guardian.

.. note::

   The example scripts in this section assume that:

   * You installed the app on the same UCS system as the Management API.

   * You installed the app on the same UCS system as the Keycloak server.

   If either of these two things isn't true,
   you need to find a way for the UCS :term:`app infrastructure maintainer`
   to communicate their locations to the script at run time.

.. _management-api-quick-start:

Management API
==============

This section describes how to get started with the *Management API*
to integrate your app with the Guardian.

.. _getting-a-keycloak-token:

Getting a Keycloak token
------------------------

The first thing that *Example Organization* needs to do
is to write a join script for its :term:`app`.
The app needs to interact with the :term:`Management API`.
To do this, the join script must obtain a token from
:external+uv-keycloak-app:doc:`Keycloak <index>`
to authenticate all calls to the API.

:numref:`getting-a-keycloak-token-variables` shows the variables you need
to obtain a token from Keycloak.

.. code-block:: bash
   :caption: Variables for obtaining a token from Keycloak
   :name: getting-a-keycloak-token-variables

   binduser=Administrator
   bindpwd=password

   CLIENT_ID=guardian-scripts

   GUARDIAN_KEYCLOAK_URL=$(ucr get guardian-management-api/oauth/keycloak-uri)
   SYSTEM_KEYCLOAK_URL=$(ucr get keycloak/server/sso/fqdn)
   KEYCLOAK_BASE_URL=${GUARDIAN_KEYCLOAK_URL:-$SYSTEM_KEYCLOAK_URL}

   KEYCLOAK_URL="$KEYCLOAK_BASE_URL/realms/ucs/protocol/openid-connect/token"
   if [[ ! $KEYCLOAK_URL == http ]]; then
       KEYCLOAK_URL="https://$KEYCLOAK_URL"
   fi

.. note::

   In a typical join script,
   the arguments ``--binduser``, ``--bindpwd``, and ``--bindpwdfile`` are available,
   which specify an administrator user,
   and either a password or a file for parsing the password.

   The example assumes that the join script has already parsed these parameters
   into the variables ``binduser`` and ``bindpwd``.

You can retrieve the token with the following command:

.. code-block:: bash

   $ token=$(curl -d "client_id=$CLIENT_ID" \
        -d "username=$binduser" \
        -d "password=$bindpwd" \
        -d "grant_type=password" \
        $KEYCLOAK_URL | sed 's/.*"access_token":"\([[:alnum:]\.-_-]*\)".*/\1/')

.. important::

   All commands in subsequent sections reference ``token``.
   You may need to refresh the token several times,
   if you are entering commands manually.

.. _registering-an-app:

Registering an app
------------------

*Example Organization* now needs to tell the Guardian about its :term:`app` :program:`Cake Express`.
To do this, it needs to take the token from the :ref:`previous section <getting-a-keycloak-token>`
and make a request to the :term:`Management API`.

.. code-block:: bash

   $ MANAGEMENT_SERVER="$(hostname).$(ucr get domainname)/guardian/management"

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cake-express", "display_name":"Cake Express"}' \
       $MANAGEMENT_SERVER/apps/register

*Example Organization* is now ready to start setting up the Guardian to work with Cake Express.

.. important::

   All names in Guardian are lower-case ASCII alphanumeric with either
   underscores or hyphens. The encoding for display names is only limited by
   the character support for the PostgreSQL database that Guardian uses.

.. _registering-namespaces:

Registering namespaces
----------------------

A :term:`namespace` is a categorization to store everything that an :term:`app` wants to use in Guardian,
like :term:`roles <role>` and :term:`permissions <permission>`.

Every app gets a ``default`` namespace to use.
*Example Organization* wants to manage three different facets of :program:`Cake Express`:

``cakes``
   Category for everything related to what's actually sold.

``orders``
   Category for administration of orders.

``users``
   Category for managing other users of Cake Express.

Later, *Example Organization* creates some roles in each of these namespaces
for tasks in Cake Express.
:numref:`registering-namespace-cakes` to :numref:`registering-namespace-users`
show how *Example Organization* creates these namespaces
for the app in the app's join script:

.. code-block:: bash
   :caption: Create namespace ``cakes``
   :name: registering-namespace-cakes

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cakes", "display_name":"Cakes"}' \
       $MANAGEMENT_SERVER/namespaces/cake-express

.. code-block:: bash
   :caption: Create namespace ``orders``
   :name: registering-namespace-orders

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"orders", "display_name":"Orders"}' \
       $MANAGEMENT_SERVER/namespaces/cake-express

.. code-block:: bash
   :caption: Create namespace ``users``
   :name: registering-namespace-users


   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"users", "display_name":"Users"}' \
       $MANAGEMENT_SERVER/namespaces/cake-express

.. _registering-roles:

Registering roles
-----------------

*Example Organization* wants to create three different :term:`roles <role>` for users of Cake Express:

``cake-express:cakes:cake-orderer``
   Someone who can order cakes from Cake Express.

``cake-express:orders:finance-manager``
   Someone who manages the expenses for the orders.

``cake-express:users:user-manager``
   Someone who manages other users within Cake Express.

*Example Organization* also wants to create a role for some of their cakes:

``cake-express:cakes:birthday-cake``
   A cake just for employee birthdays.

Each role consists of the following parts, separated by a colon (``:``):

* :term:`app`: for example ``cake-express``
* :term:`namespace`: for example ``cakes``
* role name: for example ``cake-orderer``

:numref:`registering-role-cake-orderer` to :numref:`registering-role-birthday-cake`
show how *Example Organization* creates these roles
for the app in the app's join script:

.. code-block:: bash
   :caption: Create role ``…:cake-orderer``
   :name: registering-role-cake-orderer

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cake-orderer", "display_name":"Cake Orderer"}' \
       $MANAGEMENT_SERVER/roles/cake-express/cakes

.. code-block:: bash
   :caption: Create role ``…:finance-manager``
   :name: registering-role-finance-manager

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"finance-manager", "display_name":"Finance Manager"}' \
       $MANAGEMENT_SERVER/roles/cake-express/orders

.. code-block:: bash
   :caption: Create role ``…:user-manager``
   :name: registering-role-user-manager

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"user-manager", "display_name":"User Manager"}' \
       $MANAGEMENT_SERVER/roles/cake-express/users

.. code-block:: bash
   :caption: Create role ``…:birthday-cake``
   :name: registering-role-birthday-cake

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"birthday-cake", "display_name":"Birthday Cake"}' \
       $MANAGEMENT_SERVER/roles/cake-express/cakes

.. _registering-permissions:

Registering permissions
-----------------------

*Example Organization* wants to provide some :term:`permissions <permission>`
that define what users of Cake Express want to do:

``cake-express:cakes:order-cake``
   Users with this permission can order cakes.

``cake-express:orders:cancel-order``
   Users can cancel a cake order.

``cake-express:users:manage-notifications``
   Users can manage cake notifications.

:numref:`registering-permissions-order-cake` to
:numref:`registering-permissions-manage-notifications`
show how *Example Organization* creates these permissions
for the app in the app's join script:

.. code-block:: bash
   :caption: Create permission ``…:order-cake``
   :name: registering-permissions-order-cake

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"order-cake", "display_name":"order cake"}' \
       $MANAGEMENT_SERVER/permissions/cake-express/cakes

.. code-block:: bash
   :caption: Create permission ``…:cancel-order``
   :name: registering-permissions-cancel-order

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cancel-order", "display_name":"cancel order"}' \
       $MANAGEMENT_SERVER/permissions/cake-express/orders

.. code-block:: bash
   :caption: Create permission ``…:manage-notifications``
   :name: registering-permissions-manage-notifications

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"manage-notifications", "display_name":"manage notifications"}' \
       $MANAGEMENT_SERVER/permissions/cake-express/users

.. _registering-capabilities:

Registering capabilities
------------------------

Finally, *Example Organization* wants to define some default :term:`capabilities <capability>` for its application.
The :term:`guardian app administrator`
who installs :program:`Cake Express` can change these later.
These default capabilities make it easier for Cake Express to work out of the box.

The app would like to create the following capabilities:

#. Users with the ``cake-orderer`` role can order cakes.

#. Users with the ``finance-manager`` role,
   or the person who ordered the cake,
   have the permission to cancel the cake order.

#. Users with the ``user-manager`` role have the permission to manage cake notifications.
   Users can also manage their own notifications for cakes sent to them,
   except for notifications related to birthday cakes.

Create Cake order
~~~~~~~~~~~~~~~~~

:numref:`registering-capabilities-cake-orderer`
shows how *Example Organization* creates the capability for ordering cake:

.. code-block:: bash
   :caption: Create capability for ordering cake
   :name: registering-capabilities-cake-orderer

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "name": "cake-orderer-can-order-cake",
             "display_name": "Cake Orderers can order cake",
             "role": {
               "app_name": "cake-express",
               "namespace_name": "cakes",
               "name": "cake-orderer"
             },
             "conditions": [],
             "relation": "AND",
             "permissions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "cakes",
                 "name": "order-cake"
               }
              ]
           }' \
       $MANAGEMENT_SERVER/capabilities/cake-express/cakes

Cancel cake order
~~~~~~~~~~~~~~~~~

:numref:`registering-capabilities-cancel-order-finance-manager` and
:numref:`registering-capabilities-cancel-order-self`
show how *Example Organization* creates the capability for canceling an order.
The action requires two ``POST`` requests to create the capability:

.. code-block:: bash
   :caption: Create capability to cancel a cake order for the finance manager role
   :name: registering-capabilities-cancel-order-finance-manager

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "name": "finance-manager-can-cancel-order",
             "display_name": "Finance Manager can cancel orders",
             "role": {
               "app_name": "cake-express",
               "namespace_name": "orders",
               "name": "finance-manager"
             },
             "conditions": [],
             "relation": "AND",
             "permissions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "orders",
                 "name": "cancel-order"
               }
             ]
           }' \
       $MANAGEMENT_SERVER/capabilities/cake-express/orders

.. code-block:: bash
   :caption: Create capability to cancel a cake order for the user themselves
   :name: registering-capabilities-cancel-order-self

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "name": "self-can-cancel-order",
             "display_name": "Users can cancel their own order",
             "role": {
               "app_name": "cake-express",
               "namespace_name": "cakes",
               "name": "cake-orderer"
             },
             "conditions": [
               {
                 "app_name": "guardian",
                 "namespace_name": "builtin",
                 "name": "target_field_equals_actor_field",
                 "parameters": [
                   {
                     "name": "actor_field",
                     "value": "id"
                   },
                   {
                     "name": "target_field",
                     "value": "orderer_id"
                   }
                 ]
               }
             ],
             "relation": "AND",
             "permissions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "orders",
                 "name": "cancel-order"
               }
             ]
           }' \
       $MANAGEMENT_SERVER/capabilities/cake-express/orders

Manage notifications
~~~~~~~~~~~~~~~~~~~~

:numref:`registering-capabilities-manage-notifications-user-manager` and
:numref:`registering-capabilities-manage-notifications-self`
show how *Example Organization* creates the capability for managing notifications.
The action requires two ``POST`` requests to create the capability:

.. code-block:: bash
   :caption: Create capability to manage notifications for the user manager role
   :name: registering-capabilities-manage-notifications-user-manager

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "name": "user-manager-can-manage-notifications",
             "display_name": "User Managers can manage cake notifications",
             "role": {
               "app_name": "cake-express",
               "namespace_name": "users",
               "name": "user-manager"
             },
             "conditions": [],
             "relation": "AND",
             "permissions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "users",
                 "name": "manage-notifications"
               }
              ]
           }' \
       $MANAGEMENT_SERVER/capabilities/cake-express/users

.. code-block:: bash
   :caption: Create capability to manage notifications for the user themselves
   :name: registering-capabilities-manage-notifications-self

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "name": "self-can-manage-notifications",
             "display_name": "Users can manage their own notifications, except for birthday cakes",
             "role": {
               "app_name": "cake-express",
               "namespace_name": "cakes",
               "name": "cake-orderer"
             },
             "conditions": [
               {
                 "app_name": "guardian",
                 "namespace_name": "builtin",
                 "name": "target_field_equals_actor_field",
                 "parameters": [
                   {
                     "name": "actor_field",
                     "value": "id"
                   },
                   {
                     "name": "target_field",
                     "value": "recipient_id"
                   }
                 ]
               },
               {
                 "app_name": "guardian",
                 "namespace_name": "builtin",
                 "name": "target_does_not_have_role",
                 "parameters": [
                   {
                     "name": "role",
                     "value": "cake-express:cakes:birthday-cake"
                   }
                 ]
               }
             ],
             "relation": "AND",
             "permissions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "users",
                 "name": "manage-notifications"
               }
             ]
           }' \
       $MANAGEMENT_SERVER/capabilities/cake-express/users

*Example Organization* is now done with the join script
and is ready to start using Guardian with their application.

.. _registering-custom-conditions:

Registering custom conditions
-----------------------------

The Guardian comes with several built-in :term:`conditions <condition>`,
documented in the section :ref:`conditions`.

However, some :term:`apps <app>` need to write their own custom conditions,
and the :term:`Management API` provides an endpoint to facilitate this.
The endpoint requires knowledge of `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_.

Suppose that *Example Organization* tracks whether or not a user likes cakes or not,
and wants to provide the :term:`guardian app administrator <guardian app administrator>` with a condition
that allows them to opt users out of receiving a cake,
without knowing how :program:`Cake Express` stores their cake preferences.

:numref:`registering-custom-conditions-rego`
shows the Rego code for the custom condition.

.. code-block:: python
   :caption: Create custom condition with Rego
   :name: registering-custom-conditions-rego

   package guardian.conditions

   import future.keywords.if
   import future.keywords.in

   condition("cake-express:users:recipient-likes-cakes", _, condition_data) if {
       condition_data.target.old.attributes.recipient["likes_cakes"]
   } else = false

You can test this code in the `Rego Playground <https://play.openpolicyagent.org/>`_ provided by the Open Policy Agent.
:numref:`registering-custom-conditions-rego-playground` shows the code for the Playground.
Paste it into the *Editor* section.
Click the :guilabel:`Evaluate` button in the Rego Playground.
The *OUTPUT* section shows the result ``true``.

.. code-block::
   :caption: Test custom condition with Rego Playground
   :name: registering-custom-conditions-rego-playground

   package guardian.conditions

   import future.keywords.if
   import future.keywords.in

   condition("cake-express:users:recipient-likes-cakes", _, condition_data) if {
       condition_data.target.old.attributes.recipient["likes_cakes"]
   } else = false

   result := condition(
               "cake-express:users:recipient-likes-cakes",
               {},
               {"target":
                  {"old":
                     {"attributes":
                        {"recipient": {"likes_cakes": true}}
                     }
                  }
               }
             )

The code requires ``base64`` encoding before sending it to the API.
To create the ``base64`` encoding, apply the following steps:

#. Save your Rego code in a file.

#. Encode it with the command :samp:`base64 {$FILENAME}`.

#. Copy the ``base64`` encoded Rego code
   and paste it as value to the attribute ``code`` as shown in
   :numref:`registering-custom-conditions-base64`.

:numref:`registering-custom-conditions-base64`
shows how *Example Organization* creates a custom condition:

.. code-block:: bash
   :caption: Create custom condition for the app with ``base64`` encoding
   :name: registering-custom-conditions-base64

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "name": "recipient-likes-cakes",
             "display_name": "recipient likes cakes",
             "documentation": "True if the user recieving a cake likes cakes",
             "parameters": [],
             "code": "cGFja2FnZSBndWFyZGlhbi5jb25kaXRpb25zCgppbXBvcnQgZnV0dXJlLmtleXdvcmRzLmlmCmltcG9ydCBmdXR1cmUua2V5d29yZHMuaW4KCmNvbmRpdGlvbigiY2FrZS1leHByZXNzOnVzZXJzOnJlY2lwaWVudC1saWtlcy1jYWtlcyIsIF8sIGNvbmRpdGlvbl9kYXRhKSBpZiB7CiAgICBjb25kaXRpb25fZGF0YS50YXJnZXQub2xkLmF0dHJpYnV0ZXMucmVjaXBpZW50WyJsaWtlc19jYWtlcyJdCn0gZWxzZSA9IGZhbHNl"
           }' \
       $MANAGEMENT_SERVER/conditions/cake-express/users

:numref:`registering-custom-conditions-update-capability`
shows how *Example Organization* then updates the existing :term:`capability` for ordering cakes:

.. code-block:: bash
   :caption: Update existing capability with custom condition
   :name: registering-custom-conditions-update-capability

   $ curl -X PUT \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "display_name": "Cake Orderers can order cake",
             "role": {
               "app_name": "cake-express",
               "namespace_name": "cakes",
               "name": "cake-orderer"
             },
             "conditions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "users",
                 "name": "recipient-likes-cakes",
                 "parameters": []
               }
             ],
             "relation": "AND",
             "permissions": [
               {
                 "app_name": "cake-express",
                 "namespace_name": "cakes",
                 "name": "order-cake"
               }
              ]
           }' \
       $MANAGEMENT_SERVER/capabilities/cake-express/cakes/cake-orderer-can-order-cake

.. _authorization-api-quick-start:

Authorization API
=================

Before going through this section,
you must follow the instructions from the previous section
:ref:`management-api-quick-start`.

.. note::

   Code in this section isn't part of the join script.
   This means that it doesn't have access to the ``guardian-scripts`` client
   and the ``Administrator`` password.
   As part of the join script for your :term:`app`,
   create your own Keycloak client to use it with your app,
   that allows service accounts and requires a client secret.

   All examples in this section use a hypothetical Keycloak client that :program:`Cake Express` already has.
   To create your own Keycloak client,
   adapt the code in :numref:`create-keycloak-client-for-join-scripts`.

.. _listing-all-general-permissions:

Listing all general permissions
-------------------------------

:program:`Cake Express` has three tabs in the web interface:

* :guilabel:`Order a Cake`
* :guilabel:`Manage Existing Orders`
* :guilabel:`Settings`

Cake Express uses its own internal rules:

* The :guilabel:`Settings` tab is always available.

* :guilabel:`Order a Cake` is only available to users
  who can order cakes
  and have the ``cake-express:cakes:order-cake`` permission.

* :guilabel:`Manage Existing Orders` is only available to users
  who can manage all orders
  and have the ``cake-express:orders:manage-order`` permission.
  Users who can't manage all orders
  have to use the :guilabel:`Order a Cake` tab to see their own orders.

Ariel is a user with id ``ariel``.
She has the ``cake-express:cakes:cake-orderer`` :term:`role`.
Tristan has ordered her an anniversary cake,
because she has been with the *Happy Employees* company for 10 years.
It's also Ariel's birthday in two weeks,
so Carla has also ordered her a birthday cake.

Ariel logs into Cake Express,
and Cake Express needs to know which tabs to show Ariel.
So Cake Express asks the :term:`Authorization API`
for all :term:`capabilities <capability>` related to the ``cakes`` and ``orders`` namespaces:

.. code-block:: bash
   :caption: Retrieve all capabilities related to cakes and orders namespaces

   AUTHORIZATION_SERVER="$(hostname).$(ucr get domainname)/guardian/authorization"

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "namespaces": [
               {
                 "app_name": "cake-express",
                 "name": "cakes"
               },
               {
                 "app_name": "cake-express",
                 "name": "orders"
               }
             ],
             "actor": {
               "id": "ariel",
               "roles": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "cakes",
                   "name": "cake-orderer"
                 }
               ],
               "attributes": {}
             },
             "targets": [],
             "include_general_permissions": true,
             "extra_request_data": {}
           }' \
       $AUTHORIZATION_SERVER/permissions

.. note::

   Usually the *Authorization API* expects one or more targets to evaluate permissions.
   However, you can ask for ``general_permissions``,
   which means the *Authorization API* also evaluates all capabilities without a target.

   In the Cake Express example of the web interface tabs,
   there aren't specific objects like cakes to verify.
   You just want to know general permissions,
   so you set ``include_general_permissions`` to ``true``.

The *Authorization API* says that Ariel has one general permission: ``cake-express:cakes:order-cakes``.
This means that Cake Express shows her the :guilabel:`Order a Cake` tab,
but not the :guilabel:`Manage Existing Orders` tab.
Cake Express always shows the :guilabel:`Settings` tab.

.. _listing-all-target-permissions:

Listing all target permissions
------------------------------

Now Ariel wants to manage her cake notifications,
so she clicks on the :guilabel:`Settings` tab
and goes to the :guilabel:`Cake Notifications` section.

From the previous call to the API,
:program:`Cake Express` already knows
that Ariel doesn't have the ``cake-express:users:manage-notifications`` general permission for any cake.
But Ariel might be able to manage notifications for cakes she is associated with.
So Cake Express gathers a list of all cakes where Ariel is the recipient,
and asks the *Authorization API* for target permissions for those cakes:

.. code-block:: bash
   :caption: List all cakes associated with Ariel

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "namespaces": [
               {
                 "app_name": "cake-express",
                 "name": "users"
               }
             ],
             "actor": {
               "id": "ariel",
               "roles": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "cakes",
                   "name": "cake-orderer"
                 }
               ],
               "attributes": {
                 "id": "ariel"
               }
             },
             "targets": [
               {
                 "old_target": {
                   "id": "anniversary-cake-from-tristan",
                   "roles": [],
                   "attributes": {
                     "id": "anniversary-cake-from-tristan",
                     "orderer_id": "tristan",
                     "recipient_id": "ariel",
                     "notifications": true
                   }
                 }
               },
               {
                 "old_target": {
                   "id": "birthday-cake-from-carla",
                   "roles": [
                     {
                       "app_name": "cake-express",
                       "namespace_name": "cakes",
                       "name": "birthday-cake"
                     }
                   ],
                   "attributes": {
                     "id": "birthday-cake-from-carla",
                     "orderer_id": "carla",
                     "recipient_id": "ariel",
                     "notifications": true
                   }
                 }
               }
             ],
             "include_general_permissions": false,
             "extra_request_data": {}
           }' \
       $AUTHORIZATION_SERVER/permissions

.. note::

   :term:`Targets <target>` for the *Authorization API* can verify the ``old_target``,
   which is the original state of the target,
   and the ``new_target``,
   which is the updated state of the target.

   In the case of showing Ariel which cakes she can manage,
   the cakes haven't changed,
   so the request only needs to supply the ``old_target``.

The *Authorization API* shows
that Ariel has ``cake-express:users:manage-notifications`` permissions for the anniversary cake from Tristan,
but no permissions for the birthday cake from Carla.
So :program:`Cake Express` only shows Ariel the anniversary cake from Tristan.

.. _checking-specific-permissions:

Checking specific permissions
-----------------------------

When Ariel turns notifications off for the anniversary cake,
:program:`Cake Express` makes a confirmation verification
to make sure she can manage notifications on the cake:

.. code-block:: bash

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{
             "namespaces": [
               {
                 "app_name": "cake-express",
                 "name": "users"
               }
             ],
             "actor": {
               "id": "ariel",
               "roles": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "cakes",
                   "name": "cake-orderer"
                 }
               ],
               "attributes": {
                 "id": "ariel"
               }
             },
             "targets": [
               {
                 "old_target": {
                   "id": "anniversary-cake-from-tristan",
                   "roles": [],
                   "attributes": {
                     "id": "anniversary-cake-from-tristan",
                     "orderer_id": "tristan",
                     "recipient_id": "ariel",
                     "notifications": true
                   }
                 },
                 "new_target": {
                   "id": "anniversary-cake-from-tristan",
                   "roles": [],
                   "attributes": {
                     "id": "anniversary-cake-from-tristan",
                     "orderer_id": "tristan",
                     "recipient_id": "ariel",
                     "notifications": false
                   }
                 }
               }
             ],
             "targeted_permissions_to_check": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "users",
                   "name": "manage-notifications"
                 }
               ],
               "general_permissions_to_check": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "users",
                   "name": "manage-notifications"
                 }
               ],
             "extra_request_data": {}
           }' \
       $AUTHORIZATION_SERVER/permissions/check

The *Authorization API* says
that Ariel doesn't have general permissions to manage notifications,
but she does have permissions for all targets.
So :program:`Cake Express` saves her updated notification settings,
and Ariel doesn't receive notifications about her anniversary cake.
