.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _guardian-assigning-roles-to-users:

###################################
Assigning roles to users or objects
###################################

The Guardian itself does not assign roles to users or objects.
Instead, an :term:`app infrastructure maintainer` is responsible for assigning role strings
with UDM, or an :term:`app developer` must assign roles to objects in their own internal database.

.. versionadded:: 3.0.0

   The Guardian supports the attributes ``guardianRoles`` and ``guardianInheritedRoles`` to identify the roles of a user or object.
   The old attribute ``guardianRole`` is no longer used.

In the default configuration the Guardian gets the role information from :external+uv-ucs-manual:ref:`UDM <central-udm>`.
You have two options for adding roles to users or other objects:

#. Append the role string, for example ``cake-express:cakes:cake-orderer``, to the attribute ``guardianRoles`` of the user or object
#. Add the user to a group and append the role string to the group attribute ``guardianMemberRoles``.
   All members of that group will receive that role in the calculated ``guardianInheritedRoles`` attribute.

Suppose you have a user with ``uid=m.mustermann``, who is in group ``testgroup``:

.. code-block:: bash
   :caption: Preparing the user and group.

   GROUP_POSITION="cn=groups,$(ucr get ldap/base)"
   GROUP_NAME="testgroup"
   USER_POSITION="cn=users,$(ucr get ldap/base)"
   USER_NAME="m.mustermann"

   udm groups/group create --position "cn=groups,$(ucr get ldap/base)" --set name="$GROUP_NAME"
   GROUP_DN="cn=$GROUP_NAME,$GROUP_POSITION"

   udm users/user create --position "cn=users,$(ucr get ldap/base)" --set username="$USER_NAME" --set lastname="mustermann" --set password="univention" --append groups=$GROUP_DN
   USER_DN="uid=$USER_NAME,$USER_POSITION"

You can now add roles via the attribute ``guardianMemberRoles`` and ``guardianRoles``:

.. code-block:: bash
   :caption: Adding the roles.

   udm groups/group modify --dn $GROUP_DN --append guardianMemberRoles="app1:namespace1:role1"
   udm users/user modify --dn $USER_DN --append guardianRoles="app2:namespace2:role2"

When you inspect the user, you will see both roles:

.. code-block:: bash
   :caption: Inspecting the roles.

   udm users/user list --filter username=$USER_NAME --properties guardianRoles --properties guardianInheritedRoles

   # Output:
   # DN: uid=m.mustermann,cn=users,dc=testschool,dc=intranet
   #   guardianInheritedRoles: app1:namespace1:role1
   #   guardianRoles: app2:namespace2:role2

.. important::

   You must specify the ``--properties guardianInheritedRoles`` explicitly, otherwise this attribute will neither be calculated
   or shown.

.. note::

   The Guardian will combine both attributes with a union operation. Hence, the origin of the role
   does not matter and receiving the same role more than once also has no effect. Similarly, being a member
   of more than one groups which have an equal ``guardianMemberRoles`` does not have an effect.

