from datetime import date, timedelta


def future(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


async def create_reservation(
    client, headers, start: str, end: str, vehicle_id: int = 1
):
    return await client.post(
        "/reservations",
        json={"vehicle_id": vehicle_id, "start_date": start, "end_date": end},
        headers=headers,
    )


async def test_customer_creates_reservation(client, ana_headers):
    response = await create_reservation(client, ana_headers, future(10), future(13))
    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == 2
    assert body["status"] == "pending"
    assert body["total_price"] == "105.00"


async def test_reservation_requires_login(client):
    response = await client.get("/reservations")
    assert response.status_code == 401


async def test_customer_sees_only_own_reservations(
    client, ana_headers, marko_headers, admin_headers
):
    await create_reservation(client, ana_headers, future(10), future(12))

    marko_list = await client.get("/reservations", headers=marko_headers)
    assert marko_list.json()["total"] == 0

    ana_list = await client.get("/reservations", headers=ana_headers)
    assert ana_list.json()["total"] == 1

    admin_list = await client.get("/reservations", headers=admin_headers)
    assert admin_list.json()["total"] == 1


async def test_customer_cannot_see_others_reservation(
    client, ana_headers, marko_headers
):
    created = await create_reservation(client, ana_headers, future(10), future(12))
    reservation_id = created.json()["id"]

    response = await client.get(
        f"/reservations/{reservation_id}", headers=marko_headers
    )
    assert response.status_code == 404
    assert response.json()["code"] == "RESERVATION_NOT_FOUND"


async def test_customer_cannot_cancel_others_reservation(
    client, ana_headers, marko_headers
):
    created = await create_reservation(client, ana_headers, future(10), future(12))
    reservation_id = created.json()["id"]

    response = await client.post(
        f"/reservations/{reservation_id}/cancel", headers=marko_headers
    )
    assert response.status_code == 404


async def test_admin_sees_any_reservation(client, ana_headers, admin_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))
    reservation_id = created.json()["id"]

    response = await client.get(
        f"/reservations/{reservation_id}", headers=admin_headers
    )
    assert response.status_code == 200


async def test_end_before_start_returns_400(client, ana_headers):
    response = await create_reservation(client, ana_headers, future(12), future(10))
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_DATE_RANGE"


async def test_start_in_past_returns_400(client, ana_headers):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = await create_reservation(client, ana_headers, yesterday, future(2))
    assert response.status_code == 400
    assert response.json()["code"] == "START_DATE_IN_PAST"


async def test_inactive_vehicle_returns_409(client, ana_headers, admin_headers):
    await client.patch("/vehicles/1", json={"is_active": False}, headers=admin_headers)

    response = await create_reservation(client, ana_headers, future(10), future(12))
    assert response.status_code == 409
    assert response.json()["code"] == "VEHICLE_INACTIVE"
