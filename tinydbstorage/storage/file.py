import warnings
from typing import Any, Optional

from tinydb.storages import JSONStorage


class FileStorage(JSONStorage):
    """Deprecated: TinyDB's own JSONStorage does the same."""

    def __init__(
        self,
        path: str,
        create_dirs: bool = False,
        encoding: Optional[str] = None,
        access_mode: str = "r+",
        **kwargs: Any,
    ) -> None:
        warnings.warn(
            "FileStorage is deprecated and will be removed; use tinydb.storages.JSONStorage",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(path, create_dirs, encoding, access_mode, **kwargs)
