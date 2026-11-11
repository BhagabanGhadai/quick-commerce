"""HTTP Parameter Pollution protection (the Python equivalent of `hpp`).

`?sort=price&sort=name` is collapsed to `?sort=name` (the last value wins), so
code reading `request.query_params` never gets surprised by a repeated key.
Params meant to be lists (e.g. `?tag=a&tag=b`) must be listed in `allow_lists`.
"""

from collections.abc import Iterable
from urllib.parse import parse_qsl, urlencode

from starlette.types import ASGIApp, Receive, Scope, Send


class HPPMiddleware:
    def __init__(self, app: ASGIApp, allow_lists: Iterable[str] = ()) -> None:
        self.app = app
        self.allow_lists = frozenset(allow_lists)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["query_string"]:
            deduped = self._dedupe(scope["query_string"])
            if deduped is not None:
                scope = dict(scope, query_string=deduped)
        await self.app(scope, receive, send)

    def _dedupe(self, query_string: bytes) -> bytes | None:
        """Return the cleaned query string, or None if nothing was repeated."""
        # latin-1 maps bytes 1:1 to characters, so the round trip is lossless.
        pairs = parse_qsl(
            query_string.decode("latin-1"), keep_blank_values=True, encoding="latin-1"
        )
        list_pairs = [(k, v) for k, v in pairs if k in self.allow_lists]
        last_values = {k: v for k, v in pairs if k not in self.allow_lists}
        if len(list_pairs) + len(last_values) == len(pairs):
            return None
        kept = list_pairs + list(last_values.items())
        return urlencode(kept, encoding="latin-1").encode("latin-1")
