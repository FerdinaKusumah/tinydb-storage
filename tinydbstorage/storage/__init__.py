import importlib
from typing import Any

_MODULES = {
    "FileStorage": "tinydbstorage.storage.file",
    "MemoryStorage": "tinydbstorage.storage.memory",
    "RedisStorage": "tinydbstorage.storage.redis",
    "S3Storage": "tinydbstorage.storage.s3",
}

__all__ = list(_MODULES)


def __getattr__(name: str) -> Any:
    # Imported on first use, so installing only the redis or only the s3 extra works.
    if name not in _MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(importlib.import_module(_MODULES[name]), name)
