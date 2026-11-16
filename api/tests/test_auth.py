async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_login_ok(client):
    response = await client.post(
        "/auth/login", json={"email": "ana@test.hr", "password": "ana12345"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_wrong_password_and_unknown_user_return_same_401(client):
    wrong_password = await client.post(
        "/auth/login", json={"email": "ana@test.hr", "password": "kriva"}
    )
    unknown_user = await client.post(
        "/auth/login", json={"email": "nitko@test.hr", "password": "bilosto"}
    )
    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()
    assert wrong_password.json()["code"] == "INVALID_CREDENTIALS"


async def test_login_missing_field_returns_422(client):
    response = await client.post("/auth/login", json={"email": "ana@test.hr"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["errors"][0]["field"] == "password"


async def test_me_without_token_returns_401(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


async def test_me_with_invalid_token_returns_401(client):
    response = await client.get(
        "/auth/me", headers={"Authorization": "Bearer nije.pravi.token"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"


async def test_me_returns_user_without_password_hash(client, ana_headers):
    response = await client.get("/auth/me", headers=ana_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ana@test.hr"
    assert body["role"] == "customer"
    assert "password_hash" not in body


async def test_refresh_returns_new_tokens(client):
    login = await client.post(
        "/auth/login", json={"email": "ana@test.hr", "password": "ana12345"}
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_refresh_with_access_token_returns_401(client):
    login = await client.post(
        "/auth/login", json={"email": "ana@test.hr", "password": "ana12345"}
    )
    access_token = login.json()["access_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"