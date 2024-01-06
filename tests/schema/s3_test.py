import unittest
from tinydbstorage.schema import S3Schema


class TestS3Schema(unittest.TestCase):
    def test_s3schema_creation(self):
        file_path = "test/path"
        bucket_name = "test-bucket"
        region_name = "us-east-1"
        access_key = "your-access-key"
        secret_key = "your-secret-key"

        s3_schema = S3Schema(
            file_path=file_path,
            bucket_name=bucket_name,
            region_name=region_name,
            access_key_id=access_key,
            secret_access_key=secret_key,
        )

        self.assertEqual(s3_schema.file_path, file_path)
        self.assertEqual(s3_schema.bucket_name, bucket_name)
        self.assertEqual(s3_schema.region_name, region_name)
        self.assertEqual(s3_schema.access_key_id, access_key)
        self.assertEqual(s3_schema.secret_access_key, secret_key)

    def test_s3schema_from_param(self):
        file_path = "test/path"
        bucket_name = "test-bucket"
        region_name = "us-east-1"
        access_key = "your-access-key"
        secret_key = "your-secret-key"

        s3_schema = S3Schema.from_param(
            file_path=file_path,
            bucket_name=bucket_name,
            region_name=region_name,
            access_key_id=access_key,
            secret_access_key=secret_key,
        )

        self.assertEqual(s3_schema.file_path, file_path)
        self.assertEqual(s3_schema.bucket_name, bucket_name)
        self.assertEqual(s3_schema.region_name, region_name)
        self.assertEqual(s3_schema.access_key_id, access_key)
        self.assertEqual(s3_schema.secret_access_key, secret_key)


if __name__ == "__main__":
    unittest.main()
