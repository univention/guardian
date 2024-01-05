.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _management-ui:

*************
Management UI
*************

This section addresses :term:`Guardian administrators <guardian administrator>`
who want to manage :term:`roles <role>` and related objects
which can grant :term:`permissions <permission>` to users.

The Guardian :term:`Management UI` app provides a web interface
to manage some of the features of the REST API of the Guardian :term:`Management API` app.
The following sections describe which functions you can perform with the web interface.

You can access the *Management UI* at
:samp:`https://{domainname}/univention/guardian/management-ui`.
For the :samp:`{domainname}` use the UCS system's hostname where you installed the *Management UI*.
The installation of the *Management UI* creates a portal entry
in the *Administration* category of the default
domain portal, :samp:`cn=domain,cn=portal,cn=portals,cn=univention,$ldap_base`.
With the default configuration, a user who wants to use the *Management UI* as a :term:`guardian administrator`
needs the role ``guardian:builtin:super-admin``.

For a detailed explanation of the terms :term:`roles <role>`, :term:`capabilities<capability>`, :term:`namespaces<namespace>`,
and :term:`contexts<context>`, refer to :ref:`guardian-terminology`.

After you entered the *Management UI*,
you see a navigation menu with the entries
:guilabel:`ROLES`, :guilabel:`NAMESPACES` and :guilabel:`CONTEXTS`,
and a search bar with filters and a table as shown in :numref:`management-ui-front-page-fig`.

.. _management-ui-front-page-fig:

.. figure:: /images/management-ui/front_page.png
   :width: 100%
   :align: center

   The front page of the :program:`Guardian Management UI`.

You can view and manage the object types :term:`role`,
:term:`namespace`, and :term:`context`
by navigating between them using the navigation menu,
as described in the following sections.
You manage :term:`capabilities <capability>` while editing a role.

.. tip::

   You can only manage the :term:`apps <app>` in the *App* drop-down
   through the REST API provided by the :term:`Management API`.
   If you want to integrate your app with the Guardian,
   refer to :ref:`developer-quick-start`.


In the search view for any of the object types,
you can filter by app and namespace, except for namespaces themselves,
which can only be filtered by an app.

.. admonition:: Limitation for search criteria

   Including properties of an object,
   such as its *Display Name*,
   in the search criteria
   isn't supported.

.. _management-ui-roles:

Roles
=====

You can use the *Management UI* to manage :term:`roles <role>`.
A role contains capabilities.
An app and a namespace define roles.
The Guardian derives permissions from the role and its capabilities.
For more information about the fundamental concepts,
refer to :ref:`terminology-guardian-role` in :ref:`guardian-terminology`.

.. _create-a-new-role:

Create a role
-------------

This section describes how to create a role in the *Management UI*.

#. To create a role, first open the *Management UI*
   and click :guilabel:`ROLES` in the navigation menu.

   .. figure:: /images/management-ui/click_on_roles_button.png
      :width: 100%
      :align: center

      Link to the roles page.

#. To open the page to create a role, click the :guilabel:`+ ADD` button.

   .. figure:: /images/management-ui/click_on_add_roles_button.png
      :width: 100%
      :align: center

      Click :guilabel:`+ ADD` to create a role.

   The page to create a role looks like :numref:`create-role-page-fig`.

   .. _create-role-page-fig:

   .. figure:: /images/management-ui/create_role_page.png
      :width: 100%
      :align: center

      Page to create a role.

#. Fill out all the necessary fields.
   To create the role, click the :guilabel:`CREATE ROLE` button.
   A dialog confirms the creation and shows the role name.

.. hint::

   The selectable options for the *Namespace* box depend on the selected app in the *App* box.
   You have to select an app first before you can select a namespace.
   If you selected an app and still don't see any selectable namespaces
   that means that there are no namespaces for that app.
   Refer to :ref:`create-a-new-namespace`.

.. hint::

   You can only manage capabilities on existing roles.

   If you create a role and want to manage its capabilities,
   first create the role with the :guilabel:`CREATE ROLE` button
   and then manage capabilities as described in :ref:`capabilities-of-a-role`.

.. _listing-roles:

Listing and searching roles
---------------------------

This section describes how to list and search roles in the *Management UI*.

#. To list existing roles, open the *Management UI*.
   Click :guilabel:`ROLES` in the navigation menu.

   .. figure:: /images/management-ui/click_on_role.png
      :width: 100%
      :align: center

      Link to the "Roles" page.

