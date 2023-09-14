import pytest
from guardian_management_api.models.routers.base import RawCodeObjectMixin
from pydantic import ValidationError


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
