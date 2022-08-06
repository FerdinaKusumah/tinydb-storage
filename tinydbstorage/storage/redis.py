import json
from collections import defaultdict
from typing import Dict, Any

import redis
from tinydb.storages import Storage


class RedisStorage(Storage):
    def __init__(self, redis_uri: str, **kwargs):
        """Initialize new object connection from specified uri
        :param redis_uri:
        """
        self.redis_uri = redis_uri
        self.connection = redis.client.StrictRedis(
            connection_pool=redis.ConnectionPool.from_url(redis_uri), **kwargs
        )

    def read(self) -> Dict[str, Any]:
        """Read data from redis storage
        :return: dictionary data
        """
        tmp = defaultdict()
        for key in self.connection.scan_iter("*"):
            tmp[key.decode("utf-8")] = json.loads(self.connection.get(key))
        return tmp

    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Write all data to redis storage
        :param data: dictionary data
        :return: none
        """
        if len(data) == 0:
            self.connection.flushdb()
            return None

        for k, v in data.items():
            self.connection.set(k, json.dumps(v))
        return None

    def close(self):
        """Close redis connection
        :return:
        """
        self.connection.close()
