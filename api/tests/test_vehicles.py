from datetime import date, timedelta

NEW_VEHICLE = {
    "category_id": 1,
    "brand": "Renault",
    "model": "Clio",
    "license_plate": "ZD-002-AA",
    "year": 2023,
}


async def test_list_vehicles_is_public(client):
    response = await client.get("/vehicles")
    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_filter_vehicles_by_category(client, admin_headers):
    category = await client.post(
        "/categories", json={"name": "SUV", "daily_price": 80}, headers=admin_headers
    )
    suv_id = category.json()["id"]
    await client.post(
        "/vehicles",
        json={**NEW_VEHICLE, "category_id": suv_id},
        headers=admin_headers,
    )

    response = await client.get(f"/vehicles?category_id={suv_id}")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["model"] == "Clio"


async def test_admin_creates_vehicle(client, admin_headers):
    response = await client.post("/vehicles", json=NEW_VEHICLE, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["is_active"] is True


async def test_customer_cannot_create_vehicle(client, ana_headers):
    response = await client.post("/vehicles", json=NEW_VEHICLE, headers=ana_headers)
    assert response.status_code == 403


async def test_vehicle_with_missing_category_returns_404(client, admin_headers):
    response = await client.post(
        "/vehicles", json={**NEW_VEHICLE, "category_id": 999}, headers=admin_headers
    )
    assert response.status_code == 404
    assert response.json()["code"] == "CATEGORY_NOT_FOUND"


async def test_duplicate_license_plate_returns_409(client, admin_headers):
    response = await client.post(
        "/vehicles",
        json={**NEW_VEHICLE, "license_plate": "ZD-001-AA"},
        headers=admin_headers,
    )
    assert response.status_code == 409
    assert response.json()["code"] == "LICENSE_PLATE_TAKEN"


async def test_deactivated_vehicle_disappears_from_list(client, admin_headers):
    response = await client.patch(
        "/vehicles/1", json={"is_active": False}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    response = await client.get("/vehicles")
    assert response.json()["total"] == 0


async def test_delete_vehicle_with_reservations_returns_409(
    client, admin_headers, ana_headers
):
    start = date.today() + timedelta(days=10)
    await client.post(
        "/reservations",
        json={
            "vehicle_id": 1,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=2)).isoformat(),
        },
        headers=ana_headers,
    )

    response = await client.delete("/vehicles/1", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "VEHICLE_HAS_RESERVATIONS"


async def test_delete_vehicle_without_reservations(client, admin_headers):
    response = await client.delete("/vehicles/1", headers=admin_headers)
    assert response.status_code == 204

    response = await client.get("/vehicles/1")
    assert response.status_code == 404
