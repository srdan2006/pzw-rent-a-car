from freezegun import freeze_time

from tests.conftest import login_headers
from tests.test_reservations import create_reservation, future


# --- Kapacitet: preklapanje termina ---


async def test_overlapping_reservation_returns_409(client, ana_headers, marko_headers):
    await create_reservation(client, ana_headers, future(10), future(14))

    response = await create_reservation(client, marko_headers, future(12), future(16))
    assert response.status_code == 409
    assert response.json()["code"] == "VEHICLE_NOT_AVAILABLE"


async def test_reservation_inside_existing_returns_409(client, ana_headers, marko_headers):
    await create_reservation(client, ana_headers, future(10), future(20))

    response = await create_reservation(client, marko_headers, future(12), future(14))
    assert response.status_code == 409


async def test_pickup_on_return_day_is_allowed(client, ana_headers, marko_headers):
    await create_reservation(client, ana_headers, future(10), future(14))

    response = await create_reservation(client, marko_headers, future(14), future(16))
    assert response.status_code == 201


async def test_cancelled_reservation_frees_vehicle(client, ana_headers, marko_headers):
    created = await create_reservation(client, ana_headers, future(10), future(14))
    await client.post(f"/reservations/{created.json()['id']}/cancel", headers=ana_headers)

    response = await create_reservation(client, marko_headers, future(10), future(14))
    assert response.status_code == 201


# --- Prijelaz statusa ---


async def test_customer_cannot_change_status(client, ana_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))

    response = await client.patch(
        f"/reservations/{created.json()['id']}/status",
        json={"status": "confirmed"},
        headers=ana_headers,
    )
    assert response.status_code == 403


async def test_full_status_flow(client, ana_headers, admin_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))
    url = f"/reservations/{created.json()['id']}/status"

    for status in ["confirmed", "active", "returned"]:
        response = await client.patch(url, json={"status": status}, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == status


async def test_skipping_status_returns_409(client, ana_headers, admin_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))

    response = await client.patch(
        f"/reservations/{created.json()['id']}/status",
        json={"status": "returned"},
        headers=admin_headers,
    )
    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATUS_TRANSITION"


async def test_unknown_status_returns_422(client, ana_headers, admin_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))

    response = await client.patch(
        f"/reservations/{created.json()['id']}/status",
        json={"status": "pobjegao"},
        headers=admin_headers,
    )
    assert response.status_code == 422


async def test_active_reservation_cannot_be_cancelled(client, ana_headers, admin_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))
    reservation_id = created.json()["id"]
    for status in ["confirmed", "active"]:
        await client.patch(
            f"/reservations/{reservation_id}/status",
            json={"status": status},
            headers=admin_headers,
        )

    response = await client.post(
        f"/reservations/{reservation_id}/cancel", headers=ana_headers
    )
    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATUS_TRANSITION"


async def test_cancel_twice_returns_409(client, ana_headers):
    created = await create_reservation(client, ana_headers, future(10), future(12))
    url = f"/reservations/{created.json()['id']}/cancel"

    first = await client.post(url, headers=ana_headers)
    second = await client.post(url, headers=ana_headers)
    assert first.status_code == 200
    assert first.json()["status"] == "cancelled"
    assert second.status_code == 409


# --- Rok: otkazivanje najkasnije dan prije preuzimanja (zamrznuto vrijeme) ---


async def test_cancel_day_before_pickup_is_allowed(client):
    with freeze_time("2030-06-01 10:00", real_asyncio=True) as frozen:
        headers = await login_headers(client, "ana@test.hr")
        created = await create_reservation(client, headers, "2030-06-10", "2030-06-12")

        frozen.move_to("2030-06-09 23:59")
        headers = await login_headers(client, "ana@test.hr")
        response = await client.post(
            f"/reservations/{created.json()['id']}/cancel", headers=headers
        )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_cancel_on_pickup_day_returns_409(client):
    with freeze_time("2030-06-01 10:00", real_asyncio=True) as frozen:
        headers = await login_headers(client, "ana@test.hr")
        created = await create_reservation(client, headers, "2030-06-10", "2030-06-12")

        frozen.move_to("2030-06-10 00:00")
        headers = await login_headers(client, "ana@test.hr")
        response = await client.post(
            f"/reservations/{created.json()['id']}/cancel", headers=headers
        )

    assert response.status_code == 409
    assert response.json()["code"] == "CANCELLATION_DEADLINE_PASSED"


async def test_cancel_after_pickup_day_returns_409(client):
    with freeze_time("2030-06-01 10:00", real_asyncio=True) as frozen:
        headers = await login_headers(client, "ana@test.hr")
        created = await create_reservation(client, headers, "2030-06-10", "2030-06-12")

        frozen.move_to("2030-06-11 12:00")
        headers = await login_headers(client, "ana@test.hr")
        response = await client.post(
            f"/reservations/{created.json()['id']}/cancel", headers=headers
        )

    assert response.status_code == 409
    assert response.json()["code"] == "CANCELLATION_DEADLINE_PASSED"