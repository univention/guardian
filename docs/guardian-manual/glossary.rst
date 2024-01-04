.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

********
Glossary
********

.. glossary::

   actor
     For the definition, see the terminology section :ref:`terminology-guardian-actor`.

   app
     For the definition, see the terminology section :ref:`terminology-guardian-app`.

   app developer
      A person, company, or organization that develops software
      that is used with a UCS system
      and that integrates with the Guardian.
      This includes Univention App Center applications,
      as well as third-party service providers using a service connector.

   app infrastructure maintainer
      A person who installs and manages UCS systems.

   authentication
      Confirmation of a user's identity.
      The Guardian doesn't handle authentication.

   authorization
      Confirmation of the access that a user has.
      The Guardian's job is to handle authorization after a user is authenticated.

   Authorization API
      A `REST <https://en.wikipedia.org/wiki/REST>`_ interface
      that allows an :term:`app` to authorize an :term:`actor`
      to use features of the app.

   capability
     For the definition, see the terminology section :ref:`terminology-guardian-capability`.

   condition
     For the definition, see the terminology section :ref:`terminology-guardian-condition`.

   context
     For the definition, see the terminology section :ref:`terminology-guardian-context`.

   guardian administrator
      A user with the ``guardian:builtin:super-admin`` :term:`role`,
      who can manage all aspects of the Guardian and any :term:`app`
      using the Guardian,
      including :term:`capabilities <capability>` for users and groups.

   guardian app administrator
      A user with a :term:`role` ending in ``app-admin``,
      who can manage most aspects of an :term:`app`,
      including which :term:`capabilities <capability>` a user has for that app.

   Management API
      A `REST <https://en.wikipedia.org/wiki/REST>`_ interface
      that allows an :term:`app` or :term:`guardian administrator` to manage the Guardian.

   Management UI
      A limited web interface that allows an :term:`guardian administrator`
      or :term:`guardian app administrator` to manage the Guardian.

   namespace
     For the definition, see the terminology section :ref:`terminology-guardian-namespace`.

   permission
     For the definition, see the terminology section :ref:`terminology-guardian-permission`.

   role
     For the definition, see the terminology section :ref:`terminology-guardian-role`.

   target
     For the definition, see the terminology section :ref:`terminology-guardian-actor`.
