"""Response compression (zstd/brotli/gzip), skipped where secrets are returned.

Compressing a response that holds a secret (like a JWT) next to text an attacker
can influence lets them guess the secret from the compressed size (the BREACH
attack). So routes that hand out tokens are never compressed.
"""

from collections.abc import Iterable

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette_compress import CompressMiddleware


class CompressionMiddleware:
    def __init__(
        self, app: ASGIApp, excluded_paths: Iterable[str], minimum_size: int = 1000
    ) -> None:
        self.app = app
        self.compressed_app = CompressMiddleware(app, minimum_size=minimum_size)
        self.excluded_paths = tuple(p.rstrip("/") for p in excluded_paths)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and not self._is_excluded(scope["path"]):
            await self.compressed_app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def _is_excluded(self, path: str) -> bool:
        # "/auth" excludes "/auth" and "/auth/login", but not "/authors".
        return any(path == p or path.startswith(p + "/") for p in self.excluded_paths)
