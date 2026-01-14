.. _changelog:

**********
Changelogs
**********

This section lists the changes to the Guardian components organized by
component and version of the app.

Authorization API
=================

Version 3.0.4 (2026-04-15)
--------------------------

* Update container images.

Version 3.0.3 (2025-12-16)
--------------------------

* Update sub-dependencies to their latest versions.

Version 3.0.2 (2025-12-15)
--------------------------

* Update dependencies to their latest versions.

Version 3.0.1 (2025-07-10)
--------------------------

* All Guardian apps are now available for UCS version 5.2-2.

Version 3.0.0 (2024-12-16)
--------------------------

* The Authorization API now uses the UDM attributes ``guardianRoles`` and
  ``guardianInheritedRoles`` instead of ``guardianRole``.

Version 2.0.3 (2024-04-18)
--------------------------

* The app installation has been simplified and doesn't need additional steps anymore.

Version 2.0.2 (2024-03-26)
--------------------------

* Add service entry for Guardian Authorization API to host server in UDM.

Version 2.0.1 (2024-01-22)
--------------------------

* Fix a problem, where contexts are not processed correctly.

Version 2.0.0 (2024-01-15)
--------------------------

* Remove App Center settings containing secrets:

  * :envvar:`guardian-management-api/oauth/keycloak-client-secret`
  * :envvar:`guardian-authorization-api/udm_data/username`

* Use Machine Account for UDM access.

* The application now only allows installation on the UCS system roles
  Primary Directory Node and Backup Directory Node.

* Fix container startup behavior.

* Update Keycloak configuration.

Version 1.1.0 (2023-12-22)
--------------------------

* Remove obsolete App Center settings.

* Migrate Docker image to UCS base image.

Version 1.0.0 (2023-12-11)
--------------------------

* Initial release.


Management API
==============

Version 3.0.4 (2026-01-15)
--------------------------

* Add condition to test the value of an actor attribute.

* Update container images.

Version 3.0.3 (2025-12-16)
--------------------------

* Update sub-dependencies to their latest versions.

Version 3.0.2 (2025-12-15)
--------------------------

* Update dependencies to their latest versions.

Version 3.0.1 (2025-07-10)
--------------------------

* All Guardian apps are now available for UCS version 5.2-2.

Version 3.0.0 (2024-12-16)
--------------------------

* Breaking change in the Authorization API

Version 2.0.2 (2024-04-18)
--------------------------

* The app installation has been simplified and doesn't need additional steps anymore.

Version 2.0.1 (2024-03-26)
--------------------------

* Add service entry for Guardian Management API to host server in UDM.
* Fix a bug where the permissions of a target could not be returned, if the ``old_target`` was empty.

Version 2.0.0 (2024-01-15)
--------------------------

* Fix ordering of condition parameters.

* Remove App Center settings containing secrets:
  :envvar:`guardian-management-api/oauth/keycloak-client-secret`

* Fix container startup behavior.

* Update Keycloak setup.

Version 1.1.0 (2023-12-22)
--------------------------

* Remove obsolete App Center settings.
* Rename App Center setting for *Management API* Keycloak client secret.
* Migrate docker image to UCS base image.

Version 1.0.0 (2023-12-11)
--------------------------

* Initial release.

Management UI
==============

Version 3.0.4 (2026-01-15)
--------------------------

* Update container image.

Version 3.0.3 (2025-12-16)
--------------------------

* Update sub-dependencies to their latest versions.

Version 3.0.2 (2025-12-15)
--------------------------

* Update dependencies to their latest versions.

Version 3.0.1 (2025-07-10)
--------------------------

* All Guardian apps are now available for UCS version 5.2-2.

Version 3.0.0 (2024-12-16)
--------------------------

* Breaking change in the Authorization API
* Add compatibility for Keycloak versions 25 and up.

Version 2.0.1 (2024-03-26)
--------------------------

* Fix a problem which affected all icons in the interface.

Version 2.0.0 (2024-01-15)
--------------------------

* Fix container startup behavior.
* Update Keycloak configuration.
* Set correct language for accessibility features.

Version 1.1.0 (2023-12-22)
--------------------------

* Remove obsolete App Center settings.
* Migrate docker image to UCS base image.

Version 1.0.0 (2023-12-11)
--------------------------

* Initial release.

Guardian Manual
===============

Version 2.0 (2024-01-15)
------------------------

* The app installation has been simplified and doesn't need additional steps anymore.
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

Version 1.1 (2023-12-22)
------------------------

* Rename App Center setting for *Management API* Keycloak client secret.

Version 1.0 (2023-12-22)
------------------------

* Initial release.
