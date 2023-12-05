.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _what-is-the-guardian:

*********************
What is the Guardian?
*********************

The Guardian provides an authorization service for apps used with a UCS system.
:term:`Authorization<authorization>` means confirmation of a user's access to
some resource, for example the ability to modify a user's data, export data
from a system, or view a web page. It is important to note that the Guardian itself
only informs about the results of any authorization request. The :term:`app` has to
enforce the result of any authorization itself.

.. note::

   The Guardian does not provide :term:`authentication`, confirmation that a
   user is who they claim to be. You can use Keycloak or another service to
   have a user log in, i.e., authenticate, and then use the Guardian to find
   out what the user is allowed to do.

.. _guardian-apps:

Guardian apps
=============

The authorization service consists of three applications that are installed
from the UCS App Center:

* :term:`Management API`
* :term:`Authorization API`
* :term:`Management UI`

At a minimum, you must install the Management API and the Authorization API.
The Management UI provides an optional user-friendly graphical interface for
the Management API. See the chapter on :ref:`Installation` for more information.


.. _introduction-to-the-management-api:

Management API
--------------

The Management API is a `REST <https://en.wikipedia.org/wiki/REST>`_ interface
for :term:`app developers<app developer>` to configure aspects of the Guardian
that their :term:`apps<app>` need in order to handle authorization. Apps should
run a `join script <https://docs.software-univention.de/developer-reference/latest/en/join/write-join.html#join-write>`_
during installation that hits the Management API to register with the Guardian
and set up any :term:`roles<role>`, :term:`permissions<permission>`, and other
elements that the app needs.

This API is intended for technical audiences such as app developers. For a more
user-friendly interface to manage the Guardian, please use the :ref:`management-ui`.

Please read the chapter on the :ref:`management-api-and-authorization-api` for
more information.

.. _introduction-to-the-authorization-api:

Authorization API
-----------------

The Authorization API is a `REST <https://en.wikipedia.org/wiki/REST>`_
interface that allows apps to check whether a given user or other
:term:`actor` has access to a resource that the app provides. The API can
answer the following questions:

#. Given a user and a :term:`target` resource, what is the user allowed to do?
#. Given a user, a :term:`target` resource, and a proposed user behavior, is
   the user allowed to do that behavior?

This API is intended only for :term:`app developers<app developer>`. There is
no user-friendly interface for the Authorization API.

Please read the chapter on the :ref:`management-api-and-authorization-api` for
more information.

.. _introduction-to-the-managment-ui:

Management UI
-------------

The Management UI is a user-friendly web interface that allows
:term:`guardian admins<guardian admin>` and :term:`guardian app admins<guardian app admin>`
to configure what users in their UCS system are allowed to do once an :term:`app`
has been installed.

Please read the chapter on the :ref:`management-ui` for more information.

.. _what-does-the-guardian-do:

What does the guardian do?
==========================

Here is an example that illustrates how the Guardian works with each of the
three Guardian applications:

ACME Corporation develops an application, Cake Express, which can be installed
from the UCS App Center, and which allows employees to order cakes for company
events. ACME Corporation wants to allow administrators of Cake Express to have
some flexibility in who gets to order cakes, so they update Cake Express so
it integrates with the Guardian.

Alice works for Happy Employees, Inc. as the head IT person. When she installs
Cake Express on a UCS System, the
`join script <https://docs.software-univention.de/developer-reference/latest/en/join/write-join.html#join-write>`_
for Cake Express does the following using the :term:`Management API`:

#. Registers Cake Express as an :term:`app` with the Guardian, using the name
   ``cake-express``.
#. Creates a :term:`namespace` called ``cakes`` that the app will use to store
   its roles and permissions for managing cakes.
#. Creates a :term:`permission` in the ``cakes`` namespace that the app will
   check when people try to order cakes, ``cake-express:cakes:can-order-cake``.
#. Creates a :term:`role` to assign to people, ``cake-express:cakes:cake-orderer``.
#. Creates a role to assign to cakes, ``cake-express:cakes:birthday-cake``.

At the same time the join script registers Cake Express as an app, the Guardian
creates a special role to manage Cake Express, :code:`cake-express:default:app-admin`.
Alice thinks that managing Cake Express in the Guardian should be done by an
HR person, so she assigns the :code:`cake-express:default:app-admin` role to the HR
Manager, Bob, in UDM.

Bob can now log into the :term:`Management UI`, where he is allowed to see and
edit everything related to Cake Express in the Guardian. He decides to create
two :term:`capabilities<capability>`:

* Everyone in the HR department has the role ``happy-employees:departments:hr``,
  so everyone with this role gets the permission ``cake-express:cakes:can-order-cake``.
