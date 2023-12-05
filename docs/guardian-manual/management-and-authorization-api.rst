.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _management-api-and-authorization-api:

************************************
Management API and Authorization API
************************************

.. note::

   This is a highly technical topic,
   and is primarily geared towards :term:`app developers<app developer>` who want to integrate an :term:`app` with the Guardian.
   Familiarity with using the command line and working with an HTTP API,
   is necessary to understand this chapter.

.. _introduction-to-the-management-and-authorization-apis:

Introduction
============

The :term:`Management API` and :term:`Authorization API` are the two
`REST <https://en.wikipedia.org/wiki/REST>`_
`APIs <https://en.wikipedia.org/wiki/API>`_ for the Guardian.

Please read the :ref:`developer-quick-start` for concrete examples of using the APIs.

.. _management-api:

Management API
==============

The :term:`Management API` is a general-purpose `CRUD <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_ interface for managing Guardian objects.
When installing a new :term:`app` that integrates with the Guardian,
the `join script <https://docs.software-univention.de/developer-reference/latest/en/join/write-join.html#join-write>`_ must register the app
and create any new Guardian elements that it needs, using this API.

Once the join script is complete,
the app has no more need to contact the Management API.
However, :term:`guardian admins<guardian admin>` and :term:`guardian app admins<guardian app admin>` may use this API to modify :term:`roles<role>` and :term:`capabilities<capability>` after installing the app.

.. _management-api-documentation:

API documentation
-----------------

Swagger documentation for the API is located at ``/guardian/management/docs`` on the server where the :term:`Management API` is installed.

The API requires authentication.
Click the :guilabel:`Authorize` button at the top of the page.
The default client does not require a ``client_secret``.
When logging in, please use the credentials of either a :term:`guardian admin` or a :term:`guardian app admin`.

.. note::

   Only the :term:`capabilities<capability>` have a ``DELETE`` endpoint.
   Please see the chapter on :ref:`limitations` for more information.

.. _guardian-naming-conventions:

Guardian naming conventions
---------------------------

When creating a new object in the :term:`Management API`,
the ``name`` for the object should always be lower-case ASCII alphanumeric,
with hyphens or underscores to separate words.

For example, if you want to create a :term:`role` for users who manage a pet store,
you might name the role ``pet-store-manager``.

With the exception of apps and :term:`namespaces<namespace>` themselves,
all objects belong to a namespace.
We often represent the full name of an object as a three-part string,
with each section separated by colons:

.. code-block::

   <app-name>:<namespace-name>:<object-name>

For example, if the ``pet-store-manager`` role mentioned above belongs to the namespace ``stores`` for the app ``inventory-manager``,
then the fully namespaced role is ``inventiory-manager:stores:pet-store-manager``.

.. _management-api-registering-an-app:

Registering an app
------------------

Before an :term:`app` can use the :term:`Management API`,
it needs to register itself at the ``/guardian/management/apps/register`` endpoint.

Registration looks like:

.. code-block:: bash

   MANAGEMENT_SERVER="$(hostname).$(ucr get domainname)/guardian/management"

   curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $keycloak_token" \
       -d '{"name":"my-app", "display_name":"My App"}' \
       $MANAGEMENT_SERVER/apps/register

.. note::

   There is another endpoint, ``/guardian/management/apps`` which will also create a new app.
   However, the ``register`` endpoint also does additional setup for the app,
   such as creating a :term:`guardian app admin` :term:`role` that can be used to manage the app.

   Unless you know what you are doing,
   please avoid the ``/guardian/management/apps`` endpoint.

After registration, an app must at the bare minimum register the :term:`permissions<permission>` that it needs.
However, other Guardian objects are optional and may be manually created by a :term:`guardian app admin` later.

.. _management-api-conditions:

Conditions
----------

When constructing a :term:`capability`,
the list of available :term:`conditions<condition>` is available with a ``GET`` to the ``/guardian/management/conditions`` endpoint.
Each condition provides a ``documentation`` string and a list of ``parameters`` it needs.

Please read the chapter on :ref:`conditions` for more information on Guardian's built-in conditions.

If the Guardian does not provide a condition that you need,
you can create it through the ``/guardian/management/conditions/{app-name}/{namespace-name}`` endpoint.
This requires a knowledge of `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_,
and the code must be ``base64`` encoded when submitting it to the Guardian.

Please see :ref:`registering-custom-conditions` in the :ref:`developer-quick-start` guide.

.. _management-api-contexts:

Contexts
--------

:term:`Contexts<context>` are a special feature of the Guardian that allows :term:`guardian admins<guardian admin>` to tell :term:`apps<app>` about where a :term:`role` applies.

For example, if Happy Employees installs the Cake Express app,
Happy Employees can create a ``london`` context and a ``berlin`` context,
which it includes with the ``cake-express:cakes:cake-orderer`` role.
Happy Employees can then create a :term:`capability<capability>` where users
can only order cakes for people in the same context.

Some of the built-in Guardian :term:`conditions<condition>` explicitly support contexts,
such as:

* :envvar:`target_has_same_context`
* :envvar:`target_has_role_in_same_context`
* :envvar:`target_does_not_have_role_in_same_context`

An app must explicitly support contexts
and send them as part of requests to the :term:`Authorization API`.
in order to use contexts within a capability.
Apps must specify in their documentation whether or not they support contexts.

.. _authorization-api:

Authorization API
=================

The :term:`Authorization API` helps an :term:`app` determine whether an :term:`actor` is authorized to perform a given action within the app.


.. _authorization-api-documentation:

API documentation
-----------------

Swagger documentation for the API is located at ``/guardian/authorization/docs`` on the server where the :term:`Authorization API` is installed.

The API requires authentication.
Click the :guilabel:`Authorize` button at the top of the page.
The default client does not require a ``client_secret``.

.. _authorization-api-endpoint-overview:

Endpoint overview
-----------------

There are four primary endpoints in the :term:`Authorization API`:

* ``/guardian/authorization/permissions``
* ``/guardian/authorization/permissions/with-lookup``
* ``/guardian/authorization/permissions/check``
* ``/guardian/authorization/permissions/check/with-lookup``

The first two endpoints answer the question
"What are all the :term:`permissions<permission>` an :term:`actor` has?".

The second two endpoints answer the question
"Does the user have a specific set of permissions?".
You must supply a list of permissions that you want to check.

In both cases, you must supply an actor,
and you may optionally supply :term:`targets<target>` that are used to answer these questions.

.. _authorization-api-with-lookup-endpoints:

About with-lookup endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some :term:`apps<app>` maintain all their own data in regards to :term:`actors<actor>` and :term:`targets<target>`.
This means that they do not need access to `UDM <https://docs.software-univention.de/developer-reference/latest/en/udm/index.html>`_ in order to check :term:`capabilities<capability>`.
The examples in the :ref:`developer-quick-start` all use endpoints without lookup.

However, endpoints ending in ``with-lookup`` will search for the actor and targets in UDM
and use the results in checking capabilities.
To use the UDM lookup feature, supply the LDAP ``dn`` as the ``id`` of the actor and targets.

You do not need to supply any ``attributes`` or ``roles`` in the request,
if you use the ``with-lookup`` endpoints.


.. _authorization-api-general-versus-target-permissions:

General permissions versus target permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :term:`Authorization API` endpoints allow an :term:`app` to evaluate :term:`permissions<permission>` for an :term:`actor`.

A general permission is a permission that exists,
regardless of whether there are any ``targets`` present in the API request.
When listing all permissions,
you must set ``include_general_permissions`` to ``true`` in the request,
if you want to see these permissions.
See the section on :ref:`listing-all-general-permissions` in the :ref:`developer-quick-start` guide for an example.

Target permissions require one or more :term:`targets<target>` to be present
in the ``targets`` field of the request.
See the section on :ref:`listing-all-target-permissions` in the :ref:`developer-quick-start` guide for an example.

.. _authorization-api-old-versus-new-target:

Old target versus new target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When sending ``targets`` to the :term:`Authorization API`,
a :term:`target` consists of an ``old_target`` and a ``new_target``.
The ``old_target`` represents the existing state of the target,
and the ``new_target`` represents the future state of the target.

For example, a :term:`condition` could check that the ``new_target`` user password is not the same as the ``old_target`` password.

If the :term:`app` doesn't care about an old and new state of the target,
then only the ``old_target`` is required.

All :ref:`built-in conditions<conditions>` check the ``old_target``.

.. _authorization-api-custom-endpoints:

Custom endpoints
----------------

The :term:`Authorization API` has an experimental endpoint,
``/guardian/authorization/{app-name}/{namespace-name}/{endpoint-name}``,
that allows an :term:`app` to define its own custom `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_ code to evaluate permissions.

The endpoint does not have UDM access,
so the app must supply all of its own data for :term:`actors<actor>` and :term:`targets<target>`.

This endpoint is not implemented yet, so please do not use it.
