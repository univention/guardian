.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _limitations:

***********
Limitations
***********

The Guardian software stack is a product
that the Univention software engineering team develops iteratively.
This section describes the known limitations of each component.

.. _limits-management-api:

Management API
==============

.. _limits-app-center-database:

App Center database limitations
-------------------------------

Due to the limitations of the Univention App Center,
only deploy the *Management API* once in each UCS domain.
This is because each instance of the app gets its own database for the persistent data.
Multiple instances of the app would mean
that each instance would have its own set of :term:`apps <app>`,
:term:`conditions <condition>`, and :term:`roles <role>`.
The App Center doesn't prevent administrators
from deploying as many instances of the Guardian Management API as they want.
Keep this limitation in mind.

.. _limits-no-object-deletion-limitation:

No object deletion
------------------

The *Management API* doesn't allow to delete objects,
with the exception of :term:`capabilities <capability>`.
This is due to the close relationship between the different object types
and the complex consistency checks involved in a delete operation.

.. _limits-policy-endpoint-is-public-limitation:

Policy endpoint is public
-------------------------

The endpoint in the *Management API* for downloading the policy data for
decision making doesn't require any authentication.
The *Authorization API* uses this endpoint.
Therefore, you must consider all data contained in the *Management API* as **public information**.

.. _limits-authorization-api:

Authorization API
=================

.. _limitation-for-with-lookup-endpoints:

Limitation for ``with-lookup`` endpoints
----------------------------------------

The Guardian generally allows each client :term:`application <app>`
to use its own structure for data
that's used for authorization.
As long as the capabilities and conditions are created in a fashion
that handles data correctly,
there are no restrictions what the data must look like.

However, the ``with-lookup`` endpoints,
which allow the *Authorization API* to fetch data from UDM on behalf of the :term:`app`,
are limited to the structure of :term:`actors <actor>` and :term:`targets <target>` returned by the UDM REST API.

.. _limits-management-ui:

Management UI
=============

.. _limits-frontend-only-pagination-limitation:

Frontend-only pagination
------------------------

The *Management UI* always fetches all objects in their respective list views.
This might reduce performance in the *Management UI* if working with big datasets.

.. _limits-no-typing-for-condition-parameters-limitation:

No typing for condition parameters
----------------------------------

When you manage the :term:`capabilities <capability>` of a :term:`role` in the *Management UI*
and edit the :term:`conditions <condition>`,
the parameters of those conditions aren't typed.
Therefore, it's important to take extra care when entering the values for condition parameters.

If there are any problems with users not having the correct permissions as configured,
this should be one of the first places to look.
Make sure that there are no errors due to mistyped parameter values.

.. _limits-ucs-portal-integration-limitation:

UCS Portal integration
----------------------

Users can access the *Management UI* from the UCS Portal.
It opens in a new tab in the web browser.
Integration directly in the UCS Portal tab doesn't work.
