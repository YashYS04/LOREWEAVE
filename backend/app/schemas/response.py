"""Standard API response envelopes.

All endpoints return one of these two shapes:

Success::

    {"success": true, "message": "...", "data": {...}}

Failure::

    {"success": false, "error": {"code": "...", "message": "..."}}
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiSuccess(BaseModel, Generic[DataT]):  # noqa: UP046
    success: bool = True
    message: str
    data: DataT


class ApiErrorDetail(BaseModel):
    code: str
    message: str


class ApiError(BaseModel):
    success: bool = False
    error: ApiErrorDetail


def success(data: Any, message: str = "OK") -> dict[str, Any]:
    """Build a success envelope dict (used directly in JSONResponse)."""
    return {"success": True, "message": message, "data": data}


def error(code: str, message: str) -> dict[str, Any]:
    """Build an error envelope dict (used directly in JSONResponse)."""
    return {"success": False, "error": {"code": code, "message": message}}
