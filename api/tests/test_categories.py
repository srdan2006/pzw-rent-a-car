async def test_list_categories_is_public(client):
    response = await client.get("/categories")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Mali"
    assert body["limit"] == 20
    assert body["offset"] == 0


async def test_pagination_limit_above_100_returns_422(client):
    response = await client.get("/categories?limit=500")
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


async def test_pagination_limit_and_offset(client, admin_headers):
    for name in ["Srednji", "SUV"]:
        await client.post(
            "/categories",
            json={"name": name, "daily_price": 50},
            headers=admin_headers,
        )

    response = await client.get("/categories?limit=2&offset=1")
    body = response.json()
    assert body["total"] == 3
    assert [item["name"] for item in body["items"]] == ["Srednji", "SUV"]


async def test_get_missing_category_returns_404(client):
    response = await client.get("/categories/999")
    assert response.status_code == 404
    assert response.json()["code"] == "CATEGORY_NOT_FOUND"


async def test_create_category_without_token_returns_401(client):
    response = await client.post("/categories", json={"name": "SUV", "daily_price": 80})
    assert response.status_code == 401


async def test_customer_cannot_create_category(client, ana_headers):
    response = await client.post(
        "/categories", json={"name": "SUV", "daily_price": 80}, headers=ana_headers
    )
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


async def test_admin_creates_category(client, admin_headers):
    response = await client.post(
        "/categories", json={"name": "SUV", "daily_price": 80}, headers=admin_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "SUV"
    assert response.json()["daily_price"] == "80.00"


async def test_duplicate_category_name_returns_409(client, admin_headers):
    response = await client.post(
        "/categories", json={"name": "Mali", "daily_price": 40}, headers=admin_headers
    )
    assert response.status_code == 409
    assert response.json()["code"] == "CATEGORY_NAME_TAKEN"


async def test_negative_price_returns_422(client, admin_headers):
    response = await client.post(
        "/categories", json={"name": "SUV", "daily_price": -5}, headers=admin_headers
    )
    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "daily_price"


async def test_patch_changes_only_sent_fields(client, admin_headers):
    response = await client.patch(
        "/categories/1", json={"daily_price": 40}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Mali"
    assert response.json()["daily_price"] == "40.00"


async def test_delete_category_with_vehicles_returns_409(client, admin_headers):
    response = await client.delete("/categories/1", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "CATEGORY_HAS_VEHICLES"


async def test_delete_empty_category(client, admin_headers):
    created = await client.post(
        "/categories", json={"name": "Kombi", "daily_price": 90}, headers=admin_headers
    )
    category_id = created.json()["id"]

    response = await client.delete(f"/categories/{category_id}", headers=admin_headers)
    assert response.status_code == 204

    response = await client.get(f"/categories/{category_id}")
    assert response.status_code == 404