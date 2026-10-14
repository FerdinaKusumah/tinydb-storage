import warnings

from tinydb.storages import MemoryStorage as TinyDBMemoryStorage


class MemoryStorage(TinyDBMemoryStorage):
    """Deprecated: TinyDB's own MemoryStorage does the same."""

    def __init__(self) -> None:
        warnings.warn(
            "MemoryStorage is deprecated and will be removed; use tinydb.storages.MemoryStorage",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__()
