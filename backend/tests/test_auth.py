from fastapi.testclient import TestClient

ALICE = {"email": "alice@example.com", "full_name": "Alice", "password": "alice-secret-1"}
BOB = {"email": "bob@example.com", "full_name": "Bob", "password": "bob-secret-12"}


def register(client: TestClient, payload: dict) -> dict:
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_first_user_is_admin_then_regular(client: TestClient) -> None:
    assert register(client, ALICE)["role"] == "admin"
    assert register(client, BOB)["role"] == "user"


def test_register_never_returns_password(client: TestClient) -> None:
    body = register(client, ALICE)
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_is_rejected(client: TestClient) -> None:
    register(client, ALICE)
    response = client.post("/api/v1/auth/register", json=ALICE)
    assert response.status_code == 409


def test_login_returns_a_usable_token(client: TestClient) -> None:
    register(client, ALICE)
    token = login(client, ALICE["email"], ALICE["password"])

    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == ALICE["email"]


def test_login_with_wrong_password_fails(client: TestClient) -> None:
    register(client, ALICE)
    response = client.post(
        "/api/v1/auth/login", data={"username": ALICE["email"], "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/users/me").status_code == 401
    bad = client.get("/api/v1/users/me", headers={"Authorization": "Bearer not-a-token"})
    assert bad.status_code == 401