#. To search for existing roles, click the :guilabel:`SEARCH` button.
   The results show up below the button.
   To narrow the search results, select the specific app in the *App* drop-down
   and the namespace of the selected app in the *Namespace* drop-down.

   .. figure:: /images/management-ui/search_and_list_roles.png
      :width: 100%
      :align: center

      Form elements for the search of roles.

.. seealso::

   For information about how to manage the namespace for the *Namespace*
   drop-down, refer to :ref:`namespaces`.


.. _editing-existing-roles:

Editing existing roles
----------------------

This section describes how to edit existing roles in the *Management UI*.

To edit a role,
follow the steps in :ref:`listing-roles` to list them
and then click the name of the role that you want to edit.

.. figure:: /images/management-ui/click_on_role.png
   :width: 100%
   :align: center

   Edit button for listed roles.

The role editing window has two pages.

:numref:`editing-existing-roles-first-page-fig`
shows the first page
where you edit the direct properties of the role.
It shows up first when you open a role.
To open the page from a different location,
click :guilabel:`ROLE` in the navigation menu.
Edit the fields you want to change.
To save the changes, click :guilabel:`SAVE`.

.. _editing-existing-roles-first-page-fig:

.. figure:: /images/management-ui/click_on_save_role.png
   :width: 100%
   :align: center

   View and edit page of an existing role.

:numref:`editing-existing-roles-second-page-fig`
shows the second page
where you manage the capabilities of the current role.
To open the page from a different location,
click :guilabel:`CAPABILITES` in the navigation menu.

The page list all capabilities of the role.
You can edit and manage them here.
You can also create capabilities for that role or delete existing ones.
For more details on capabilities,
see :ref:`capabilities-of-a-role`.

.. _editing-existing-roles-second-page-fig:

.. figure:: /images/management-ui/list_capabilities.png
   :width: 100%
   :align: center

   Link to the "Capabilities" page of an existing role.

.. _deleting-roles:

Deleting roles
--------------

Deleting roles isn't supported. Neither through the web-interface nor the REST API.

.. _capabilities-of-a-role:

Capabilities of a role
======================

:term:`Capabilities <capability>` serve as the means
to manage the :term:`permissions <permission>`
that the :term:`role` grants to the user it's attached to.

Each capability object can define one ore more permissions.
You can only select permissions for a specific app and namespace.
If you want to grant permissions for different apps or namespaces
you have to create multiple capability objects.

Inside a capability object
you can also add :term:`conditions <condition>`
that influence whether the permissions are actually granted.

The capabilities work on an allow list principle and don't collide.

.. hint::

   You can only manage capabilities on existing roles.

   If you create a role and want to manage its capabilities,
   first create the role and then edit the role to manage its capabilities.

.. _create-new-capabilities-for-a-role:

Create a capability for a role
------------------------------

This section describes how to create a capability for a role in the *Management UI*.

#. To add a capability for a role,
   click :guilabel:`CAPABILITES` in the navigation menu
   while you edit a role.
   For details on editing a role,
   refer to :ref:`editing-existing-roles`.

#. To open the page to create a capability,
   click the :guilabel:`+ ADD` button .

   .. figure:: /images/management-ui/click_on_add_capabilities_button.png
      :width: 100%
      :align: center

      Click :guilabel:`+ ADD` to create a capability.

   The page to create a capability looks like :numref:`create-new-capabilities-for-a-role-fig`.

   .. _create-new-capabilities-for-a-role-fig:

   .. figure:: /images/management-ui/create_new_capability.png
      :width: 100%
      :align: center

      Page to create a new capability.

#. To create the capability
   fill out all the necessary fields
   and click the :guilabel:`CREATE CAPABILITY` button.
   A dialog confirms the creation by showing the capability name.

The following noteworthy fields are the list of *Permissions*,
the list of *Conditions*
and the *Relation*.

Permissions
   In the *Permissions* list you can edit all permissions
   that the capability grants
   if the conditions in the *Conditions* list are true.
   The available permissions base on
   the selected app in the *App* drop-down
   and namespace in the *Namespace* drop-down.
   You can't select any permissions before filling out both of these fields.

   .. hint::

      If you filled out both the *App* drop-down and *Namespace* drop-down,
      and you still can't select permissions,
      this means that no permissions exist for that app and namespace.

Conditions
   In the *Conditions* list you can edit all the conditions
   that the Guardian validates
   before it grants the permissions in the *Permissions* list.
   Some conditions require additional parameters.
   After you select a condition,
   additional fields show up underneath the condition.

   .. figure:: /images/management-ui/conditions_list.png
      :width: 100%
      :align: center

      Condition with extra parameters.

   .. seealso::

      For more information about conditions,
      refer to :ref:`conditions`.

