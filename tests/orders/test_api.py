def test_place_order_takes_stock(client, make_product):
    milk = make_product(name="Milk", price=2.5, stock=10)
    eggs = make_product(name="Eggs", price=4.0, stock=3)

    response = client.post(
        "/orders/",
        json={
            "items": [
                {"product_id": milk["id"], "quantity": 2},
                {"product_id": eggs["id"], "quantity": 1},
                {"product_id": milk["id"], "quantity": 1},
            ]
        },
    )

    assert response.status_code == 201
    assert response.json()["total"] == 11.5
    assert client.get(f"/products/{milk['id']}").json()["stock"] == 7
    assert client.get(f"/products/{eggs['id']}").json()["stock"] == 2


def test_order_fails_without_changing_stock(client, make_product):
    milk = make_product(stock=10)
    eggs = make_product(name="Eggs", stock=1)

    response = client.post(
        "/orders/",
        json={
            "items": [
                {"product_id": milk["id"], "quantity": 2},
                {"product_id": eggs["id"], "quantity": 5},
            ]
        },
    )

    assert response.status_code == 409
    assert client.get(f"/products/{milk['id']}").json()["stock"] == 10


def test_order_with_unknown_product_returns_404(client):
    response = client.post(
        "/orders/", json={"items": [{"product_id": 999999, "quantity": 1}]}
    )

    assert response.status_code == 404
