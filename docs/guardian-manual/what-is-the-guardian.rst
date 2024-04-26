.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _what-is-the-guardian:

*********************
What is the Guardian?
*********************

The Guardian provides an authorization service for apps used with a UCS system.
:term:`Authorization <authorization>` is the confirmation of a user's access to some resource,
such as the ability to modify a user's data,
export data from a system,
or view a web page.
It's important to note
that the Guardian itself only informs about the result of an authorization request.
The :term:`app` itself must enforce the result of any authorization.

.. note::

   The Guardian doesn't provide :term:`authentication`,
   that's the confirmation that a user is who they say they are.
   You can use :program:`Keycloak` or another service
   to have a user sign-in to authenticate,
   and then use the Guardian to find out what the user can do.

.. _guardian-apps:

Guardian apps
=============

The authorization service consists of three applications
installed from the UCS App Center:

* :term:`Management API`
* :term:`Authorization API`
* :term:`Management UI`

At a minimum, you must install the :program:`Management API`
and the :program:`Authorization API`.
The Management UI provides an optional graphical user interface for the Management API.
For more information, see section :ref:`Installation`.

.. _introduction-to-the-management-api:

Management API
--------------

The Management API is a `REST <https://en.wikipedia.org/wiki/REST>`_ interface
for :term:`app developers <app developer>` to configure aspects of the Guardian
that their :term:`apps <app>` need to handle authorization and permissions.
Apps should run a
:external+uv-dev-ref:ref:`join script <join-write>`
during installation
that accesses the :program:`Management API` to register with the Guardian
and set up all the :term:`roles <role>`,
:term:`permissions <permission>`,
and other items that the app needs.

The Management API is for technical audiences, such as app developers.
For a more user-friendly interface to manage the Guardian,
use the :ref:`management-ui`.

For more information,
see the section about the :ref:`management-api-and-authorization-api`.

.. _introduction-to-the-authorization-api:

Authorization API
-----------------

The Authorization API is a `REST <https://en.wikipedia.org/wiki/REST>`_ interface
that allows apps to verify
whether a given user
or other :term:`actor`
has access to a resource provided by the app.
The Authorization API answers the following questions:

#. Given a user and a :term:`target` resource,
   what's the user allowed to do?

#. Given a user,
   a :term:`target` resource,
   and a proposed user behavior,
   is the user allowed to do that behavior?

The Authorization API is only for :term:`app developers<app developer>`.
There is no other more user-friendly interface.

For more information,
read the section about the :ref:`management-api-and-authorization-api`.

.. _introduction-to-the-managment-ui:

Management UI
-------------

The Management UI is a user-friendly web interface
that allows :term:`guardian administrators <guardian administrator>`
and :term:`guardian app administrators <guardian app administrator>`
to configure
what users on their UCS system can do
after an administrators installed an :term:`app`.

For more information,
read the section about the :ref:`management-ui`.

.. _what-does-the-guardian-do:

What does the Guardian do?
==========================

.. The example uses gendered names, so it's totally fine to use gendered
   pronouns referring to the respective names. It makes reading easier for the
   reader.

This section provides an overview of the behavior of the Guardian.
A fictional example illustrates
how the Guardian works with each of the three Guardian applications.

*Example Organization* develops an application,
:program:`Cake Express`,
that administrators can install from the Univention App Center.
Cake Express allows employees to order cakes for company events.
*Example Organization* wants to give Cake Express administrators some flexibility in who can order cakes,
so they update Cake Express so it integrates with the Guardian.

Ariel works for *Happy Employees, Inc.* in the role of director of IT.
When she installs :program:`Cake Express` on a UCS system,
the :external+uv-dev-ref:ref:`join script <join-write>`
for Cake Express using the :term:`Management API` does the following:

#. Register :program:`Cake Express` as an :term:`app` with the Guardian,
   using the name ``cake-express``.

