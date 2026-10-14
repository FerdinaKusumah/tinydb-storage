from pathlib import Path

import pytest
from tinydb import TinyDB

from tinydbstorage.storage import FileStorage, MemoryStorage


class TestDeprecatedStorages:
    def test_file_storage_warns_and_still_works(self, tmp_path: Path) -> None:
        path = tmp_path / "db.json"
        with pytest.warns(DeprecationWarning, match="JSONStorage"):
            db = TinyDB(str(path), storage=FileStorage)
        db.insert({"name": "a"})
        db.close()
        assert path.read_text()

    def test_memory_storage_warns_and_still_works(self) -> None:
        with pytest.warns(DeprecationWarning, match="MemoryStorage"):
            db = TinyDB(storage=MemoryStorage)
        db.insert({"name": "a"})
        assert db.all() == [{"name": "a"}]
