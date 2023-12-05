.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

********
Glossary
********

.. glossary::

    actor
       A user or machine account that wants to access a :term:`target` in an
       :term:`app` in some way. For example, a user actor may want to read
       the email of another target user.

    app
       An application installed into a UCS system from the App Center, or a
       third-party service provider that integrates with the UCS system.
       Specifically, applications or service providers that integrate with the
       Guardian.

    app developer
       A person, company, or organization that develops software that is used
       with a UCS system, that integrates with the Guardian. This includes
       UCS App Center applications, as well as third-party service providers
       using a service connector.

    app infrastructure maintainer
       A person who installs and manages UCS systems.

    authentication
       Confirmation of a user's identity. The Guardian does not handle
       authentication.

    authorization
       Confirmation of the access that a user has. The Guardian's job is to
       handle authorization after a user is authenticated.

    Authorization API
       A `REST <https://en.wikipedia.org/wiki/REST>`_ interface that allows
       an :term:`app` to authorize an :term:`actor` to use features of the
       app.

    capability
       One or more :term:`permissions<permission>`, optionally combined with
       one or more :term:`conditions<condition>` that are joined by either
       an "AND" or "OR" relationship.

    condition
       A criterion under which a :term:`permission` applies.

    context
       An optional tag that modifies when a :term:`role` applies.

    guardian admin
       A user with the :code:`guardian:builtin:super-admin` :term:`role`, who
       can manage all aspects of the Guardian and any :term:`app` using the
       Guardian, including :term:`capabilities<capability>` for users and groups.

    guardian app admin
       A user with a :term:`role` ending in :code:`app-admin`, who can manage
       most aspects of an :term:`app`, including which
       :term:`capabilities<capability>` a user has for that app.

    Management API
       A `REST <https://en.wikipedia.org/wiki/REST>`_ interface that allows
       an :term:`app` or :term:`guardian admin` to manage the Guardian.

    Management UI
       A limited web interface that allows an :term:`guardian admin` or
       :term:`guardian app admin` to manage the Guardian.

    namespace
       A categorization of Guardian elements within an :term:`app`. For example,
       an office suite might create an :code:`email` namespace in which to
       store :term:`roles<role>` and :term:`permissions<permission>` related
       to email.

    permission
       An action that an :term:`actor` can take in a specific :term:`app`.

    role
      A string assigned to a user group, or object in order to use a
      :term:`capability`. In a UCS domain this is usually done in UDM and
      currently supported for user objects only.

    target
      A resource in an :term:`app` that an :term:`actor` wants to access.
      Used in determining which :term:`permissions<permission>` an actor has.
