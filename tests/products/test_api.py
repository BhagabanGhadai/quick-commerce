def test_create_and_get_product(client, make_product):
    product = make_product(name="Bread", price=1.75, stock=5)

    response = client.get(f"/products/{product['id']}")

    assert response.status_code == 200
    assert response.json() == product


def test_get_missing_product_returns_404(client):
    response = client.get("/products/999999")

    assert response.status_code == 404


def test_delete_product(client, make_product):
    product = make_product()

    assert client.delete(f"/products/{product['id']}").status_code == 204
    assert client.get(f"/products/{product['id']}").status_code == 404


def test_create_product_strips_html_from_name(make_product):
    product = make_product(name="<script>alert(1)</script><b>Tea</b> & Biscuits")

    assert product["name"] == "Tea & Biscuits"


def test_create_product_rejects_name_that_is_only_html(client):
    response = client.post("/products/", json={"name": "<img src=x>", "price": 1})

    assert response.status_code == 422
