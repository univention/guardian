from fastapi import Query
from pydantic import BaseModel, Field


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class PaginationInfo(GuardianBaseModel):
    offset: int = 0
    limit: int = 1000
    total_count: int = 0


class PaginationRequestMixin(BaseModel):
    offset: int = Query(0, description="The offset for the paginated result.")
    limit: int = Query(
        1000, description="The maximum amount of items to return in one response."
    )


MANAGEMENT_OBJECT_NAME_REGEX = r"[a-z][a-z0-9\-_]*"


class ManagementObjectName(GuardianBaseModel):
    """Name of an app"""

    __root__: str = Field(
        example="object-name", regex=MANAGEMENT_OBJECT_NAME_REGEX, min_length=1
    )
