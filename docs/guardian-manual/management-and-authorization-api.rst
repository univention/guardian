.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _management-api-and-authorization-api:

************************************
Management API and Authorization API
************************************

.. important::

   This section covers a highly technical topic.
   It addresses :term:`app developers <app developer>`
   who want to integrate an :term:`app` with the Guardian.
   Familiarity with using the command line
   and working with an HTTP API,
   is necessary to understand this section.

The :term:`Management API` and :term:`Authorization API` are the
`REST <https://en.wikipedia.org/wiki/REST>`_
`APIs <https://en.wikipedia.org/wiki/API>`_ for the Guardian.
Read the :ref:`developer-quick-start` for concrete examples of using the APIs.

.. _management-api:

Management API
==============

The :term:`Management API` is a general-purpose
`CRUD <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_
interface for managing Guardian objects.
When installing an :term:`app` that integrates with the Guardian,
the :external+uv-dev-ref:ref:`join script <join-write>` must register the app
and create any Guardian elements that it needs, using this API.

After the join script completes,
the app has no more need to contact the *Management API*.
However, :term:`guardian administrators <guardian administrator>` and :term:`guardian app administrators <guardian app administrator>`
may use this API
to modify :term:`roles <role>` and :term:`capabilities <capability>`.

.. _management-api-documentation:

API documentation
-----------------

OpenAPI/Swagger documentation for the API locates at ``/guardian/management/docs`` on the server
where you installed the :term:`Management API`.

The API requires authentication.
Click the :guilabel:`Authorize` button at the top of the page.
The default client doesn't require a ``client_secret``.
When signing in, use the credentials of either a :term:`guardian administrator` or a :term:`guardian app administrator`.

.. important::

   Only the :term:`capabilities <capability>` have a ``DELETE`` endpoint.
   For more information, see :ref:`limits-no-object-deletion-limitation`.

.. _guardian-naming-conventions:

Guardian naming conventions
---------------------------

When creating an object in the :term:`Management API`,
the ``name`` for the object must always use lower-case ASCII alphanumeric,
with hyphens or underscores to separate words.

For example, if you want to create a :term:`role` for users
who manage a pet store, you can name the role ``pet-store-manager``.

With the exception of apps and :term:`namespaces <namespace>` themselves,
all objects belong to a namespace.
This documentation often represent the full name of an object as a three-part string,
with each section separated by colons:
:samp:`{<app-name>}:{<namespace-name>}:{<object-name>}`

For example,
if the ``pet-store-manager`` role belongs to the namespace ``stores`` for the app ``inventory-manager``,
then the complete representation of the role is ``inventory-manager:stores:pet-store-manager``.

.. _management-api-registering-an-app:

Registering an app
------------------

Before an :term:`app` can use the :term:`Management API`,
it needs to register itself at the ``/guardian/management/apps/register`` endpoint.

:numref:`management-api-registering-an-app-code`
shows an example for registration.

.. code-block:: bash
   :caption: Register an app
   :name: management-api-registering-an-app-code

   $ MANAGEMENT_SERVER="$(hostname).$(ucr get domainname)/guardian/management"

   $ curl -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $keycloak_token" \
       -d '{"name":"my-app", "display_name":"My App"}' \
       $MANAGEMENT_SERVER/apps/register

After registration,
an app must at the bare minimum register the :term:`permissions <permission>` that it needs.
However, other Guardian objects are optional
and a :term:`guardian app administrator` may manually create them later.

.. caution::

   There is another endpoint, ``/guardian/management/apps`` that also creates an app.
   However, the ``register`` endpoint also does additional setup steps for the app,
   such as creating a :term:`guardian app administrator` :term:`role`
   that you can use to manage the app.

   Unless you know what you are doing,
   avoid using the ``/guardian/management/apps`` endpoint.

.. _management-api-conditions:

Conditions
----------

When constructing a :term:`capability`,
the list of available :term:`conditions <condition>` is available
with a ``GET`` request to the ``/guardian/management/conditions`` endpoint.
Each condition provides a ``documentation`` string and a list of ``parameters`` it needs.
For more information about the Guardian's built-in conditions,
refer to :ref:`conditions`.

If the Guardian doesn't provide a condition that you need,
you can create it through the :samp:`/guardian/management/conditions/{app-name}/{namespace-name}` endpoint.
This action requires the knowledge of `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_.
And you must submit the Rego code in ``base64`` encoding to the Guardian. For
more information, see :ref:`registering-custom-conditions` in the :ref:`developer-quick-start`.

.. _management-api-contexts:

Contexts
--------

