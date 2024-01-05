import json
from collections import defaultdict
from typing import Optional, Dict, Any

import redis
from tinydb.storages import Storage


class RedisStorage(Storage):
    """
    Represents a storage implementation for TinyDB using Redis.

    This class extends the `Storage` class from the TinyDB library.

    Example usage:

    >>> redis_uri = "redis://localhost:6379/0"
    >>> db = TinyDB(storage=RedisStorage, redis_uri=redis_uri)

    :param redis_uri: The URI for the Redis connection.
    :type redis_uri: str
    :param kwargs: Additional keyword arguments to pass to the Redis connection.

    .. note::
       The `RedisStorage` class extends `Storage` from TinyDB and inherits its methods.

    :versionadded: 1.0.0

    :warning:
       Ensure that the Redis server is running and accessible. Data may be lost upon Redis server restart.

    :seealso: https://redis-py.readthedocs.io/

    :param connection: The Redis connection object.
    :type connection: redis.client.StrictRedis
    """

    def __init__(self, redis_uri: str, **kwargs):
        """
        Initialize a new Redis storage.

        :param redis_uri: The URI for the Redis connection.
        :type redis_uri: str
        :param kwargs: Additional keyword arguments to pass to the Redis connection.

        .. versionadded:: 1.0.0
           Added the `RedisStorage` class.

        :warning:
           Ensure that the Redis server is running and accessible. Data may be lost upon Redis server restart.

        :seealso: https://redis-py.readthedocs.io/
        """
        self.connection = redis.client.StrictRedis(
            connection_pool=redis.ConnectionPool.from_url(redis_uri), **kwargs
        )

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Read data from Redis storage.

        :return: Dictionary data from Redis storage.
        :rtype: Dict[str, Any]
        """
        tmp = {}
        for key in self.connection.scan_iter("*"):
            tmp[key.decode("utf-8")] = json.loads(self.connection.get(key))

        return tmp

    def write(self, data: Dict[str, Dict[str, Any]]):
        """
        Write all data to Redis storage.

        :param data: Dictionary data to store in Redis.
        :type data: Dict[str, Dict[str, Any]]

        :return: None
        :rtype: None
        """
        for k, v in data.items():
            self.connection.set(k, json.dumps(v))

        return None

    def close(self):
        """
        Close the Redis connection.

        :return: None
        :rtype: None
        """
        self.connection.close()
