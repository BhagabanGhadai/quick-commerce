"""JSON responses: HTML-safe, and errors in the standard envelope."""

from http import HTTPStatus
from typing import Any

from fastapi.responses import JSONResponse

from core.schemas import ErrorBody, ErrorDetail, ErrorResponse


class SafeJSONResponse(JSONResponse):
    """Escapes <, > and & as \\u003c, \\u003e and \\u0026.

    The decoded JSON is identical, but "</script><script>..." in a string can no
    longer break out if someone embeds the JSON in an HTML page. In JSON these
    characters only appear inside strings, so escaping them is always valid.
    """

    def render(self, content: Any) -> bytes:
        return (
            super()
            .render(content)
            .replace(b"&", b"\\u0026")
            .replace(b"<", b"\\u003c")
            .replace(b">", b"\\u003e")
        )


def error_response(
    status_code: int,
    message: str,
    code: str | None = None,
    details: list[ErrorDetail] | None = None,
    headers: dict[str, str] | None = None,
) -> SafeJSONResponse:
    """Build an error in the standard envelope. `code` defaults to the status
    name, e.g. 404 -> "NOT_FOUND"."""
    body = ErrorBody(
        code=code or HTTPStatus(status_code).name,
        message=message,
        details=details,
    )
    return SafeJSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=body).model_dump(exclude_none=True),
        headers=headers,
    )