* For everyone not in the HR department, but who has the role
  ``cake-express:cakes:cake-orderer``, they are also allowed to order cake, but
  not if the cake is a birthday cake with the role
  ``cake-express:cakes:birthday-cake``, because only HR can order birthday cakes.

Bob asks Alice to give the ``cake-express:cakes:cake-orderer`` role to Carla,
the CEO, in UDM. Now Carla is allowed to order a cake, even though she's not
in the HR department.

Carla then logs into Cake Express, where she tries to order an anniversary cake
for Daniel, who has been at the company for 20 years. Cake Express sends
information about Carla, including her role and the name of her department and
the type of cake, to the :term:`Authorization API` to ask if she has the
permission ``cake-express:cakes:can-order-cake``. The Authorization API checks
the capability that Bob created and determines that yes, Carla has the
``cake-express:cake:cake-orderer`` role and the cake is not a birthday cake, so
she is allowed to order a cake.

.. _guardian-terminology:

Terminology
===========

This section covers some of the terminology used by the Guardian in more
detail.

.. _terminology-guardian-admin-and-guardian-app-admin:

Guardian admin and Guardian app admin
-------------------------------------

:term:`Guardian admins<guardian admin>` and
:term:`guardian app admins<guardian app admin>` are the two kinds of
people who can manage the Guardian.

.. note:: Technical Note

   A guardian admin has the :term:`role` ``guardian:builtin:super-admin``.
   This means that in UCS applications that have UDM integration, the user
   should have the ``guardianRole`` attribute include this string, i.e.,
   ``guardianRole=guardian:builtin:super-admin``.

Guardian admins can manage all aspects of the Guardian and integrated apps,
including:

* :term:`Apps<app>`
* :term:`Namespaces<namespace>`
* :term:`Roles<role>`
* :term:`Permissions<permission>`
* :term:`Conditions<condition>`
* :term:`Capabilities<capability>`
* :term:`Contexts<context>`

A guardian app admin has the ability to manage a single app that integrates
with the Guardian.

.. note:: Technical Note

   The :term:`role` for an app admin comes in the format ``<app-name>:default:app-admin``,
   with the ``<app-name>`` replaced by the unique identifier for the app. In
   our Cake Express example above, the app admin for Cake express has the role
   ``cake-express:default:app-admin``. In UCS applications that have UDM
   integration, the user should have the ``guardianRole`` attribute include this
   string, e.g., ``guardianRole=cake-express:default:app-admin``.

App admins can manage all of the aspects of their respective app:

* :term:`Namespaces<namespace>`
* :term:`Roles<role>`
* :term:`Permissions<permission>`
* :term:`Conditions<condition>`
* :term:`Capabilities<capability>`
* :term:`Contexts<context>`

.. note::

   Even if the permissions granted by the app admin role allow for all aspects of an app to be
   administrated, :term:`permissions<permission>` and :term:`conditions<condition>` cannot be
   managed with the :term:`Management UI`. These types of object are intended to be created and managed
   by the :term:`apps<app>` directly during the provisioning process. Within a UCS domain this
   would usually happen during the join script.

.. _terminology-guardian-app:

App
---

An app is an application installed from the UCS App Center, or a third-party
service that integrates with a UCS system, that uses the Guardian to determine
what an :term:`actor` is allowed to do.

In order to use the Guardian, apps first must register themselves using the
:term:`Management API` and a unique identifier. For example, the Cake Express
app registered itself with the identifier ``cake-express``. Everything in the
Guardian that is used by Cake Express will start with this identifier, such as
the role ``cake-express:cakes:can-order-cake``.

.. _terminology-guardian-actor:

Actor
-----

An actor is a user or machine account that wants to do something in an :term:`app`.

In the fictitious example above, Carla the CEO is an actor who wants to order
a cake in Cake Express.

The Guardian does not manage actors. It is the responsibility of the app and
:term:`app infrastructure maintainers<app infrastructure maintainer>` to manage
actors.

.. _terminology-guardian-target:

Target
------

A target is a resource that the :term:`actor` wants to access in an :term:`app`.

When Carla ordered an anniversary cake from Cake Express, the anniversary cake
was the target resource.

The Guardian does not manage targets. It is the responsibility of the app and
:term:`app infrastructure maintainers<app infrastructure maintainer>` to manage
targets.

.. _terminology-guardian-namespace:

Namespace
---------

A namespace is a convenient categorization within an :term:`app` for all
aspects of the app, such as :term:`roles<role>` and :term:`permissions<permission>`.

When Cake Express ran its join script at installation time, it created a
namespace, ``cakes``, to store everything else it created. Later, if it wants
to add some kind of user management feature, it might also add a namespace
called ``users``. Apps also always have the ``default`` namespace, which is
where the ``app-admin`` role for an app is always located.

