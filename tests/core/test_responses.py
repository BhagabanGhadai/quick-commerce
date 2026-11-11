"""Every response uses the standard envelope (see core/schemas.py)."""

import pytest
from fastapi.testclient import TestClient

from main import app


def test_success_wraps_data(client, make_product):
    product = make_product(name="Milk")

    response = client.get("/products/")

    assert response.json() == {"success": True, "data": [product]}


@pytest.mark.parametrize(
    ("method", "path", "status", "code"),
    [
        ("GET", "/products/999999", 404, "NOT_FOUND"),  # raised by a service
        ("GET", "/no-such-route", 404, "NOT_FOUND"),  # raised by FastAPI
        ("PUT", "/products/1", 405, "METHOD_NOT_ALLOWED"),
    ],
)
def test_errors_use_envelope(client, method, path, status, code):
    response = client.request(method, path)

    assert response.status_code == status
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == code
    assert body["error"]["message"]


def test_validation_error_lists_fields_without_echoing_input(client):
    response = client.post("/products/", json={"name": "Tea", "price": "<svg/>"})

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": [
                {
                    "field": "body.price",
                    "message": "Input should be a valid number, "
                    "unable to parse string as a number",
                }
            ],
        },
    }


def test_unexpected_error_hides_internals(monkeypatch):
    from apps.products import service

    def explode():
        raise RuntimeError("db password is hunter2")

    monkeypatch.setattr(service, "list_products", explode)
    # Debug mode shows tracebacks instead, so test the production behaviour.
    # The middleware stack captures `debug` when built, so force a rebuild.
    monkeypatch.setattr(app, "debug", False)
    monkeypatch.setattr(app, "middleware_stack", None)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/products/")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong"},
    }
