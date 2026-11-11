from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from core.hpp import HPPMiddleware

app = FastAPI()
app.add_middleware(HPPMiddleware, allow_lists=["tag"])


@app.get("/echo")
def echo(request: Request):
    return {key: request.query_params.getlist(key) for key in request.query_params}


client = TestClient(app)


def test_repeated_param_keeps_last_value():
    assert client.get("/echo?sort=price&sort=name").json() == {"sort": ["name"]}


def test_allowed_list_param_keeps_all_values():
    response = client.get("/echo?tag=a&tag=b&sort=x&sort=y")

    assert response.json() == {"tag": ["a", "b"], "sort": ["y"]}


def test_non_ascii_values_survive():
    response = client.get("/echo", params=[("q", "café"), ("q", "दूध")])

    assert response.json() == {"q": ["दूध"]}
