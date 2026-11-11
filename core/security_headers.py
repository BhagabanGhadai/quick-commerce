"""Security headers on every response (the Python equivalent of helmet)."""

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

SECURITY_HEADERS = {
    # Turn off browser features this API never needs.
    "Permissions-Policy": (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
        "interest-cohort=()"
    ),
    # Don't leak our URLs to other sites.
    "Referrer-Policy": "no-referrer",
    # Browsers must use HTTPS for 2 years. Ignored over plain HTTP.
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
    # Never allow being shown inside an iframe (blocks clickjacking).
    "X-Frame-Options": "DENY",
    # Don't let browsers guess content types (e.g. run JSON as a script).
    "X-Content-Type-Options": "nosniff",
}


class SecurityHeadersMiddleware:
    """Adds SECURITY_HEADERS to each HTTP response, unless a route set its own."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in SECURITY_HEADERS.items():
                    headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, send_with_headers)