#. Create a :term:`namespace` called ``cakes``
   which the app uses to store its roles and permissions for managing cakes.

#. In the ``cakes`` namespace, create a :term:`permission`
   which the app verifies when people order cakes,
   ``cake-express:cakes:can-order-cake``.

#. Create a :term:`role` in the ``cakes`` namespace
   to assign to people,
   ``cake-express:cakes:cake-orderer``.

#. Create a role in the ``cakes`` namespace
   to assign to cakes,
   ``cake-express:cakes:birthday-cake``.

At the same time, the join script registers :program:`Cake Express` as an app.
The Guardian creates a special role to administer Cake Express,
``cake-express:default:app-admin``.
Ariel thinks that a person from the human resources department (HR) manages Cake Express in the Guardian.
So she assigns the role ``cake-express:default:app-admin`` to the HR manager, Tristan, in UDM.

Tristan can now sign in to the :term:`Management UI`,
where he can see and edit everything related to :program:`Cake Express` in the Guardian.
He decides to create two :term:`capabilities <capability>`:

* Everyone in the HR department has the role ``happy-employees:departments:hr``,
  so everyone with this role gets the permission ``cake-express:cakes:can-order-cake``.

* Anyone who isn't in HR
  but has the role ``cake-express:cakes:cake-orderer``
  is also allowed to order a cake,
  but not if it's a birthday cake with the role ``cake-express:cakes:birthday-cake``,
  because only HR can order birthday cakes.

Tristan asks Ariel to give Carla, the CEO, the role ``cake-express:cakes:cake-orderer`` in UDM.
Now Carla can order a cake,
even though she's not in HR.

Carla then signs in to :program:`Cake Express`,
where she tries to order an anniversary cake for Daniel,
who has been with the company for 20 years.
Cake Express sends information about Carla,
including her role, and the name of her department,
and the type of cake,
to the :term:`Authorization API` to ask
if she has the authorization ``cake-express:cakes:can-order-cake``.
The Authorization API verifies the capability
that Tristan created and determines that *yes*,
Carla has the role ``cake-express:cake:cake-orderer``
and the cake is not a birthday cake,
so she is allowed to order a cake.

.. _guardian-terminology:

Terminology
===========

This section covers some of the terminology used by the Guardian in more
detail.

.. _terminology-guardian-admin-and-guardian-app-admin:

Guardian administrator and Guardian app administrator
-----------------------------------------------------

:term:`Guardian administrator <guardian administrator>` and
:term:`guardian app administrator` are the two kinds of
people who can manage the Guardian.

.. admonition:: Technical Note

   A guardian administrator has the :term:`role` ``guardian:builtin:super-admin``.
   This means that in UCS applications which have UDM integration,
   the attribute ``guardianRoles`` of the user must include this string,
   for example ``guardianRoles=guardian:builtin:super-admin``. Another option
   is to add the user to a group which has the attribute ``guardianMemberRoles`` set to
   ``guardian:builtin:super-admin``.

Guardian administrators can manage all aspects of the Guardian and integrated apps,
including the following:

* :term:`Apps <app>`
* :term:`Namespaces <namespace>`
* :term:`Roles <role>`
* :term:`Permissions <permission>`
* :term:`Conditions <condition>`
* :term:`Capabilities <capability>`
* :term:`Contexts <context>`

A guardian app administrator has the ability to manage a single app
that integrates with the Guardian.

.. admonition:: Technical Note

   The :term:`role` for an app administrator comes in the format :samp:`{<app-name>}:default:app-admin`,
   with the :samp:`{<app-name>}` replaced by the unique identifier for the app.
   In the :program:`Cake Express` example from the previous section,
   the app administrator for Cake Express has the role ``cake-express:default:app-admin``.
   In UCS applications that have UDM integration,
   the user must have the attribute ``guardianRoles`` include this string,
   for example ``guardianRoles=cake-express:default:app-admin``.

Guardian app administrators can manage all of the following aspects of their respective app:

