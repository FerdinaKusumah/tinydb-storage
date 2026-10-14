import json
from typing import Any, Optional, Union

import redis
from tinydb.storages import Storage

from tinydbstorage.constants import DEFAULT_REDIS_KEY
from tinydbstorage.errors import StorageConflictError

JsonData = dict[str, dict[str, Any]]
_UNREAD = object()


class RedisStorage(Storage):
    """TinyDB storage that keeps the whole database as one JSON value in Redis.

    Read errors are raised, never read as an empty database, and a write fails
    with StorageConflictError when another writer changed the key since this
    storage last read it (`check_conflicts=False` restores last-write-wins).

    >>> db = TinyDB(storage=RedisStorage, redis_uri="redis://localhost:6379/0")
    """

    def __init__(
        self,
        redis_uri: Optional[str] = None,
        key: Optional[str] = None,
        client: Optional[redis.Redis] = None,
        check_conflicts: bool = True,
        **kwargs: Any,
    ) -> None:
        # Before 0.2.0 the key was `prefix`, which was also passed on to redis and failed there.
        legacy_key = kwargs.pop("prefix", None)
        self.key = key or legacy_key or DEFAULT_REDIS_KEY
        if client is None and redis_uri is None:
            raise ValueError("RedisStorage needs a redis_uri or a client")
        self.owns_connection = client is None
        self.connection = (
            client if client is not None else redis.Redis.from_url(redis_uri, **kwargs)
        )
        self.check_conflicts = check_conflicts
        self._last_seen: Any = _UNREAD

    def read(self) -> Optional[JsonData]:
        raw = self._as_text(self.connection.get(self.key))
        self._last_seen = raw
        return None if raw is None else json.loads(raw)

    def write(self, data: JsonData) -> None:
        payload = json.dumps(data)
        if self.check_conflicts and self._last_seen is not _UNREAD:
            self._write_if_unchanged(payload)
        else:
            self.connection.set(self.key, payload)
        self._last_seen = payload

    def close(self) -> None:
        if self.owns_connection:
            self.connection.close()

    def _write_if_unchanged(self, payload: str) -> None:
        with self.connection.pipeline() as pipe:
            try:
                pipe.watch(self.key)
                if self._as_text(pipe.get(self.key)) != self._last_seen:
                    raise self._conflict()
                pipe.multi()
                pipe.set(self.key, payload)
                pipe.execute()
            except redis.WatchError as e:
                raise self._conflict() from e

    def _conflict(self) -> StorageConflictError:
        return StorageConflictError(f"Redis key {self.key!r} changed since it was read")

    @staticmethod
    def _as_text(value: Union[bytes, str, None]) -> Optional[str]:
        return value.decode() if isinstance(value, bytes) else value

    def __repr__(self) -> str:
        return f"RedisStorage(key={self.key!r})"
