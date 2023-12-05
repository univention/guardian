.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _limitations:

***********
Limitations
***********

The Guardian software stack is a new product that is developed iteratively. This chapter documents
the known limitations of each component.

.. _guardian-management-api-limitations:

Guardian Management API
=======================

.. _app-center-database-limitations:

App Center database limitations
-------------------------------

Due to limitations in the Univention App Center, the Guardian Management API should only be deployed once in any UCS domain.
This is due to the fact that each instance of the app gets its own database for the persistent data. This would mean
that every instance has its own set of :term:`apps<app>`, :term:`conditions<condition>`, :term:`roles<role>`, etc. The App Center does not
prevent anyone from deploying as many instances of the Guardian Management API as desired, so this limitation has to be
kept in mind.

.. _no-object-deletion-limitation:

No object deletion
------------------

The Management API does not allow for the deletion of objects at the moment, with the exception of :term:`capabilities<capability>`.
This is due to the relation of the different object types with each other and the complex consistency checks this operation would entail.

.. _policy-endpoint-is-public-limitation:

Policy endpoint is public
-------------------------

The endpoint in the Management API where the Authorization API can download the policy data for decision making can be
accessed without any authentication. Therefore all data that is contained in the Management API has to be considered
public information.

.. _guardian-authorization-api-limitations:

Guardian Authorization API
==========================

.. _limitation-for-with-lookup-endpoints:

Limitation for ``with-lookup`` endpoints
----------------------------------------

The Guardian generally allows each client :term:`application<app>` to use its own structure for data that is used
for authorization. As long as the capabilities and conditions are created in a fashion that handles data correctly,
there are no restrictions what the data must look like.

However, the ``with-lookup`` endpoints, which allow the Authorization API to fetch data from UDM on behalf of the :term:`app`,
are limited to the structure of :term:`actors<actor>` and :term:`targets<target>` returned by the UDM REST API.

.. _guardian-management-ui-limitations:

Guardian Management UI
======================

.. _frontend-only-pagination-limitation:

Frontend-only pagination
------------------------

The Management UI in its current state always fetches all objects in their respective list views.
This might reduce performance in the UI if working with very big datasets.

.. _no-typing-for-condition-parameters-limitation:

No typing for condition parameters
----------------------------------

When managing the :term:`capabilities<capability>` of a :term:`role` in the UI and editing the :term:`conditions<condition>`, the parameters of those conditions
are currently not typed. Therefore it is important to take special care when entering the values for condition
parameters.

If there are any problems with users not having the correct permissions as configured, it should be one of the first
places to check. Make sure that there are no errors due to wrongly typed parameter values.

.. _ucs-portal-integration-limitation:

UCS Portal integration
----------------------

The Management UI can be accessed from the UCS Portal, but is opened in a new tab. Currently the integration directly into
the Portal tab does not work.
