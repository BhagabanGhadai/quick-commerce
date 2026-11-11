import pytest

from core.security_headers import DOCS_CSP, SECURITY_HEADERS


@pytest.mark.parametrize(
    ("method", "path", "headers"),
    [
        ("GET", "/health", {}),
        ("GET", "/does-not-exist", {}),
        # CORS preflight is answered by CORSMiddleware before reaching routes.
        (
            "OPTIONS",
            "/health",
            {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        ),
    ],
)
def test_security_headers_on_every_response(client, method, path, headers):
    response = client.request(method, path, headers=headers)

    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_docs_get_a_csp_that_allows_swagger_ui(client):
    response = client.get("/docs")

    assert response.headers["Content-Security-Policy"] == DOCS_CSP
