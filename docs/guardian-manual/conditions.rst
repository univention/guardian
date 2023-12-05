.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conditions:

********************
Conditions Reference
********************

This chapter documents the :term:`conditions<condition>` that the Guardian provides for configuring
:term:`capabilities<capability>` on :term:`roles<role>`. This is of interest for both
:term:`app developers<app developer>` and :term:`guardian admins<guardian admin>`, that
want to configure roles properly.

All conditions listed here are created in the ``guardian`` app's ``builtin`` :term:`namespace`. Therefore the identifier of
any condition is ``guardian:builtin:condition_name``, where ``condition_name`` is the name of the specific condition.

.. note::

   Requests to the :term:`Authorization API` supply both an ``old_target``,
   the state of the :term:`target` before a change,
   and a ``new_target``,
   the state of the target after the change.

   In this document, conditions on the target apply only to the ``old_target``.

.. envvar:: actor_does_not_have_role

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - role
     - ROLE (string)

This condition applies if the :term:`actor` does not have the :term:`role` specified in the ``role`` parameter.

.. envvar:: no_targets

This condition applies if the authorization request does not contain a specific :term:`target`.

.. envvar:: only_if_param_result_true

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - result
     - BOOLEAN

This condition is included for testing and debugging purposes only and should not be used.

.. envvar:: target_does_not_have_role

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - role
     - ROLE (string)

This condition applies if the :term:`target` does not have the :term:`role` specified in the ``role`` parameter.

.. envvar:: target_does_not_have_role_in_same_context

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - role
     - ROLE (string)

This condition applies if the :term:`target` does not have the :term:`role` specified in the ``role`` parameter with the
same :term:`context` as the :term:`actor's<actor>` role currently being evaluated. For example, if the actor's role is
``company:default:admin`` in the context ``DEPARTMENT1`` and the ``role`` parameter is ``company:default:user``,
this condition would apply as long as the target does not have the role ``company:default:user``
with the context ``DEPARTMENT1``.

.. envvar:: target_field_equals_actor_field

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - target_field
     - STRING
   * - actor_field
     - STRING

This condition applies if the specified field of the :term:`actor` and the specified field of the :term:`target` have the same value.

.. envvar:: target_field_equals_value

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - field
     - STRING
   * - value
     - ANY

This condition applies if the specified ``field`` of the :term:`target` has the same value as specified in the ``value`` parameter.

.. envvar:: target_field_not_equals_value

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - field
     - STRING
   * - value
     - ANY

This condition applies if the specified ``field`` of the :term:`target` does not have the same value as specified in the
``value`` parameter.

.. envvar:: target_has_role

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - role
     - ROLE (string)

This condition applies if the :term:`target` has the :term:`role` specified in the ``role`` parameter.

.. envvar:: target_has_role_in_same_context

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - role
     - ROLE (string)

This condition applies if the :term:`target` has the :term:`role` specified in the ``role`` parameter with the
same :term:`context` as the :term:`actor's<actor>` role currently being evaluated. If for example the actor's role is
``company:default:admin`` in the context ``DEPARTMENT1`` and the ``role`` parameter is ``company:default:user``,
this condition would apply as long as the target has the role ``company:default:user``
with the context ``DEPARTMENT1``.

.. envvar:: target_has_same_context

This condition applies if any of the :term:`target's<target>` :term:`roles<role>` have the same :term:`context` as any of the
:term:`actor's<actor>` :term:`roles<role>`.

.. envvar:: target_is_self

.. list-table::
   :header-rows: 1
   :align: left
   :width: 50%

   * - Parameter name
     - Value type
   * - field
     - STRING

This condition applies if the :term:`actor` and the :term:`target` are the same. Per default this is decided by comparing their ``id``
attribute. If the ``field`` value is specified this field is used for identification instead.
