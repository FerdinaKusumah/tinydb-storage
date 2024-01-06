import json
import unittest
from unittest.mock import patch

from tinydb import TinyDB

from tinydbstorage.storage.redis import RedisStorage


class TestRedisStorage(unittest.TestCase):
    def setUp(self):
        # Set up a temporary Redis database for testing
        self.redis_test_uri = "redis://localhost:6379/1"
        self.db = TinyDB(storage=RedisStorage, redis_uri=self.redis_test_uri)

    def tearDown(self):
        # Close the TinyDB instance after each test
        self.db.close()

    @patch("tinydbstorage.storage.redis.redis.client.StrictRedis")
    def test_redisstorage_initialization(self, mock_strict_redis):
        # Mock the StrictRedis connection
        self.db.storage.connection = mock_strict_redis.return_value

        # Check if RedisStorage initializes correctly
        self.assertIsInstance(self.db.storage, RedisStorage)
        self.assertEqual(self.db.storage.connection, mock_strict_redis.return_value)

    @patch("tinydbstorage.storage.redis.redis.client.StrictRedis")
    def test_redisstorage_read_empty(self, mock_strict_redis):
        # Mock the StrictRedis connection
        self.db.storage.connection = mock_strict_redis.return_value

        # Mock the scan_iter and get methods
        mock_strict_redis.return_value.get.return_value = None

        # Read data from an empty Redis storage
        data_read = self.db.storage.read()

        # Check if the read data is an empty dictionary
        self.assertEqual(data_read, {})

    @patch("tinydbstorage.storage.redis.redis.StrictRedis")
    def test_redisstorage_write_and_read(self, mock_strict_redis):
        # Mock the StrictRedis connection
        self.db.storage.connection = mock_strict_redis.return_value

        data_to_write = {"key1": {"value": "A"}, "key2": {"value": "B"}}

        # Mock the scan_iter and get methods
        mock_strict_redis.return_value.get.return_value = json.dumps(data_to_write)

        # Write data to Redis storage
        self.db.storage.write(data_to_write)

        # Read data from Redis storage
        data_read = self.db.storage.read()

        # Check if the read data matches the data written
        self.assertEqual(data_read, data_to_write)

    @patch("tinydbstorage.storage.redis.redis.client.StrictRedis")
    def test_redisstorage_close(self, mock_strict_redis):
        # Mock the StrictRedis connection
        self.db.storage.connection = mock_strict_redis.return_value

        # Close the Redis connection
        self.db.storage.close()

        # Check if the connection is closed
        mock_strict_redis.return_value.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
