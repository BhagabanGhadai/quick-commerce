import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.compression import CompressionMiddleware

BIG = {"data": "x" * 5000}

app = FastAPI()
app.add_middleware(CompressionMiddleware, excluded_paths=["/auth"])


@app.get("/products")
@app.get("/auth/login")
@app.get("/authors")
def big():
    return BIG


client = TestClient(app)


@pytest.mark.parametrize("encoding", ["gzip", "br"])
def test_large_response_is_compressed(encoding):
    response = client.get("/products", headers={"Accept-Encoding": encoding})

    assert response.headers["content-encoding"] == encoding
    assert response.json() == BIG


def test_token_routes_are_never_compressed():
    response = client.get("/auth/login", headers={"Accept-Encoding": "gzip, br"})

    assert "content-encoding" not in response.headers


def test_exclusion_matches_whole_path_segments():
    response = client.get("/authors", headers={"Accept-Encoding": "gzip"})

    assert response.headers["content-encoding"] == "gzip"
