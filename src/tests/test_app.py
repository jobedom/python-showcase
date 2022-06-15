from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from pytest_asyncio import fixture

import main
from storage import Storage
from download_rules import DownloadRules

MAX_FILE_COUNT = 10
DOWNLOAD_RATE_LIMIT_SIZE_BYTES = 200
DOWNLOAD_RATE_LIMIT_TIME_SECS = 5


@fixture
def client():
    with TemporaryDirectory() as storage_path:
        main.storage = Storage(storage_path)
        main.download_rules = DownloadRules(
            MAX_FILE_COUNT,
            DOWNLOAD_RATE_LIMIT_SIZE_BYTES,
            DOWNLOAD_RATE_LIMIT_TIME_SECS,
        )
        yield TestClient(main.app)


def save_test_file(client, file_name, file_contents=None):
    file_contents = file_contents or f"Contents for {file_name}"
    files_to_upload = {"file": (file_name, file_contents.encode())}
    return client.post("/files", files=files_to_upload)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200  # OK


def test_unknown_endpoint(client):
    response = client.get("/unknown")
    assert response.status_code == 404  # Not found


def test_unknown_methods(client):
    endpoints = ("/health", "/files")
    missing_method_names = ("delete", "put", "options", "head")
    for endpoint in endpoints:
        for missing_method_name in missing_method_names:
            method = getattr(client, missing_method_name)
            assert method(endpoint).status_code == 405  # Method not allowed


def test_empty_storage_get_files(client):
    response = client.get("/files")
    assert response.status_code == 200  # OK
    data = response.json()
    assert data["files"] == []


def test_save_file_count(client):
    save_test_file(client, "file.txt")
    response = client.get("/files")
    data = response.json()
    assert len(data["files"]) == 1


def test_download_saved_file(client):
    file_name = "file.txt"
    new_file_contents = "New file content"
    response = save_test_file(client, file_name, new_file_contents)
    assert response.status_code == 201
    data = response.json()
    file_url = data["url"]
    response = client.get(file_url)
    assert response.text == new_file_contents


def test_download_unknown(client):
    response = client.get("/files/unknown_id")
    assert response.status_code == 404  # Not found


def test_file_count_limit(client):
    for index in range(0, MAX_FILE_COUNT):
        response = save_test_file(client, f"file{index}.txt")
        assert response.status_code == 201  # Created
    response = save_test_file(client, "too_many_files.txt")
    assert response.status_code == 400  # Bad request


def test_download_rate_limit(client):
    response = save_test_file(client, "file.txt", "*" * (DOWNLOAD_RATE_LIMIT_SIZE_BYTES + 1))
    data = response.json()
    file_url = data["url"]
    client.get(file_url)  # Gets through: Rate limit is calculated after the download
    response = client.get(file_url)
    assert response.status_code == 429  # Too many requests
