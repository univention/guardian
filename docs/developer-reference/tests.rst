.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

*****
Tests
*****

Guardian has extensive testing in place to ensure the quality and reliability of its components. There are two main types of tests: unit tests that check individual functions, classes, or modules, and integration tests that verify how different parts of the system work together. Both unit and integration tests are written using Python's ``pytest`` framework.

The tests were designed with the goal of having 100% unit tests coverage.

Running Tests Locally
=====================

If you have an instance of UDM and Keycloak running, you can run the integration tests as well. Those tests
additionally need the UDM user ``guardian`` to exist with the right role. It can be created with the following command on your
:guilabel:`UCS server`:

.. code-block:: bash

    udm users/user create \
      --set username=guardian \
      --set lastname=app-admin \
      --set password=univention \
      --set guardianRoles=guardian:builtin:app-admin \
      --position cn=users,$(ucr get ldap/base)

Finally, run the tests for the desired component in your environment:

.. code-block:: bash

    # Activate your preferred python env, e.g.
    # . ~/venvs/management-api/bin/activate
    pytest -lv management-api/; deactivate
    # . ~/venvs/authorization-api/bin/activate
    pytest -lv authorization-api/; deactivate
    #. ~/venvs/guardian-lib/bin/activate
    pytest -lv guardian-lib/; deactivate

If you don't want to test the integration with UDM and Keycloak, you can exclude the ``e2e_udm`` test in the management-api component:

.. code-block:: bash

    # . ~/venvs/management-api/bin/activate
    pytest -lv -k "not e2e_udm" management-api/; deactivate

For the Authorization API component, the UDM integration tests are automatically skipped if ``UDM_DATA_ADAPTER__URL`` is not set.

GitLab Testing Pipeline
=========================

Guardian uses GitLab CI/CD for its testing pipeline. The tests are automatically run whenever a change is pushed to the repository or a new merge request is created.

The pipeline consists of several stages:

1. **build**: This stage builds the Docker image that will be used for testing.
2. **test**: This stage runs the unit tests for each component using pytest. The `GUARDIAN_COMPONENT` variable determines which component is being tested, and the `GUARDIAN_TEST_ARGS` variable can be used to pass additional arguments to pytest.
3. **coverage**: This stage generates a coverage report that shows what percentage of each component's code is covered by the unit tests. The `GUARDIAN_COMPONENT` and `GUARDIAN_TEST_ARGS` variables are used in the same way as in the test stage.

Jenkins Testing Pipeline
=========================

Guardian also uses Jenkins for its testing pipeline, which provides a more complex but realistic setup that ensures integration with external systems via ``pytest`` integration and E2E tests. The Jenkins pipeline is similar to the GitLab pipelinewith the addition of seting up Keycloak, UDM, and a test user for the aforementioned integration tests.

There are two jobs, one for automatically run daily tests with the latest published version of Guardian, and another for manually triggered tests with custom docker images generated from branches.
