from fastapi.testclient import TestClient

from tests.test_auth import ALICE, BOB, login, register


def auth_header(client: TestClient, user: dict) -> dict[str, str]:
    token = login(client, user["email"], user["password"])
    return {"Authorization": f"Bearer {token}"}


def test_list_users_is_admin_only(client: TestClient) -> None:
    register(client, ALICE)  # admin (first user)
    register(client, BOB)

    forbidden = client.get("/api/v1/users", headers=auth_header(client, BOB))
    assert forbidden.status_code == 403

    allowed = client.get("/api/v1/users", headers=auth_header(client, ALICE))
    assert allowed.status_code == 200
    assert {u["email"] for u in allowed.json()} == {ALICE["email"], BOB["email"]}


def test_update_me_changes_name_and_password(client: TestClient) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)

    updated = client.patch(
        "/api/v1/users/me",
        json={"full_name": "Alice Renamed", "password": "new-password-99"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Alice Renamed"

    # Old password no longer works, new one does
    old = client.post(
        "/api/v1/auth/login",
        data={"username": ALICE["email"], "password": ALICE["password"]},
    )
    assert old.status_code == 401
    assert login(client, ALICE["email"], "new-password-99")


def test_admin_can_delete_user_but_not_self(client: TestClient) -> None:
    admin = register(client, ALICE)
    bob = register(client, BOB)
    headers = auth_header(client, ALICE)

    self_delete = client.delete(f"/api/v1/users/{admin['id']}", headers=headers)
    assert self_delete.status_code == 400

    deleted = client.delete(f"/api/v1/users/{bob['id']}", headers=headers)
    assert deleted.status_code == 204

    listing = client.get("/api/v1/users", headers=headers)
    assert {u["email"] for u in listing.json()} == {ALICE["email"]}
