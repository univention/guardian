.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _developer-quick-start:

*********************
Developer quick start
*********************

.. note::

   This is a highly technical topic,
   and is primarily geared towards :term:`app developers<app developer>` who want to integrate an :term:`app` with the Guardian.
   Familiarity with using the command line, working with an API,
   and writing code is necessary to understand this chapter.

   You should also be familiar with:

   * `Documentation for App Center Providers <https://docs.software-univention.de/app-center/latest/en/contents.html>`_
   * `Manual for Developers <https://docs.software-univention.de/developer-reference/latest/en/contents.html>`_

This section provides a walk-through of the steps necessary to integrate an :term:`app` with the Guardian.

ACME Corporation is an :term:`app developer` who creates Cake Express,
which allows people to order cakes for company events,
and which can be installed from the Univention App Center.
They want to integrate Cake Express with the Guardian.

.. note::

   The example scripts assume that:

   * The app is installed on the same server as the Management API, and
   * The app is installed on the same server as the Keycloak server.

   If either of these two things is not true,
   you will need to find a way for the UCS :term:`app infrastructure maintainer` to communicate their locations to the script at run time.

.. _management-api-quick-start:

Management API
==============

.. _getting-a-keycloak-token:

Getting a Keycloak token
------------------------

The first thing that ACME Corporation needs to do is to write a join script for their :term:`app`.
This app will need to interact with the :term:`Management API`,
and to do this the join script must get a token from `Keycloak <https://docs.software-univention.de/keycloak-app/latest/#doc-entry>`_ to authenticate all calls to the API.

Here are the variables you need to get a token:

.. code-block:: bash

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

   In a typical join script, the ``--binduser``, ``--bindpwd``, and ``--bindpwdfile`` are available,
   which specify an administrator user,
   and either a password or a file for parsing the password.

   The example above assumes that the join script has already parsed these
   parameters into ``binduser`` and ``bindpwd`` variables.

You can retrieve the token with:

.. code-block:: bash

   token=$(curl -d "client_id=$CLIENT_ID" \
        -d "username=$binduser" \
        -d "password=$bindpwd" \
        -d "grant_type=password" \
        $KEYCLOAK_URL | sed 's/.*"access_token":"\([[:alnum:]\.-_-]*\)".*/\1/')

The ``token`` is referenced in all commands for subsequent sections.
You may need to refresh the token several times,
if you are entering commands manually.

.. _registering-an-app:

Registering an app
------------------

ACME Corporation now needs to let the Guardian know about its :term:`app`, Cake Express.
To do this, it needs to take the token from the :ref:`previous section<getting-a-keycloak-token>`
and make a request to the :term:`Management API`.

.. code-block:: bash

   MANAGEMENT_SERVER="$(hostname).$(ucr get domainname)/guardian/management"

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cake-express", "display_name":"Cake Express"}' \
       $MANAGEMENT_SERVER/apps/register

.. note::

   All names in Guardian are lower-case ASCII alphanumeric with either
   underscores or hyphens. The encoding for display names is only limited by
   the character support for the PostgreSQL database that Guardian uses.

ACME Corporation is now ready to start setting up the Guardian to work with Cake Express.

.. _registering-namespaces:

Registering namespaces
----------------------

A :term:`namespace` is just a handy categorization to store everything that an :term:`app` wants to use in Guardian,
like :term:`roles<role>` and :term:`permissions<permission>`.

Every app gets a ``default`` namespace to use.
But ACME Corporation wants to manage three different facets of Cake Express:

* ``cakes``: Category for everything related to what is actually being sold.
* ``orders``: Category for administration of orders.
* ``users``: Category for managing other users of Cake Express.

Later, ACME Corporation will create some roles in each of these namespaces for
doing tasks in Cake Express.

Here is how ACME Corporation creates these namespaces:

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cakes", "display_name":"Cakes"}' \
       $MANAGEMENT_SERVER/namespaces/cake-express

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"orders", "display_name":"Orders"}' \
       $MANAGEMENT_SERVER/namespaces/cake-express

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"users", "display_name":"Users"}' \
       $MANAGEMENT_SERVER/namespaces/cake-express

.. _registering-roles:

Registering roles
-----------------

ACME Corporation wants to create three different :term:`roles<role>` for users of Cake Express:

* ``cake-express:cakes:cake-orderer``: Someone who can order cakes from Cake Express.
* ``cake-express:orders:finance-manager``: Someone who manages the expenses for the orders.
* ``cake-express:users:user-manager``: Someone who manages other users within Cake Express.

ACME Corporation also wants to create a role for some of their cakes:

* ``cake-express:cakes:birthday-cake``: A cake just for employee birthdays.

Each role above consists of the following parts, separated by a ``:``:

* :term:`app`: e.g., ``cake-express``
* :term:`namespace`: e.g., ``cakes``
* role name: e.g., ``cake-orderer``