All objects in the guardian are namespaced. When referencing the
``cake-express:cakes:cake-orderer`` role in Cake Express, the namespace is
the second field of the role string, ``cakes``.

.. _terminology-guardian-role:

Role
----

A role is a string that you assign to a user, group, or other database object,
in order to associate it with a :term:`capability`, either as an :term:`actor`
or as a :term:`target`.

In the Cake Express example, Alice could assign the role
``cake-express:cakes:cake-orderer`` to any person or even a machine account to
let that actor order a cake. Cake Express, in its own internal database,
might assign the role ``cake-express:cakes:birthday-cake`` to distinguish
between different kinds of cakes.

A role string always follows the format ``<app-name>:<namespace-name>:<role-name>``.

The Guardian does not assign roles to users or objects. Instead, an
:term:`app infrastructure maintainer` is responsible for assigning role strings
to the ``guardianRole`` attribute in UDM, or an :term:`app developer` must
assign roles to objects in their own internal database.

.. _terminology-guardian-permission:

Permission
----------

A permission is an action that an :term:`actor` can take in an :term:`app`.

In Cake Express, there is a permission ``cake-express:cakes:can-order-cake``,
that allows a user to order a cake within the Cake Express app.

Permissions are strings that are recognized by the code in an app, and used
to cause something to happen in the app. Some other examples of fictitious
permissions include:

* ``cake-express:orders:read-order``: Allows a user to read all orders.
* ``cake-express:orders:export-orders``: Allows a user to export all orders
  as an excel spreadsheet.
* ``cake-express:users:manage-email-notifications``: Allows a user to manage
  the email notifications that users receive from Cake Express.


.. note::

   The :term:`Management UI` does not have an interface to manage permissions.
   This can only be done in the Management API, and as such should only be
   managed by :term:`app developers<app developer>`.

   While a :term:`guardian admin` technically has the ability to create
   permissions, the app most likely won't recognize the permission and know
   what to do with it.

A permission is a required component of a :term:`capability`.

.. _terminology-guardian-condition:

Condition
---------

A condition is a criterion under which a :term:`permission` applies.

Cake Express might have a permission :code:`cake-express:cakes:can-add-candles`
that only applies if the condition is met that the cake has the role
:code:`cake-express:default:birthday-cake`.

.. note::

   The :term:`Management UI` does not have an interface to manage conditions.
   This can only be done in the Management API, and
   :term:`app developers<app developer>` are most likely to manage them.

   While a :term:`guardian admin` technically has the ability to create
   conditions, this requires knowledge of how to write
   `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_
   code.

A condition is an optional component of a :term:`capability`.

.. _terminology-guardian-capability:

Capability
----------

Capabilities are one of the more complicated aspects of the Guardian to
explain, but they are also the key to how the :term:`Authorization API` can
answer the question of what a user or other :term:`actor` is allowed to do
in an :term:`app`.

A capability is one or more :term:`permissions<permission>`, optionally
combined with one or more :term:`conditions<condition>` that modify when the
permission applies. A capability is then assigned to a :term:`role` to determine
what an actor with that role is allowed to do.

The simplest capability consists of a single permission. In the Cake Express
example, everyone with the ``happy-employees:department:hr`` role is assigned a
capability with a single permission, ``cake-express:cakes:can-order-cake``.

A more complex capability might include a permission plus a condition. In the
Cake Express example, everyone with the ``cake-express:cakes:cake-orderer``
role has the permission ``cake-express:cakes:can-order-cake``, provided
the condition that the :term:`target` cake does not have the role
``cake-express:cakes:birthday-cake``.

If there is more than one condition, the conditions are joined by a relation,
either :guilabel:`AND` or :guilabel:`OR`. With :guilabel:`AND`, all conditions
must apply: the user gets permissions if the target does not have the birthday
cake role *AND* the target cake is not marked as a "top-tier" style cake. With
:guilabel:`OR`, any condition can apply: the user gets permissions if they made
the cake order *OR* the cake is an anniversary cake.

.. _terminology-guardian-context:

Context
-------

A context is an additional tag that can be applied to a :term:`role`, to make
it only apply in certain circumstances.

For example, Happy Employees, Inc. has two different offices, London and Berlin.
They have the party-planner role, and Daniel is the party-planner for London
and Erik is the party-planner for Berlin. ACME sets up a :term:`capability`
that says that a party-planner can order a cake, but only for the office context
where they are a party-planner. So Erik can't order a cake for London, and
Daniel can't order a cake for Berlin.

Not all :term:`apps<app>` support contexts. Please check with the
:term:`app developer` for your app, to see if they support contexts.