Relation
   The value of the *Relation* drop-down
   describes how the *Authorization API* evaluates conditions during authorization.
   **AND** means all conditions must evaluate to true
   and **OR** means only one condition must evaluate to true.

.. _listing-capabilities-of-a-role:

Listing and searching capabilities of a role
--------------------------------------------

This section describes how to list and search capabilities of a role in the *Management UI*.

To list capabilities of a role,
click :guilabel:`CAPABILITES` in the navigation menu while editing a role.
For more details on editing a role, refer to :ref:`editing-existing-roles`.

On this page, to search for capabilities of the role you are editing,
click the :guilabel:`SEARCH` button.
The results shown up below the button.
To narrow the search results,
select a specific app in the *App* drop-down,
and a namespace of the selected app in the *Namespace* drop-down.

.. figure:: /images/management-ui/listing_and_searching_capabilities.png
   :width: 100%
   :align: center

   Form elements for the search of capabilities.

.. seealso::

   To manage the namespaces in the *Namespace* drop-down,
   refer to :ref:`namespaces`.


.. _editing-a-capability-of-a-role:

Edit a capability of a role
---------------------------

This section describes how to edit a capability of a role in the *Management UI*.

To edit a capability of a role,
you must first list it.
To list a capability, follow the steps in :ref:`listing-capabilities-of-a-role`.
To edit a capability,
click the name of the capability you want to edit
in the search results list.

.. figure:: /images/management-ui/click_on_capability.png
   :width: 100%
   :align: center

   Edit button for listed capabilities.

The page to edit a capability looks like :numref:`editing-a-capability-of-a-role-fig`.

.. _editing-a-capability-of-a-role-fig:

.. figure:: /images/management-ui/capability_edit_page.png
   :width: 100%
   :align: center

   View and edit page of an existing capability.

The following noteworthy fields are the list of *Conditions*,
the *Relation*
and the list of *Permissions*.

Permissions
   In the *Permissions* list you can edit all permissions
   that the capability grants
   if the conditions in the *Conditions* list are true.

Conditions
   In the *Conditions* list you can edit all the conditions
   that the Guardian validates
   before it grants the permissions in the *Permissions* list.
   Some conditions require additional parameters.
   After you select a condition,
   additional fields show up underneath the condition.

   .. figure:: /images/management-ui/conditions_list.png
      :width: 100%
      :align: center

      Condition with extra parameters.

   .. seealso::

      For more information about conditions,
      refer to :ref:`conditions`.

Relation
   The value of the *Relation* drop-down describes
   how the *Authorization API* evaluates the selected
   conditions of the *Conditions*.
   **AND** means that all conditions must be true.
   **OR** means that only one condition must be true.

.. _deleting-capabilities-of-a-role:

Delete capabilities of a role
-----------------------------

This section describes how to delete a capability of a role in the *Management UI*.

To delete capabilities,
you must first click :guilabel:`CAPABILITES` in the navigation menu while editing a role.
For more details on editing a role, refer to :ref:`editing-existing-roles`.

Search and select all the capabilities you want to delete,
then click the :guilabel:`DELETE` button.

.. figure:: /images/management-ui/delete_capabilities.png
   :width: 100%
   :align: center

   Deletion of capabilities.


.. _namespaces:

Namespaces
==========

A namespace is a means to categorize roles and permissions.
You can create, view, edit, and search namespaces with the *Management UI*.
For more information about namespaces,
refer to :ref:`terminology-guardian-namespace` in :ref:`guardian-terminology`.

.. _create-a-new-namespace:

Create a new namespace
----------------------

This section describes how to create a namespace in the *Management UI*.

#. To create a namespace,
   first open the *Management UI*
   and click :guilabel:`NAMESPACES` in the navigation menu.

   .. figure:: /images/management-ui/click_on_namespace_button.png
      :width: 100%
      :align: center

      Link to the "Namespaces" page.

#. To open the page to create a namespace, click the :guilabel:`+ ADD` button.

   .. figure:: /images/management-ui/click_on_add_namespace_button.png
      :width: 100%
      :align: center

      Click :guilabel:`+ ADD` to create a namespace.

   The page to create a namespace looks like :numref:`create-a-new-namespace-fig`.

   .. _create-a-new-namespace-fig:

   .. figure:: /images/management-ui/create_namespace_page.png
      :width: 100%
      :align: center

      Page to create a namespace.

#. Fill out all the necessary fields.
   To create the namespace, click the :guilabel:`CREATE NAMESPACE` button.
   A dialog confirms the creation by showing the namespace name.

