.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

###############
Guardian manual
###############

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :numbered:
   :hidden:

   what-is-the-guardian
   installation
   configuration
   troubleshooting
   management-ui
   management-and-authorization-api
   developer-quick-start
   limitations

.. toctree::
   :hidden:

   conditions
   glossary
   changelogs

Managing user permissions for a Univention Corporate Server (UCS) system is difficult and time-consuming.
Historically, it has required knowledge of access control lists (ACLs),
and applications have usually hard-coded permissions
to specific roles such as the domain administrator.

The Guardian provides an alternative to this system,
where :term:`applications <app>` can register user permissions,
which UCS system administrators can then manage
and organize in roles with an easy-to-use web interface.
The :term:`applications <app>` in turn can then query the Guardian
for authorization questions regarding specific :term:`actors <actor>`
and enforce app specific behavior in accordance with the administrator's configuration.

For example, suppose that you run a business
where you have a human resources department (HR)
and an IT department.
You want your human resources department to have different access permissions
to installed applications than your IT department.
You may want to give permissions to the head of your IT department to manage email,
while only the head of HR can manage your vacation tracking application.

The Guardian provides a convenient way to manage these permissions,
for applications that support integration with the Guardian.

Welcome to the Guardian manual.
It explains how both UCS system administrators,
as well as, developers of applications for a UCS system,
can use the Guardian to manage
what users can do in applications.

.. _audience-for-this-manual:

Audience for this manual
========================

The Guardian manual addresses the following audiences:

* :term:`Guardian Administrators <guardian administrator>`
* :term:`App Infrastructure Maintainers <app infrastructure maintainer>`
* :term:`App Developers <app developer>`

.. _guardian-administrators-audience:

Guardian administrators
-----------------------

A Guardian administrator in the context of this manual is a superuser
who administers the Guardian after its installation,
as well as, manages :term:`apps <app>`
that integrate with the Guardian.
A :term:`Guardian administrator <guardian app administrator>`
is a subset of the guardian administrator role,
which has limited capabilities to manage specific apps within the Guardian.
Whenever this manual refers to an *admininstrator*,
it either refers to the superuser,
or a limited app administrator.

The :ref:`management-ui` section is for administrators.

This manual doesn't assume any specific technical knowledge
for administrators of the Guardian.
When possible, all instructions use a web browser.

.. note::

   Not all applications installed through the Univention App Center
   support the integration with the Guardian
   and can be managed through the Guardian.
   Refer to the manual of your specific application to see
   if it supports the Guardian.

.. _app-infrastructure-maintainers-audience:

App infrastructure maintainers
------------------------------

An app infrastructure maintainer in the context of this manual is a person
who is responsible for installing
and maintaining a UCS system
and applications installed from the Univention App Center.
This manual assumes some technical knowledge for app infrastructure maintainers,
such as the ability to use the command line and read log files.

The most relevant chapters
for app infrastructure maintainers
are the following ones:

* :ref:`installation`
* :ref:`configuration`
* :ref:`troubleshooting`

.. _app-developers-audience:

App developers
--------------

An app developer in the context of this manual is a person
in a company, or organization
who develops either applications
installed through the Univention App Center,
or a third-party external service provider
that in some way connects to a UCS system
to provide services to users
within that system, for example,
using the
`UCS\@school ID Connector <https://docs.software-univention.de/ucsschool-id-connector/index.html>`_.

An :term:`app` is either an App Center application
or a third-party external service provider,
that integrates with the Guardian.

This manual presumes that app developers have high technical knowledge,
including using a command line, writing code for software, and making calls to an API.

The most relevant chapters for app developers are the following ones:

* :ref:`management-api-and-authorization-api`
* :ref:`developer-quick-start`
* :ref:`conditions`