* :term:`Namespaces <namespace>`
* :term:`Roles <role>`
* :term:`Permissions <permission>`
* :term:`Conditions <condition>`
* :term:`Capabilities <capability>`
* :term:`Contexts <context>`

.. important::

   Even if the permissions granted by the Guardian app administrator role
   allow to manage all aspects of an app,
   the :term:`Management UI` can't manage :term:`permissions <permission>` and :term:`conditions <condition>`.
   Only :term:`apps <app>` can create and manage these types of objects directly during the provisioning process.
   Within a UCS domain, an app would typically create and manage these object types within the join script.

.. _terminology-guardian-app:

App
---

An app is an application installed from Univention App Center,
or a third-party service that integrates with a UCS system,
that uses the Guardian to determine what an :term:`actor` can do.

To use the Guardian,
apps first must register themselves using the :term:`Management API` and a unique identifier.
In the :ref:`Cake Express example <what-does-the-guardian-do>`,
the app :program:`Cake Express` registered itself with the identifier ``cake-express``.
Everything in the Guardian
that Cake Express uses, starts with this identifier,
such as the role ``cake-express:cakes:can-order-cake``.

.. _terminology-guardian-actor:

Actor
-----

An actor is a user or machine account that wants to do something in an :term:`app`.

In the :ref:`Cake Express example <what-does-the-guardian-do>`,
the CEO *Carla* is an actor who wants to order a cake in :program:`Cake Express`.

The Guardian doesn't manage actors.
It's the responsibility of the app
and :term:`app infrastructure maintainers <app infrastructure maintainer>` to manage actors.

.. _terminology-guardian-target:

Target
------

A target is a resource that the :term:`actor` wants to access in an :term:`app`.

In the :ref:`Cake Express example <what-does-the-guardian-do>`,
when *Carla* ordered an anniversary cake from :program:`Cake Express`,
the anniversary cake was the target resource.

The Guardian doesn't manage targets.
It's the responsibility of the app
and :term:`app infrastructure maintainers <app infrastructure maintainer>` to manage targets.

.. _terminology-guardian-namespace:

Namespace
---------

A namespace is a convenient categorization within an :term:`app`
for all aspects of the app,
such as :term:`roles <role>` and :term:`permissions <permission>`.
For example, an office suite might create an ``email`` namespace
in which to store :term:`roles <role>` and :term:`permissions <permission>` related to email.

In the :ref:`Cake Express example <what-does-the-guardian-do>`,
when :program:`Cake Express` ran its join script at install time,
it created the namespace ``cakes`` to store everything else it created.
Later, if it wants to add some kind of user management feature,
it might also add a namespace called ``users``.
Apps also always have the ``default`` namespace,
which is where the ``app-admin`` role for an app always resides.

All objects in the guardian have a namespace.
When referring to the role ``cake-express:cakes:cake-orderer`` in Cake Express,
the namespace is the second field of the role string, ``cakes``.

.. _terminology-guardian-role:

Role
----

A role is a string that you assign to a user, group, or other database object,
to associate it with a :term:`capability`,
either as an :term:`actor` or as a :term:`target`.
In a UCS domain this is usually done in UDM
and supported for user objects only.

In the :ref:`Cake Express example <what-does-the-guardian-do>`,
Ariel could assign the role ``cake-express:cakes:cake-orderer``
to any person or even a machine account to let that actor order a cake.
Cake Express, in its own internal database,
might assign the role ``cake-express:cakes:birthday-cake`` to distinguish between different kinds of cakes.

