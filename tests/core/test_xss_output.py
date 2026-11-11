def test_json_responses_escape_html_characters(client, make_product):
    product = make_product(name="Salt & Pepper > Sugar")

    response = client.get(f"/products/{product['id']}")

    assert "&" not in response.text
    assert ">" not in response.text
    assert response.json()["name"] == "Salt & Pepper > Sugar"  # decodes unchanged


def test_validation_errors_do_not_echo_raw_html(client):
    response = client.post("/products/", json={"name": "Tea", "price": "<svg/>"})

    assert response.status_code == 422
    assert "<svg" not in response.text
