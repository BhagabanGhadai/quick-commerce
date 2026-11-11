import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.timeout import TimeoutMiddleware

app = FastAPI()
app.add_middleware(TimeoutMiddleware, seconds=0.05)


@app.get("/slow")
async def slow():
    await asyncio.sleep(1)


@app.get("/fast")
async def fast():
    return {"ok": True}


client = TestClient(app)


def test_slow_request_returns_504():
    response = client.get("/slow")

    assert response.status_code == 504
    assert response.json() == {"detail": "Request timed out"}


def test_fast_request_is_untouched():
    assert client.get("/fast").json() == {"ok": True}
