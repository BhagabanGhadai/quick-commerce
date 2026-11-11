"""Reject request bodies over a size limit with 413, before they fill memory."""

from fastapi import HTTPException
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BodySizeLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Fast path: the client told us the size up front.
        content_length = dict(scope["headers"]).get(b"content-length")
        if (
            content_length
            and content_length.isdigit()
            and int(content_length) > self.max_bytes
        ):
            await self._too_large(scope, receive, send)
            return

        # Chunked uploads have no Content-Length, so count bytes as they arrive.
        received = 0
        response_started = False

        async def counting_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    # FastAPI re-raises HTTPException from body reading, so routes
                    # answer 413 through the normal error handling.
                    raise HTTPException(status_code=413, detail=self._detail())
            return message

        async def send_and_track(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, counting_receive, send_and_track)
        except HTTPException as exc:
            if exc.status_code != 413 or response_started:
                raise
            await self._too_large(scope, receive, send)

    def _detail(self) -> str:
        return f"Request body too large (max {self.max_bytes} bytes)"

    async def _too_large(self, scope: Scope, receive: Receive, send: Send) -> None:
        response = JSONResponse({"detail": self._detail()}, status_code=413)
        await response(scope, receive, send)
