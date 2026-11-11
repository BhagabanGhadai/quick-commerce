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
    # The API only returns JSON, so a browser should never load or run anything
    # from it. This is the main XSS defense helmet adds.
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    # Turn off the old browser XSS filter; it caused leaks. CSP replaces it.
    "X-XSS-Protection": "0",
}

# /docs and /redoc are HTML pages that load Swagger UI / ReDoc from a CDN and
# run inline scripts, so they need a looser policy than the API.
DOCS_PATHS = ("/docs", "/redoc")
DOCS_CSP = (
    "default-src 'none'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
    "https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.redoc.ly; "
    "connect-src 'self'; "
    "worker-src blob:; "
    "frame-ancestors 'none'"
)


class SecurityHeadersMiddleware:
    """Adds SECURITY_HEADERS to each HTTP response, unless a route set its own."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        security_headers = SECURITY_HEADERS
        if scope["path"].startswith(DOCS_PATHS):
            security_headers = {**SECURITY_HEADERS, "Content-Security-Policy": DOCS_CSP}

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in security_headers.items():
                    headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, send_with_headers)
