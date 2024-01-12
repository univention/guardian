.. _changelog:

**********
Changelogs
**********

This section lists the changes to the Guardian components organized by
component and version of the app.

Authorization API
=================

2.0.0 (2024-01-15)
------------------

* It is no longer needed to provide a UDM password and username
* Removed App Center settings :envvar:`guardian-management-api/oauth/keycloak-client-secret`
  and :envvar:`guardian-authorization-api/udm_data/username`

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
* The Keycloak client secret must now be provided with a file
* Removed setting :envvar:`guardian-management-api/oauth/keycloak-client-secret`

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

* Add a new upgrade section: :ref:`_upgrade-on-ucs-primary-node`
* Remove obsolete settings from configuration documentation
* Clarified UCS node roles on which the applications can be installed

1.1 (2023-12-22)
----------------

* Rename App Center setting for *Management API* Keycloak client secret.

1.0 (2023-12-22)
----------------

* Initial release.
