from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from core.body_limit import BodySizeLimitMiddleware


class Item(BaseModel):
    name: str


app = FastAPI()
app.add_middleware(BodySizeLimitMiddleware, max_bytes=100)


@app.post("/items")
def create(item: Item):
    return item


client = TestClient(app)


def test_small_body_is_accepted():
    assert client.post("/items", json={"name": "Tea"}).status_code == 200


def test_body_over_limit_is_rejected():
    response = client.post("/items", json={"name": "x" * 200})

    assert response.status_code == 413


def test_chunked_body_over_limit_is_rejected():
    def chunks():
        yield b'{"name": "'
        yield b"x" * 200
        yield b'"}'

    response = client.post(
        "/items", content=chunks(), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 413
