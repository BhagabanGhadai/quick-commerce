import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def make_product(client):
    def _make(name="Milk", price=2.5, stock=10) -> dict:
        response = client.post(
            "/products/", json={"name": name, "price": price, "stock": stock}
        )
        assert response.status_code == 201
        return response.json()["data"]

    return _make
