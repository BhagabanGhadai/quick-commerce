"""Errors shared by every module.

Services raise these instead of HTTPException, so business code stays free of
HTTP details. The handler below turns them into JSON responses.
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import Response

from core.responses import SafeJSONResponse


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


async def _handle_app_error(_: Request, exc: AppError) -> Response:
    return SafeJSONResponse(
        status_code=exc.status_code, content={"detail": exc.message}
    )


# FastAPI's own handlers for the two below use plain JSONResponse. Validation
# errors echo the user's input back, so we send them through SafeJSONResponse.
async def _handle_validation_error(_: Request, exc: RequestValidationError) -> Response:
    return SafeJSONResponse(
        status_code=422, content={"detail": jsonable_encoder(exc.errors())}
    )


async def _handle_http_error(_: Request, exc: HTTPException) -> Response:
    if exc.status_code in (204, 304):  # these must not have a body
        return Response(status_code=exc.status_code, headers=exc.headers)
    return SafeJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(HTTPException, _handle_http_error)
