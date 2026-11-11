"""Errors shared by every module, and the handlers that format them.

Services raise these instead of HTTPException, so business code stays free of
HTTP details. Every error leaves the API in the standard envelope (see
core/schemas.py), whatever raised it.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import Response

from core.responses import error_response
from core.schemas import ErrorDetail

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code  # e.g. "OUT_OF_STOCK"; defaults to the status name


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


async def _handle_app_error(_: Request, exc: AppError) -> Response:
    return error_response(exc.status_code, exc.message, code=exc.code)


async def _handle_validation_error(_: Request, exc: RequestValidationError) -> Response:
    # Only field + message: pydantic's raw errors also echo the user's input.
    details = [
        ErrorDetail(field=".".join(map(str, err["loc"])), message=err["msg"])
        for err in exc.errors()
    ]
    return error_response(
        422, "Request validation failed", code="VALIDATION_ERROR", details=details
    )


async def _handle_http_error(_: Request, exc: HTTPException) -> Response:
    if exc.status_code in (204, 304):  # these must not have a body
        return Response(status_code=exc.status_code, headers=exc.headers)
    return error_response(exc.status_code, str(exc.detail), headers=exc.headers)


async def _handle_unexpected_error(request: Request, exc: Exception) -> Response:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    # Never leak internals (stack traces, SQL, file paths) to the client.
    return error_response(500, "Something went wrong", code="INTERNAL_ERROR")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(HTTPException, _handle_http_error)
    app.add_exception_handler(Exception, _handle_unexpected_error)