:term:`Contexts <context>` are a special feature of the Guardian
that allows :term:`guardian administrators <guardian administrator>`
to tell :term:`apps <app>` about where a :term:`role` applies.

For example, if *Happy Employees* installs the :program:`Cake Express` app,
*Happy Employees* can create a ``london`` context and a ``berlin`` context
and populate them with the ``cake-express:cakes:cake-orderer`` role.
*Happy Employees* can then create a :term:`capability <capability>`
where users can only order cakes for people in the same context.

Some of the built-in Guardian :term:`conditions <condition>` explicitly support contexts,
such as:

* :envvar:`target_has_same_context`
* :envvar:`target_has_role_in_same_context`
* :envvar:`target_does_not_have_role_in_same_context`


.. important::

   An app must explicitly support contexts
   and send them as part of requests to the :term:`Authorization API`
   to use contexts within a capability.
   Apps must specify in their documentation whether or not they support contexts.

.. _authorization-api:

Authorization API
=================

The :term:`Authorization API` helps an :term:`app` determine
whether an :term:`actor` is authorized to perform a particular action within the app.

.. _authorization-api-documentation:

API documentation
-----------------

OpenAPI/Swagger documentation for the API locates at ``/guardian/authorization/docs`` on the server
where you installed the :term:`Authorization API`.

The API requires authentication.
Click the :guilabel:`Authorize` button at the top of the page.
The default client doesn't require a ``client_secret``.

.. _authorization-api-endpoint-overview:

Endpoint overview
-----------------

The :term:`Authorization API` has the following primary endpoints:

#. ``/guardian/authorization/permissions``
#. ``/guardian/authorization/permissions/with-lookup``
#. ``/guardian/authorization/permissions/check``
#. ``/guardian/authorization/permissions/check/with-lookup``

The endpoints 1-2 answer the question
"What are all the :term:`permissions <permission>` an :term:`actor` has?"

The endpoints 3-4 answer the question
"Does the user have a specific set of permissions?"
You must supply a list of permissions that you want to verify.

In both cases, you must specify an actor,
and you can optionally specify :term:`targets <target>`
for use in answering these questions.

.. _authorization-api-with-lookup-endpoints:

About ``with-lookup`` endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some :term:`apps <app>` maintain all their own data in regards to :term:`actors <actor>` and :term:`targets <target>`.
This means that they don't need access to
:external+uv-dev-ref:ref:`chap-udm`
to verify :term:`capabilities <capability>`.
All examples in the :ref:`developer-quick-start` use endpoints without lookup.

However, endpoints ending in ``with-lookup`` search for the actor and targets in UDM
and use the results in checking capabilities.
To use the UDM lookup feature,
supply the LDAP distinguished name ``dn`` as the ``id`` of the actor and targets.

You don't need to supply any ``attributes`` or ``roles`` in the request,
if you use the ``with-lookup`` endpoints.


.. _authorization-api-general-versus-target-permissions:

General permissions versus target permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :term:`Authorization API` endpoints allow an :term:`app`
to evaluate :term:`permissions <permission>` for an :term:`actor`.

A general permission is a permission that exists,
regardless of whether there are any ``targets`` present in the API request.
When listing all permissions,
you must set ``include_general_permissions`` to ``true`` in the request,
if you want to see these permissions.
For an example, see :ref:`listing-all-general-permissions` in the :ref:`developer-quick-start` guide.

Target permissions require one or more :term:`targets <target>`
to be present in the ``targets`` field of the request.
For an example, see :ref:`listing-all-target-permissions` in the :ref:`developer-quick-start` guide.

.. _authorization-api-old-versus-new-target:

Old target versus new target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When sending ``targets`` to the :term:`Authorization API`,
a :term:`target` consists of an ``old_target`` and a ``new_target``.
The ``old_target`` represents the existing state of the target,
and the ``new_target`` represents the future state of the target.

If the :term:`app` doesn't care about an old and new state of the target,
then the request only requires the ``old_target``.
All :ref:`built-in conditions <conditions>` evaluate the ``old_target``.

For example, a :term:`condition` could verify
that the ``new_target`` user password isn't the same as the ``old_target`` password.

.. _authorization-api-custom-endpoints:

Custom endpoints
----------------

The :term:`Authorization API` has an experimental endpoint,
:samp:`/guardian/authorization/{app-name}/{namespace-name}/{endpoint-name}`,
that allows an :term:`app`
to define its own custom `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_ code to evaluate permissions.

The endpoint doesn't have UDM access,
so the app must supply all of its own data
for :term:`actors <actor>` and :term:`targets <target>`.

.. important::

   Don't use this endpoint, because it isn't implemented.
