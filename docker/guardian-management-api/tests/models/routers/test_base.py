import re

import pytest
from guardian_management_api.models.routers.app import AppCreateRequest
from guardian_management_api.models.routers.base import (
    AppNamePathMixin,
    ManagementObjectName,
    NamePathMixin,
    NamespacePathMixin,
    RawCodeObjectMixin,
)
from guardian_management_api.models.routers.capability import (
    CapabilityCreateData,
    CapabilityCreateRequest,
    CapabilityRole,
    RelationChoices,
)
from guardian_management_api.models.routers.condition import (
    ConditionCreateData,
    ConditionCreateRequest,
)
from guardian_management_api.models.routers.context import (
    ContextCreateData,
    ContextCreateRequest,
)
from guardian_management_api.models.routers.custom_endpoint import (
    CustomEndpointCreateData,
    CustomEndpointCreateRequest,
)
from guardian_management_api.models.routers.namespace import (
    NamespaceCreateData,
    NamespaceCreateRequest,
)
from guardian_management_api.models.routers.permission import (
    PermissionCreateData,
    PermissionCreateRequest,
)
from guardian_management_api.models.routers.role import (
    RoleCreateData,
    RoleCreateRequest,
)
from pydantic import ValidationError, parse_obj_as


class TestNameRegex:
    invalid_values = [
        "$_invalid_char_at_beginning",
        "invalid_char_$_in_middle",
        "CAPITAL",
        "xCAPITAL",
        "999",
    ]
    validation_error_match = re.escape(
        r'string does not match regex "^[a-z][a-z0-9\-_]*$"'
    )

    @pytest.mark.parametrize("value", ["valid", "valid_1-test", "also-valid_name123"])
    def test_management_object_happy_path(self, value):
        parse_obj_as(ManagementObjectName, value)

    @pytest.mark.parametrize("value", invalid_values)
    def test_management_object_name_validation(self, value):
        with pytest.raises(ValidationError, match=TestNameRegex.validation_error_match):
            parse_obj_as(ManagementObjectName, value)

    @pytest.mark.parametrize("value", invalid_values)
    def test_app_name_path_mixin_validation(self, value):
        with pytest.raises(ValidationError, match=TestNameRegex.validation_error_match):
            AppNamePathMixin(app_name=value)

    @pytest.mark.parametrize("value", invalid_values)
    def test_namespace_path_mixin_validation(self, value):
        with pytest.raises(ValidationError, match=TestNameRegex.validation_error_match):
            NamespacePathMixin(namespace_name=value)

    @pytest.mark.parametrize("value", invalid_values)
    def test_name_path_mixin_validation(self, value):
        with pytest.raises(ValidationError, match=TestNameRegex.validation_error_match):
            NamePathMixin(name=value)

    @pytest.mark.parametrize("value", invalid_values)
    def test_app_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for AppCreateRequest\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            AppCreateRequest(name=value)

    @pytest.mark.parametrize("value", invalid_values)
    def test_role_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for RoleCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            RoleCreateRequest(
                app_name="app",
                namespace_name="namespace",
                data=RoleCreateData(name=value),
            )

    @pytest.mark.parametrize("value", invalid_values)
    def test_permission_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for PermissionCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            PermissionCreateRequest(
                app_name="app",
                namespace_name="namespace",
                data=PermissionCreateData(name=value),
            )

    @pytest.mark.parametrize("value", invalid_values)
    def test_namespace_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for NamespaceCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            NamespaceCreateRequest(app_name="app", data=NamespaceCreateData(name=value))

    @pytest.mark.parametrize("value", invalid_values)
    def test_custom_endpoint_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for CustomEndpointCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            CustomEndpointCreateRequest(
                app_name="app",
                namespace_name="asd",
                data=CustomEndpointCreateData(name=value),
            )

    @pytest.mark.parametrize("value", invalid_values)
    def test_context_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for ContextCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            ContextCreateRequest(
                app_name="app", namespace_name="asd", data=ContextCreateData(name=value)
            )

    @pytest.mark.parametrize("value", invalid_values)
    def test_condition_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for ConditionCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            ConditionCreateRequest(
                app_name="app",
                namespace_name="asd",
                data=ConditionCreateData(name=value),
            )

    @pytest.mark.parametrize("value", invalid_values)
    def test_capability_create_request_validation(self, value):
        with pytest.raises(
            ValidationError,
            match=f"1 validation error for CapabilityCreateData\nname\n"
            f"  {TestNameRegex.validation_error_match}",
        ):
            CapabilityCreateRequest(
                app_name="app",
                namespace_name="namespace",
                data=CapabilityCreateData(
                    name=value,
                    role=CapabilityRole(
                        app_name="app",
                        namespace_name="namespace",
                        name="role",
                    ),
                    relation=RelationChoices.AND,
                    conditions=[],
                    permissions=[],
                ),
            )


class TestRawCodeObjectMixin:
    @pytest.mark.parametrize("value", [None, b"Q09ERQ==", "Q09ERQ=="])
    def test_ensure_code_base64(self, value):
        RawCodeObjectMixin(code=value)

    @pytest.mark.parametrize(
        "value",
        ["SOME_STRING", "sdgsghsdg", b"SOME_STRING", b"sdgsghsdg", 5, b"hfjo=="],
    )
    def test_ensure_code_base64_validation_error(self, value):
        with pytest.raises(ValidationError):
            RawCodeObjectMixin(code=value)
