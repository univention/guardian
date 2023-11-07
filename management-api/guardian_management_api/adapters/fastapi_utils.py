from abc import ABC
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError
from starlette import status

from guardian_management_api.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    ParentNotFoundError,
    UnauthorizedError,
)


class TransformExceptionMixin(ABC):
    logger: Any

    async def transform_exception(self, exc: Exception) -> Exception:
        self.logger.exception(exc)
        if isinstance(exc, ObjectNotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": str(exc)},
            )
        if isinstance(exc, ObjectExistsError):
            return HTTPException(
                status_code=400,
                detail={"message": str(exc)},
            )
        if isinstance(exc, UnauthorizedError):
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "Not allowed."},
            )
        if isinstance(exc, ValidationError):  # pragma: no cover
            return HTTPException(
                status_code=422,
                detail={"message": str(exc)},
            )
        if isinstance(exc, ParentNotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": str(exc)},
            )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal Server Error"},
        )
