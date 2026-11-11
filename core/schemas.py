"""The standard response envelope every endpoint uses.

Success: {"success": true,  "data": ...}
Error:   {"success": false, "error": {"code": ..., "message": ..., "details": ...}}
"""

from typing import Literal

from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    success: Literal[True] = True
    data: T


class ErrorDetail(BaseModel):
    field: str | None = None  # e.g. "body.items.0.quantity"
    message: str


class ErrorBody(BaseModel):
    code: str  # stable, machine-readable, e.g. "NOT_FOUND"
    message: str  # human-readable
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorBody
