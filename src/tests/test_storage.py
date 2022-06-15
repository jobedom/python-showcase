from tempfile import TemporaryDirectory
from pytest import fixture

from storage import Storage

TEST_FILE_COUNT = 3


@fixture
def empty_storage():
    with TemporaryDirectory() as storage_path:
        yield Storage(storage_path)


@fixture
def non_empty_storage():
    with TemporaryDirectory() as storage_path:
        storage = Storage(storage_path)
        for index in range(0, TEST_FILE_COUNT):
            storage.save_file(f"file{index}", "contents of file {index}")
        yield storage


def test_empty_storage_file_count(empty_storage):
    assert empty_storage.get_file_count() == 0


def test_non_empty_storage_file_count(non_empty_storage):
    assert non_empty_storage.get_file_count() == TEST_FILE_COUNT


def test_empty_storage_get_files_metadata(empty_storage):
    files_metadata = empty_storage.get_files_metadata()
    assert files_metadata == []


def test_non_empty_storage_get_files_metadata(non_empty_storage):
    files_metadata = non_empty_storage.get_files_metadata()
    assert type(files_metadata) == list
    assert len(files_metadata) == TEST_FILE_COUNT


def test_get_file_metadata(non_empty_storage):
    files_metadata = non_empty_storage.get_files_metadata()
    first_file_metadata = files_metadata[0].copy()  # Clone to avoid the possibility of referencing same dict
    first_file_id = first_file_metadata["id"]
    retrieved_file_metadata = non_empty_storage.get_file_metadata(first_file_id)
    assert retrieved_file_metadata == first_file_metadata


def test_get_unknown_file_metadata(non_empty_storage):
    retrieved_file_metadata = non_empty_storage.get_file_metadata("unknown_id")
    assert retrieved_file_metadata is None


def test_ovewrite_existing_file(non_empty_storage):
    new_content = "new content"
    first_file_metadata = non_empty_storage.get_files_metadata()[0]
    saved_file_id = non_empty_storage.save_file(first_file_metadata["name"], new_content)
    with open(first_file_metadata["path"], "r") as first_file:
        saved_file_content = first_file.read()
    assert saved_file_id == first_file_metadata["id"]
    assert non_empty_storage.get_file_count() == TEST_FILE_COUNT
    assert saved_file_content == new_content


def test_save_new_file(non_empty_storage):
    new_content = "new content"
    new_file_name = f"file{TEST_FILE_COUNT}"
    new_file_id = non_empty_storage.save_file(new_file_name, new_content)
    file_metadata = non_empty_storage.get_file_metadata(new_file_id)
    with open(file_metadata["path"], "r") as new_file:
        saved_file_content = new_file.read()
    assert non_empty_storage.get_file_count() == TEST_FILE_COUNT + 1
    assert saved_file_content == new_content
