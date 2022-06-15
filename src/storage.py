import os
import hashlib
from pathlib import Path


class Storage:
    def __init__(self, storage_path):
        self.storage_path = Path(storage_path)
        if not self.storage_path.is_absolute():
            self.storage_path = Path(__file__).parent / storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.files_metadata = {}
        self._get_existing_files_metadata()

    def get_files_metadata(self):
        return list(self.files_metadata.values())

    def get_file_metadata(self, file_id):
        return self.files_metadata.get(file_id)

    def save_file(self, file_name, file_contents):
        if type(file_contents) == str:
            file_contents = file_contents.encode()
        file_path = self.storage_path / file_name
        with open(file_path, "wb") as file_handle:
            file_handle.write(file_contents)
        file_metadata = self._get_file_metadata(file_path)
        self.files_metadata[file_metadata["id"]] = file_metadata
        return file_metadata["id"]

    def get_file_count(self):
        return len(self.files_metadata)

    def _get_existing_files_metadata(self):
        for entry in self.storage_path.glob("*"):
            file_metadata = self._get_file_metadata(self.storage_path / entry.name)
            self.files_metadata[file_metadata["id"]] = file_metadata

    def _get_file_metadata(self, file_path):
        file_name = os.path.basename(file_path)
        file_id = self._generate_id(file_name)
        return {
            "id": file_id,
            "name": file_name,
            "path": file_path,
            "size": os.path.getsize(file_path),
        }

    def _generate_id(self, file_name):
        return hashlib.sha1(file_name.encode()).hexdigest()
