from fastapi.testclient import TestClient

from tests.conftest import FakeStorage
from tests.test_auth import ALICE, BOB, login, register

CSV_CONTENT = b"sepal_length,sepal_width\n5.1,3.5\n4.9,3.0\n"


def auth_header(client: TestClient, user: dict) -> dict[str, str]:
    token = login(client, user["email"], user["password"])
    return {"Authorization": f"Bearer {token}"}


def upload(client: TestClient, headers: dict, filename: str = "iris.csv", **form) -> dict:
    response = client.post(
        "/api/v1/datasets",
        files={"file": (filename, CSV_CONTENT, "text/csv")},
        data=form,
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_upload_stores_file_and_metadata(client: TestClient, storage: FakeStorage) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)

    body = upload(client, headers)

    assert body["name"] == "iris"
    assert body["format"] == "csv"
    assert body["version"] == 1
    assert body["size_bytes"] == len(CSV_CONTENT)
    # The file itself ended up in object storage
    assert list(storage.objects.values()) == [CSV_CONTENT]


def test_reupload_same_name_creates_new_version(client: TestClient) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)

    first = upload(client, headers)
    second = upload(client, headers)

    assert (first["version"], second["version"]) == (1, 2)


def test_unsupported_extension_is_rejected(client: TestClient, storage: FakeStorage) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)

    response = client.post(
        "/api/v1/datasets",
        files={"file": ("malware.exe", b"nope", "application/octet-stream")},
        headers=headers,
    )

    assert response.status_code == 415
    assert storage.objects == {}


def test_upload_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/datasets", files={"file": ("iris.csv", CSV_CONTENT, "text/csv")}
    )
    assert response.status_code == 401


def test_users_only_see_their_own_datasets(client: TestClient) -> None:
    register(client, ALICE)
    register(client, BOB)
    alice, bob = auth_header(client, ALICE), auth_header(client, BOB)

    alice_dataset = upload(client, alice, filename="alice.csv")
    upload(client, bob, filename="bob.csv")

    names = [d["name"] for d in client.get("/api/v1/datasets", headers=bob).json()]
    assert names == ["bob"]

    # Bob cannot read or delete Alice's dataset — 404, not 403 (no existence leak)
    assert client.get(f"/api/v1/datasets/{alice_dataset['id']}", headers=bob).status_code == 404
    delete = client.delete(f"/api/v1/datasets/{alice_dataset['id']}", headers=bob)
    assert delete.status_code == 404


def test_download_returns_presigned_url(client: TestClient) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)
    dataset = upload(client, headers)

    response = client.get(f"/api/v1/datasets/{dataset['id']}/download", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["url"].startswith("https://storage.test/")
    assert "iris" in body["url"]


def test_delete_removes_row_and_object(client: TestClient, storage: FakeStorage) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)
    dataset = upload(client, headers)

    assert client.delete(f"/api/v1/datasets/{dataset['id']}", headers=headers).status_code == 204
    assert client.get("/api/v1/datasets", headers=headers).json() == []
    assert storage.objects == {}
