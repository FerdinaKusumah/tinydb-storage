import subprocess
import sys

import pytest

import tinydbstorage.storage as storage

WITHOUT = "import sys; sys.modules['{blocked}'] = None; "


def run(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


class TestOptionalExtras:
    @pytest.mark.parametrize("blocked", ["redis", "boto3"])
    def test_the_package_imports_without_an_extra(self, blocked: str) -> None:
        result = run(
            WITHOUT.format(blocked=blocked)
            + "import tinydbstorage; from tinydbstorage.storage import MemoryStorage; print('ok')"
        )
        assert result.stdout.strip() == "ok", result.stderr

    @pytest.mark.parametrize(
        "blocked, name", [("redis", "RedisStorage"), ("boto3", "S3Storage")]
    )
    def test_a_storage_needs_its_extra(self, blocked: str, name: str) -> None:
        result = run(
            WITHOUT.format(blocked=blocked)
            + f"from tinydbstorage.storage import {name}"
        )
        assert result.returncode != 0
        assert "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr

    def test_unknown_names_raise_attribute_error(self) -> None:
        with pytest.raises(AttributeError):
            storage.NoSuchStorage  # noqa: B018
