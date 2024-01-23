.. _changelog:

**********
Changelogs
**********

This section lists the changes to the Guardian components organized by
component and version of the app.

Authorization API
=================

2.0.1 (2024-01-22)
------------------

* Fix a problem, where contexts are not processed correctly.

2.0.0 (2024-01-15)
------------------

* Remove App Center settings containing secrets.
    * Removed App Center settings :envvar:`guardian-management-api/oauth/keycloak-client-secret`
      and :envvar:`guardian-authorization-api/udm_data/username`.
* Use Machine Account for UDM access.
* The application can now only be installed on the UCS system roles primary and backup.
* Fix container startup behavior.
* Update Keycloak configuration.

1.1.0 (2023-12-22)
------------------

* Remove obsolete App Center settings.
* Migrate docker image to UCS base image.

1.0.0 (2023-12-11)
------------------

* Initial release.


Management API
==============

2.0.0 (2024-01-15)
------------------

* Fix ordering of condition parameters.
* Remove App Center settings containing secrets.
    * Removed setting :envvar:`guardian-management-api/oauth/keycloak-client-secret`.
* Fix container startup behavior.
* Update Keycloak setup.

1.1.0 (2023-12-22)
------------------

* Remove obsolete App Center settings.
* Rename App Center setting for *Management API* Keycloak client secret.
* Migrate docker image to UCS base image.

1.0.0 (2023-12-11)
------------------

* Initial release.

Management UI
==============

2.0.0 (2024-01-15)
------------------

* Fix container startup behavior.
* Update Keycloak configuration.
* Set correct language for accessibility features.

1.1.0 (2023-12-22)
------------------

* Remove obsolete App Center settings.
* Migrate docker image to UCS base image.

1.0.0 (2023-12-11)
------------------

* Initial release.

Guardian Manual
===============

2.0 (2024-01-15)
----------------

* Style improvements.
* Remove PDF version of the manual.
* Add a new upgrade section: :ref:`upgrade-on-ucs-primary-node`.
* Remove obsolete settings from configuration documentation.
* Clarify UCS node roles on which the applications can be installed.
* Add upgrade instructions.

Minor changes
~~~~~~~~~~~~~

2024-01-24
""""""""""

* Fix some broken references.

1.1 (2023-12-22)
----------------

* Rename App Center setting for *Management API* Keycloak client secret.

1.0 (2023-12-22)
----------------

* Initial release.
