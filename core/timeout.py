"""Request timeout: answer 504 instead of letting slow requests hang forever."""

import asyncio
import logging

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class TimeoutMiddleware:
    def __init__(self, app: ASGIApp, seconds: float) -> None:
        self.app = app
        self.seconds = seconds

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_and_track(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        timer = asyncio.timeout(self.seconds)
        try:
            async with timer:
                await self.app(scope, receive, send_and_track)
        except TimeoutError:
            # Re-raise if the app raised TimeoutError itself, or if the response
            # already started (too late to send a different one).
            if not timer.expired() or response_started:
                raise
            logger.warning(
                "%s %s timed out after %ss",
                scope["method"],
                scope["path"],
                self.seconds,
            )
            response = JSONResponse({"detail": "Request timed out"}, status_code=504)
            await response(scope, receive, send)
