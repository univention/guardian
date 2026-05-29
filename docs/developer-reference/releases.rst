.. Copyright (C) 2023-2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

********
Releases
********

This chapter describes how the Guardian components are released and is specific
to the internal tools and structures of Univention.

Since the migration to the shared ``common-ci`` pipeline, releases are driven by
GitLab CI and a single Git tag releases all three apps at once. The previous
Jenkins jobs, the per-app tags (``management-api_$VERSION`` and friends) and the
manual ``omar`` commands are no longer used.

Versioning
==========

The components of the Guardian are versioned following `Semantic Versioning
<https://semver.org/>`_.

The documentation of the Guardian follows semantic versioning as well, but omits
the patch level version number. This means that the Guardian Manual in version
``1.1`` is valid for all components of version ``1.1.x``.

*Version synchronisation* is strict: the Authorization API, the Management API
and the Management UI always share a single version. This is now enforced by the
release mechanism itself. One ``vX.Y.Z`` tag releases all three at the same
version, so they cannot drift apart.

How a release is triggered
==========================

All three app-release components are configured with the shared tag prefix ``v``
(see ``.gitlab-ci/gitlab-ci.yml``). Pushing a single annotated tag of the form
``vX.Y.Z`` (for example ``v3.0.10``) on the release commit on ``main`` starts a
tag pipeline that:

#. builds the container images and pushes them to the public ``nubus`` Harbor
   project, tagged ``X.Y.Z`` (the ``v`` is stripped), as well as to the private
   ``nubus-dev`` project,
#. runs ``create_app_version`` and ``update_appcenter`` for each app, which
   uploads the app at version ``X.Y.Z`` to the **test** App Center. The App
   Center ``ini`` and ``compose`` files are templated (``Version = {{ APP_VERSION }}``),
   so the version is injected automatically and no manual edit is required,
#. waits for the manual ``do_release`` jobs to publish to the **production**
   App Center,
#. creates a GitLab release for the tag and sends the announcement mail and chat
   message automatically.

Pushes to ``main`` without a tag do **not** create a public release. They build
the images and publish them only to the private ``nubus-dev`` project, and they
keep the ``999.0.0-staging`` version in the test App Center up to date. A public
release happens exclusively on a ``vX.Y.Z`` tag.

.. note::
   The tag pipeline only starts if the project's ``workflow:rules`` allow tag
   pipelines (a rule matching ``$CI_COMMIT_TAG``). If pushing a tag does not
   create a pipeline, add such a rule to the ``workflow`` configuration.

Checklist
=========

Copy this into a release issue:

.. code-block:: text

    - [ ] Announce that a release is planned a day prior
    - [ ] Ensure the branch test succeeded for the branch: https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-5/job/guardian-tests-branch/
    - [ ] Ensure a merge stop on the main branch during the release
    - [ ] Decide whether a major, minor or patch level increase is needed
    - [ ] Ensure the version is consistent in all places:
        - [ ] management-api/pyproject.toml
        - [ ] authorization-api/pyproject.toml
        - [ ] the alembic migration folder in management-api/alembic (if a new one was added)
    - [ ] Merge the release commit to main and check that the main pipeline is green
    - [ ] Wait for the Guardian Product Tests to pass (run after merge, takes about one day): https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-5/job/Guardian%20Product%20Tests/
    - [ ] Push the tag vX.Y.Z on the release commit on main
    - [ ] Wait for the tag pipeline to build/push the images and upload all three apps to the test App Center
    - [ ] Smoke test from the test App Center (follow the manual, interact with the management-ui):
        - [ ] Fresh installation of the new version
        - [ ] Upgrade from the last public release to the new version
    - [ ] Trigger the manual do_release jobs for all three apps (authz-do_release, management-do_release, management-ui-do_release)
    - [ ] Confirm the manual check_release jobs once the apps are public
    - [ ] Verify the app files were released (links below)
    - [ ] Verify the release with a test installation/upgrade
    - [ ] Confirm the announcement mail and chat message were sent
    - [ ] Release the Guardian Manual (see below)
    - [ ] Adapt the repo to the next dev version (pyproject.toml, App Center ini) if needed
    - [ ] Create the next release issue

Releasing the apps
==================

#. Ensure a merge stop on ``main`` for the duration of the release.
#. Make sure the branch test succeeded for the branch:
   `guardian-tests-branch <https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-5/job/guardian-tests-branch/>`_.
#. Make sure the version is consistent in all places:

   * the version in ``management-api/pyproject.toml`` and
     ``authorization-api/pyproject.toml``,
   * the alembic migration folder in ``management-api/alembic`` if a new one was
     added.

#. Merge the release commit to ``main`` and wait for the pipeline to pass. The
   dev images are published to the private ``nubus-dev`` project.
#. Wait for the `Guardian Product Tests <https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-5/job/Guardian%20Product%20Tests/>`_
   to pass. They run after the merge and take about one day.
#. Push a single annotated tag on the release commit on ``main``:

   .. code-block:: bash

      git tag -a v3.0.10 -m "Guardian 3.0.10"
      git push origin v3.0.10

#. The tag pipeline builds and publishes the public images and uploads all three
   apps at ``X.Y.Z`` to the test App Center automatically. The relevant jobs are
   ``<prefix>create_app_version`` and ``<prefix>update_appcenter`` with the
   prefixes ``authz-``, ``management-`` and ``management-ui-``.
#. For installation smoke tests, install the latest version from the test App
   Center and follow the installation steps in the manual. Check that you can log
   into the ``management-ui`` with the Administrator (who needs the Guardian
   ``super`` role) and that you can interact with it, for example create a role.
#. For upgrade smoke tests, install the latest publicly released version and
   follow the upgrade steps in the manual. Check that you can log into and
   interact with the ``management-ui`` again.
#. To publish to the production App Center, trigger the manual ``do_release`` job
   of each app in the tag pipeline (``authz-do_release``,
   ``management-do_release`` and ``management-ui-do_release``). These jobs run
   the ``copy_from_appcenter.test.sh`` and ``update_mirror.sh`` steps on
   :guilabel:`omar` for you, no manual SSH is required.
#. Confirm the manual ``check_release`` job of each app when prompted. It verifies
   that the app is reachable in the production App Center.
#. Verify the app files were released `here <https://appcenter.software-univention.de/meta-inf/5.0/guardian-management-api/>`_
   and `there <https://appcenter.software-univention.de/univention-repository/5.0/maintained/component/>`_.
#. The ``create_gitlab_release`` job creates the GitLab release for the tag, and
   the ``send_mail`` and ``send_chat_message`` jobs announce the release
   automatically (see `Release Announcement`_ for the message content).

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
#. To add the new version to the doc search as well, please create and merge a MR to add the new version,
   like here `Docsearch <https://git.knut.univention.de/univention/documentation/docsearch/-/merge_requests/7>`_

Release Announcement
====================

The announcement mail (to ``app-announcement@univention.de``) and the chat
message (to the ``#ucsschool`` channel) are sent automatically by the tag
pipeline's ``send_mail`` and ``send_chat_message`` jobs. The template below
documents the content. You can also use it when announcing a release manually,
for example in the Rocket.Chat channel ``Guardian``:

.. code-block:: text

   Hello,

   the following App update has been published:

   Guardian Management API $VERSION

   Most important changes:

      * CHANGE1
      * CHANGE2

   The changelog can be read here:

   https://docs.software-univention.de/guardian-manual/latest/changelogs.html

   Greetings,

   $NAME