A role string always follows the format :samp:`{<app-name>}:{<namespace-name>}:{<role-name>}``.

The Guardian doesn't assign roles to users or objects.
Instead, an :term:`app infrastructure maintainer` is responsible for assigning role strings
to the ``guardianRoles`` attribute in UDM,
or an :term:`app developer` must assign roles to objects in their own internal database.

.. _terminology-guardian-permission:

Permission
----------

A permission is an action that an :term:`actor` can take in an :term:`app`.

In the :ref:`Cake Express example <what-does-the-guardian-do>`,
there is a permission ``cake-express:cakes:can-order-cake``,
that allows a user to order a cake within the :program:`Cake Express` app.

Permissions are strings that the code in an app recognizes,
and uses to cause something to happen in the app.

Some other examples of fictional permissions include:

``cake-express:orders:read-order``
   Allows a user to read all orders.

``cake-express:orders:export-orders``
   Allows a user to export all orders as a spreadsheet.

``cake-express:users:manage-email-notifications``
   Allows a user to manage the email notifications that users receive from Cake Express.

.. important::

   The :term:`Management UI` doesn't have a permissions management interface.
   Only :term:`app developers <app developer>` can manage permissions through the Management API.

   While a :term:`guardian administrator` technically has the ability to create permissions,
   the app most likely doesn't recognize the permission and know what to do with it.

A permission is a required component of a :term:`capability`.

.. _terminology-guardian-condition:

Condition
---------

A condition is a criterion by which a :term:`permission` applies.

In the :ref:`Cake Express example <what-does-the-guardian-do>`,
:program:`Cake Express` might have a permission ``cake-express:cakes:can-add-candles``
that applies only
if the condition is true
that the cake has the role ``cake-express:default:birthday-cake``.

A condition is an optional component of a :term:`capability`.

.. important::

   The :term:`Management UI` doesn't have an interface for managing conditions.
   Only :term:`app developers <app developer>` can manage conditions in the Management API.

   While a :term:`guardian administrator` technically has the ability to create conditions,
   this requires knowledge of how to write
   `Rego <https://www.openpolicyagent.org/docs/latest/policy-language/>`_
   code.

.. _terminology-guardian-capability:

Capability
----------

Capabilities are one of the more complicated aspects of the Guardian to explain,
but they're also the key to how the :term:`Authorization API` can answer the question
of what a user or an other :term:`actor` can do in an :term:`app`.

A capability is one or more :term:`permissions <permission>`,
optionally combined with one or more :term:`conditions <condition>`
that change when the permission applies.
A capability is then assigned to a :term:`role` to determine
what an actor with that role can do.

The simplest capability is a single permission.
In the :ref:`Cake Express example <what-does-the-guardian-do>`,
anyone with the role ``happy-employees:department:hr`` is assigned a
capability with the single permission ``cake-express:cakes:can-order-cake``.

A more complex capability might involve a permission plus a condition.
In the Cake Express example,
anyone with the role ``cake-express:cakes:cake-orderer``
has the permission ``cake-express:cakes:can-order-cake``,
provided the condition that the :term:`target` cake doesn't have the role ``cake-express:cakes:birthday-cake``.

If there is more than one condition,
a relation joins the conditions with Boolean operators,
either **AND** or **OR**.

AND
   With **AND**, all conditions must be true.
   The Guardian grants permission to the user
   if the target doesn't have the birthday cake role
   *AND* the target cake isn't marked as a "top-tier" style cake.

OR
   **OR** allows any condition to be true.
   The Guardian grants permission to the user
   if they placed the cake order *OR* the cake is an anniversary cake.

.. _terminology-guardian-context:

Context
-------

A context is an additional tag that the Guardian applies to a :term:`role`
so that it only applies in certain circumstances.

For example, *Happy Employees, Inc.* has two different offices, London and Berlin.
Persons in the offices have the party planner role.
Daniel is the party planner for London.
Erik is the party planner for Berlin.
*Example Organization* sets up a :term:`capability`
that says a party planner can order a cake,
but only for the office context where they're a party planner.
So Erik can't order a cake for London,
and Daniel can't order a cake for Berlin.

.. important::

   Not all :term:`apps <app>` support contexts.
   Validate with the :term:`app developer` for your app, to see if they support contexts.
