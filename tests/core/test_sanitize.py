import pytest

from core.sanitize import strip_html


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Salt & Pepper", "Salt & Pepper"),
        ("a < b", "a < b"),
        ("  Milk  ", "Milk"),
        ("<b>Hi</b> there", "Hi there"),
        ("<script>alert(1)</script>Tea", "Tea"),
        ("<img src=x onerror=alert(1)>", ""),
        ('<a href="javascript:alert(1)">click</a>', "click"),
        # Tags hidden behind HTML entities are removed too.
        ("&lt;script&gt;alert(1)&lt;/script&gt;Tea", "Tea"),
        ("&amp;lt;script&amp;gt;x&amp;lt;/script&amp;gt;Tea", "Tea"),
    ],
)
def test_strip_html(raw, expected):
    assert strip_html(raw) == expected
