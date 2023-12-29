.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

********
Releases
********

This chapter describes the process of releasing the different components of the Guardian and is specific to the
internal tools and structures of Univention.

Versioning
==========

The components of the Guardian are versioned following `Semantic Versioning <https://semver.org/>`_.

The documentation of the Guardian follows semantic versioning as well, but omits the patch level version number.
This means that the Guardian Manual in version ``1.1`` is valid for all components of version ``1.1.x``.

Guardian Management API
=======================

The Guardian Management API is a docker compose app in the Univention App center. The following steps have to be observed
to release a new version of the app:

#. Ensure a merge stop on the main branch during the duration of the release
#. Ensure the correct version of the component in all places.

   * The version in ``management-api/pyproject.toml``
   * The version of the migration folder in ``management-api/alembic`` if a new one was added
   * The app center version in ``appcenter-management/ini``
   * The version in the App center's `provider portal <https://provider-portal.software-univention.de>`_

#. Create the tag ``management-api-$VERSION`` on the latest commit on main to mark the correct release.
#. Copy the docker image referenced in the compose file to the public docker registry.

   For that to work, use `this jenkins job <https://univention-dist-jenkins.k8s.knut.univention.de/job/UCS-5.0/job/Apps/job/guardian-management-api/job/App%20Autotest%20MultiEnv/>`_
   and run it. Make sure to only run the ``docker-update/s4`` job. This will publish the image and modify the compose file.

   .. warning::
      If there are any commits on main that trigger the ``management_app_to_test_appcenter`` job, the changes made by this
      jenkins job are overwritten.

#. The following steps require the correct app center id to proceed. You can find it by examining the
   `ini files <https://appcenter-test.software-univention.de/meta-inf/5.0/guardian-management-api/>`_. Search for the one
   that corresponds with the app version you want to release. This will be your ``$APP_ID``.
#. To release the app, run the following commands on :guilabel:`omar`:

   .. code-block:: bash

      APP_ID = guardian-management-api_20231222153016
      cd /var/univention/buildsystem2/mirror/appcenter
      ./copy_from_appcenter.test.sh 5.0
      ./copy_from_appcenter.test.sh 5.0 $APP_ID
      sudo update_mirror.sh -v appcenter

#. Verify the app files were released `here <https://appcenter.software-univention.de/meta-inf/5.0/guardian-management-api/>`_
   and `there <https://appcenter.software-univention.de/univention-repository/5.0/maintained/component/>`_.
#. Verify the release with a test installation/update.

Guardian Authorization API & Guardian Management UI
===================================================

The release of the Authorization API and Management UI closely follow the instructions for the Management API.

Guardian Manual
===============

The release of the Guardian Manual is mostly automated, but contains a couple of manual steps:

#. Ensure the correct version in the ``DOC_TARGET_VERSION`` environment variable of the gitlab pipeline.
#. If a documentation release is desired, manually trigger the ``docs-merge-to-one-artifact`` pipeline job on the main branch.
#. The following job ``docs-create-production-merge-request`` creates a new merge request in the
   `docs.univention.de <https://git.knut.univention.de/univention/docs.univention.de>`_ repository, which is automatically
   merged once the pipeline passes. At this point the documentation is publicly available.

   .. warning::
      If you release a new version, it is important to cancel the automatic merge of the merge request and fix the symlink
      for the ``latest`` version, before merging.

#. If you release a new version, you also have to update the navigation in the `docs-overview-pages <https://git.knut.univention.de/univention/documentation/ucs-doc-overview-pages>`_
   repository. The necessary changes can be derived from this `MR <https://git.knut.univention.de/univention/documentation/ucs-doc-overview-pages/-/merge_requests/26/>`_.