.. _listing-namespaces:

Listing and searching namespaces
--------------------------------

This section describes how to list and search namespaces in the *Management UI*.

To list existing namespaces
open the *Management UI*
and click :guilabel:`NAMESPACES` in the navigation menu.

.. figure:: /images/management-ui/click_on_namespace_button.png
   :width: 100%
   :align: center

   Link to the "Namespaces" page.

On this page, to search for namespaces,
click the :guilabel:`SEARCH` button.
The results show up below the button.
To narrow the search results,
select a specific app in the *App* drop-down.

.. figure:: /images/management-ui/namespace_app_box.png
   :width: 100%
   :align: center

   Form elements for the search of namespaces.

.. _editing-existing-namespaces:

Editing existing namespaces
---------------------------

This section describes how to edit existing namespaces in the *Management UI*.

To edit a namespaces,
you must first list it.
To list a namespace, follow the steps in :ref:`listing-namespaces`.
To edit a namespace,
click the name of the namespace you want to edit
in the search results list.

.. figure:: /images/management-ui/click_on_namespace.png
   :width: 100%
   :align: center

   Edit button for listed namespaces.

The page to edit the namespace you clicked looks like :numref:`editing-existing-namespaces-fig`.

.. _editing-existing-namespaces-fig:

.. figure:: /images/management-ui/namespace_edit_page.png
   :width: 100%
   :align: center

   View and edit page of an existing namespace.

.. _deleting-namespaces:

Deleting namespaces
-------------------

Deleting namespaces isn't supported.
Neither through the web-interface nor the REST API.

.. _management-ui-contexts:

Contexts
========

A context is an additional tag that you can apply to a :term:`role`,
to make it only apply in certain circumstances.
With the *Management UI* you can create, view, edit, and search a context.
For more information about contexts, refer to
:ref:`terminology-guardian-context` in the :ref:`guardian-terminology` section.

.. _create-a-new-context:

Create a context
----------------

This section describes how to create a context in the *Management UI*.

#. To create a context
   first open the *Management UI*
   and click :guilabel:`CONTEXTS` in the navigation menu.

   .. figure:: /images/management-ui/click_on_context_button.png
      :width: 100%
      :align: center

      Link to the "Contexts" page.

#. To open the page to create a context,
   click the :guilabel:`ADD` button.

   .. figure:: /images/management-ui/click_on_add_context_button.png
      :width: 100%
      :align: center

      Click :guilabel:`+ ADD` to create a context.

#. The page to create a context looks like :numref:`create-a-new-context-fig`.

   .. _create-a-new-context-fig:

   .. figure:: /images/management-ui/create_context_page.png
      :width: 100%
      :align: center

      Page to create a context.

#. Fill out all the necessary fields.
   To create the context, click the :guilabel:`CREATE CONTEXT` button.
   A dialog confirms the creation by showing the context name.

.. _listing-contexts:

Listing and searching contexts
------------------------------

This section describes how to list and search a context in the *Management UI*.

To list existing contexts
open the *Management UI*
and click :guilabel:`CONTEXTS` in the navigation menu.

.. figure:: /images/management-ui/click_on_context_button.png
   :width: 100%
   :align: center

   Link to the "Contexts" page.

On this page,
to search for contexts,
click the :guilabel:`SEARCH` button.
The results show up below the button.
To narrow the search results,
select a specific in the *App* drop-down,
and a namespace of the selected app in the *Namespace* drop-down.

.. figure:: /images/management-ui/search_filter_context.png
   :width: 100%
   :align: center

   Form elements for the search of contexts.

.. seealso::

   To manage the namespaces in the *Namespace* drop-down,
   refer to :ref:`namespaces`.

.. _editing-existing-contexts:

Editing existing contexts
-------------------------

This section describes how to edit a context in the *Management UI*.

To edit a context,
you must first list it.
To list a context, follow the steps in :ref:`listing-contexts`.
To edit a context,
click the name of the context you want to edit
in the search results list.

.. figure:: /images/management-ui/click_on_context.png
   :width: 100%
   :align: center

   Edit button for listed contexts.

The page to edit the context you clicked,
looks like :numref:`editing-existing-contexts-fig`.

.. _editing-existing-contexts-fig:

.. figure:: /images/management-ui/context_edit_page.png
   :width: 100%
   :align: center

   View and edit page of an existing context.

.. _deleting-contexts:

Deleting contexts
-----------------

Deleting contexts isn't supported.
Neither through the web-interface nor the REST API.