Here is how ACME Corporation creates these roles:

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cake-orderer", "display_name":"Cake Orderer"}' \
       $MANAGEMENT_SERVER/roles/cake-express/cakes

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"finance-manager", "display_name":"Finance Manager"}' \
       $MANAGEMENT_SERVER/roles/cake-express/orders

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"user-manager", "display_name":"User Manager"}' \
       $MANAGEMENT_SERVER/roles/cake-express/users

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"birthday-cake", "display_name":"Birthday Cake"}' \
       $MANAGEMENT_SERVER/roles/cake-express/cakes

.. _registering-permissions:

Registering permissions
-----------------------

ACME Corporation wants to provide some :term:`permissions<permission>` that define what users of Cake Express want to do:

* ``cake-express:cakes:order-cake``: Users with this permission are allowed to order cakes.
* ``cake-express:orders:cancel-order``: Users can cancel a cake order.
* ``cake-express:users:manage-notifications``: Users can manage cake notifications.

Here is how ACME Corporation creates these permissions:

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"order-cake", "display_name":"order cake"}' \
       $MANAGEMENT_SERVER/permissions/cake-express/cakes

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"cancel-order", "display_name":"cancel order"}' \
       $MANAGEMENT_SERVER/permissions/cake-express/orders

.. code-block:: bash

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $token" \
       -d '{"name":"manage-notifications", "display_name":"manage notifications"}' \
       $MANAGEMENT_SERVER/permissions/cake-express/users

.. _registering-capabilities:

Registering capabilities
------------------------

Finally, ACME Corporation wants to define some default :term:`capabilities<capability>` for their applications.
The :term:`guardian app admin` that installs Cake Express can change these later,
but these default capabilities make it easier for Cake Express to work out of the box.

They want to create:

#. Users with the ``cake-orderer`` role are allowed to order cakes.
#. Users with the ``finance-manager`` role, or the person who ordered the cake, have the permission to cancel the cake order.
#. Users with the ``user-manager`` role have the permission to manage cake notifications.
   Users can also manage their own notifications for cakes that are sent to them,
   except for notifications related to birthday cakes.

Here is how ACME Corporation creates the capability for ordering cake:

.. code-block:: bash

   curl -X POST \
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

Here is how ACME Corporation creates the capability for canceling an order.
This requires two ``POST`` requests in order to create it:

.. code-block:: bash

   curl -X POST \
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

   curl -X POST \
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

Here is how ACME Corporation creates the capability for managing notifications.
This also requires two ``POST`` requests in order to create it:

.. code-block:: bash

   curl -X POST \
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

   curl -X POST \
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

ACME Corporation is now done with the join script
and is ready to start using Guardian with their application.

.. _registering-custom-conditions:

Registering custom conditions
-----------------------------

The Guardian comes with several built-in :term:`conditions<condition>`,
which are documented in the chapter on :ref:`conditions`.

However, some :term:`apps<app>` need to write their own custom conditions,
and the :term:`Management API` provides an endpoint to facilitate this.
The endpoint requires knowledge of `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_.

Suppose that ACME Corporation tracks whether or not a user likes cake,
and wants to provide a simple condition to :term:`guardian app admins<guardian app admin>`
that allows them to opt users out of receiving a cake,
without having to know how Cake Express stores its cake preferences.

The Rego code for this condition is as follows:

.. code-block::

   package guardian.conditions

   import future.keywords.if
   import future.keywords.in

   condition("cake-express:users:recipient-likes-cakes", _, condition_data) if {
       condition_data.target.old.attributes.recipient["likes_cakes"]
   } else = false

You can test this code in the `Rego Playground <https://play.openpolicyagent.org/>`_ provided by the Open Policy Agent:

.. code-block::

   package guardian.conditions

   import future.keywords.if
   import future.keywords.in

   condition("cake-express:users:recipient-likes-cakes", _, condition_data) if {
       condition_data.target.old.attributes.recipient["likes_cakes"]
   } else = false

   result := condition("cake-express:users:recipient-likes-cakes", {}, {"target": {"old": {"attributes": {"recipient": {"likes_cakes": true}}}}})

Click the :guilabel:`Evaluate` button on the Rego Playground to receive a
``true`` result.

The code must be ``base64`` encoded before sending to the API.
Here is how ACME Corporation creates a custom condition:

.. code-block:: bash

   curl -X POST \
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

ACME Corporation then updates the existing :term:`capability` for ordering cakes:

.. code-block:: bash

   curl -X PUT \
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

Please follow the previous section for the :ref:`management-api-quick-start` before starting this section.

.. note::

   Code in this section is not part of the join script.
   This means that it does not have access to the ``guardian-scripts`` client and Administrator password.
   As part of the join script for your :term:`app`,
   you should create your own Keycloak client to use with your app,
   that allows service accounts and requires a client secret.

   All examples in this section use a hypothetical Keycloak client that Cake Express already has.

.. _listing-all-general-permissions:

Listing all general permissions
-------------------------------

Cake Express has three tabs in the web interface:

* :guilabel:`Order a Cake`
* :guilabel:`Manage Existing Orders`
* :guilabel:`Settings`

