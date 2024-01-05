import unittest
from unittest.mock import MagicMock, patch
import json
from tinydb import TinyDB
from tinydbstorage.storage import S3Storage
from tinydbstorage.schema import S3Schema
from botocore.exceptions import ClientError


class TestS3Storage(unittest.TestCase):
    @patch("tinydbstorage.storage.s3.boto3.resource")
    def setUp(self, mock_boto_resource):
        # Mock the S3 client
        self.mock_s3_client = mock_boto_resource.return_value

        # Create an instance of S3Schema with the required fields
        self.s3_config = S3Schema(
            bucket_name="mocked-bucket",
            file_path="mocked-file-path",
            region_name="mocked-region",
            access_key_id="mocked-access-key-id",
            secret_access_key="mocked-secret-access-key",
        )

        # Create an instance of S3Storage and set the mock S3 client
        self.s3_storage = S3Storage
        self.s3_storage.client = self.mock_s3_client

        # Properly configure the TinyDB instance with S3Storage
        self.db = TinyDB(storage=self.s3_storage, config=self.s3_config)

    def test_read_from_empty_s3_storage(self):
        # Mock the S3 client's 'get' method for an empty storage
        mock_s3_get = self.mock_s3_client.Object.return_value.get
        mock_s3_get.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "operation_name"
        )

        # Call the read method for an empty storage
        data_read = self.db.storage.read()

        # Check if the read data is an empty dictionary
        self.assertEqual(data_read, {})

    def test_read_from_s3_storage(self):
        # Mock the S3 client's 'get' method
        mock_s3_get = self.mock_s3_client.Object.return_value.get
        mock_s3_get.return_value = {"Body": MagicMock()}
        mock_s3_get.return_value["Body"].read.return_value = json.dumps(
            {"key1": {"value": "A"}, "key2": {"value": "B"}}
        ).encode("utf-8")

        # Call the read method on the storage instance (not on TinyDB)
        data_read = self.db.storage.read()

        # Check if the read data matches the expected data
        expected_data = {"key1": {"value": "A"}, "key2": {"value": "B"}}
        self.assertEqual(data_read, expected_data)

    def test_write_to_s3_storage(self):
        # Call the write method on the storage instance (not on TinyDB)
        data_to_write = {"key1": {"value": "A"}, "key2": {"value": "B"}}
        self.db.storage.write(data_to_write)

        # Check if the put method was called with the correct data
        self.mock_s3_client.Object.assert_called_once_with(
            self.s3_config.bucket_name, self.s3_config.file_path
        )
        self.mock_s3_client.Object.return_value.put.assert_called_once_with(
            Body=json.dumps(data_to_write)
        )


if __name__ == "__main__":
    unittest.main()
