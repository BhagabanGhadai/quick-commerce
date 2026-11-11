"""JSON responses that are safe even if a page puts them inside HTML."""

from typing import Any

from fastapi.responses import JSONResponse


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