Cake Express uses its own internal rules:

* The :guilabel:`Settings` tab is always available.
* :guilabel:`Order a Cake` is only available to users who are allowed to order cakes
  and have the ``cake-express:cakes:order-cake`` permission.
* :guilabel:`Manage Existing Orders` is only available to users who can manage all orders
  and have the ``cake-express:orders:manage-order`` permission.
  Users who can't manage all orders have to use the :guilabel:`Order a Cake` tab to see their own orders.

Alice is a user with id ``alice``.
She has the ``cake-express:cakes:cake-orderer`` :term:`role`.
Bob has ordered her an anniversary cake,
because she has been with the Happy Employees company for 10 years.
It is also Alice's birthday in two weeks,
so Carol has also ordered her a birthday cake.

Alice logs into Cake Express,
and Cake Express needs to know which tabs to show Alice.
So Cake Express asks the :term:`Authorization API` for all :term:`capabilities<capability>` related to the ``cakes`` and ``orders`` namespaces:

.. code-block:: bash

   AUTHORIZATION_SERVER="$(hostname).$(ucr get domainname)/guardian/authorization"

   curl -X POST \
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
               "id": "alice",
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

   Usually the Authorization API expects one or more targets in order to evaluate permissions.
   However, you can ask for ``general_permissions``,
   which means the Authorization API will also evaluate all capabilities without a target.

   In the Cake Express example of the web interface tabs,
   we don't have specific objects like cakes to check.
   We just want to know general permissions,
   so we set ``include_general_permissions`` to ``true``.

The Authorization API says that Alice has one general permission, ``cake-express:cakes:order-cakes``.
This means that Cake express should show her the :guilabel:`Order a Cake` tab,
but not the :guilabel:`Manage Existing Orders` tab.
Cake Express always shows the :guilabel:`Settings` tab.

.. _listing-all-target-permissions:

Listing all target permissions
------------------------------

Now Alice wants to manage her cake notifications,
so she clicks on the :guilabel:`Settings` tab
and goes to the :guilabel:`Cake Notifications` section.

From the previous call to the API,
Cake Express already knows that Alice does not have the ``cake-express:users:manage-notifications`` general permission for any cake.
But Alice might be able to manage notifications for cakes she is associated with.
So Cake Express gathers a list of all cakes where Alice is the recipient,
and asks the Authorization API for target permissions for those cakes:

.. code-block:: bash

   curl -X POST \
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
               "id": "alice",
               "roles": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "cakes",
                   "name": "cake-orderer"
                 }
               ],
               "attributes": {
                 "id": "alice"
               }
             },
             "targets": [
               {
                 "old_target": {
                   "id": "anniversary-cake-from-bob",
                   "roles": [],
                   "attributes": {
                     "id": "anniversary-cake-from-bob",
                     "orderer_id": "bob",
                     "recipient_id": "alice",
                     "notifications": true
                   }
                 }
               },
               {
                 "old_target": {
                   "id": "birthday-cake-from-carol",
                   "roles": [
                     {
                       "app_name": "cake-express",
                       "namespace_name": "cakes",
                       "name": "birthday-cake"
                     }
                   ],
                   "attributes": {
                     "id": "birthday-cake-from-carol",
                     "orderer_id": "carol",
                     "recipient_id": "alice",
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

   :term:`Targets<target>` for the Authorization API can check the ``old_target``,
   which is the original state of the target,
   and the ``new_target``,
   which is the updated state of the target.

   In the case of showing Alice which cakes she can manage,
   the cakes haven't changed,
   so the request only needs to supply the ``old_target``.

The Authorization API shows that Alice has ``cake-express:users:manage-notifications`` permissions for the anniversary cake from Bob,
but no permissions for the birthday cake from Carol.
So Cake Express only shows Alice the anniversary cake from Bob.

.. _checking-specific-permissions:

Checking specific permissions
-----------------------------

When Alice turns notifications off for the anniversary cake,
Cake Express makes a confirmation check to make sure she can manage notifications on the cake:

.. code-block:: bash

   curl -X POST \
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
               "id": "alice",
               "roles": [
                 {
                   "app_name": "cake-express",
                   "namespace_name": "cakes",
                   "name": "cake-orderer"
                 }
               ],
               "attributes": {
                 "id": "alice"
               }
             },
             "targets": [
               {
                 "old_target": {
                   "id": "anniversary-cake-from-bob",
                   "roles": [],
                   "attributes": {
                     "id": "anniversary-cake-from-bob",
                     "orderer_id": "bob",
                     "recipient_id": "alice",
                     "notifications": true
                   }
                 },
                 "new_target": {
                   "id": "anniversary-cake-from-bob",
                   "roles": [],
                   "attributes": {
                     "id": "anniversary-cake-from-bob",
                     "orderer_id": "bob",
                     "recipient_id": "alice",
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

The Authorization API says that Alice doesn't have general permissions to manage notifications,
but she does have permissions for all targets.
So Cake Express saves the new notification settings,
and Alice will no longer get notifications about her anniversary cake.
