"""Input sanitizing: strip HTML/JS from user-supplied text.

This is defense in depth. The main XSS protection is still escaping on output
(React and other frontends do this by default), and SQL injection is prevented
by parameterized queries, not by cleaning strings.
"""

import html
from typing import Annotated

import nh3
from pydantic import AfterValidator

_MAX_PASSES = 5


def strip_html(value: str) -> str:
    """Return plain text with all tags removed (script/style including content).

    nh3 escapes what it keeps ("&" -> "&amp;"), so we unescape to store plain
    text. Unescaping can reveal hidden tags ("&lt;script&gt;" -> "<script>"),
    so we clean again until nothing changes.
    """
    for _ in range(_MAX_PASSES):
        cleaned = html.unescape(nh3.clean(value, tags=set()))
        if cleaned == value:
            return cleaned.strip()
        value = cleaned
    # Still changing after several passes: keep the escaped form, which is safe.
    return nh3.clean(value, tags=set()).strip()


# Use instead of `str` for any free-text field that comes from users.
SafeStr = Annotated[str, AfterValidator(strip_html)]
