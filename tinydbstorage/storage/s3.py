import json
from typing import Optional, Dict, Any

import boto3
from botocore.exceptions import ClientError
from tinydb.storages import Storage

from tinydbstorage.schema import S3Schema


class S3Storage(Storage):
    """
    Represents a storage implementation for TinyDB using Amazon S3.

    This class extends the `Storage` class from the TinyDB library.

    Example usage:

    >>> s3_config = S3Schema(
    ...     file_path="your/file/path",
    ...     bucket_name="your-s3-bucket",
    ...     region_name="your-region",
    ...     access_key_id="your-access-key-id",
    ...     secret_access_key="your-secret-access-key",
    ... )
    >>> db = TinyDB(storage=storage, config=s3_config)

    :param config: The S3 configuration schema.
    :type config: S3Schema

    .. note::
       The `S3Storage` class extends `Storage` from TinyDB and inherits its methods.

    :versionadded: 1.0.0

    :warning:
       Ensure that the AWS credentials and S3 bucket information are correctly provided.

    :seealso: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

    :param bucket: The name of the S3 bucket.
    :type bucket: str
    :param file_path: The file path in the S3 bucket.
    :type file_path: str
    :param client: The S3 client from the `boto3` library.
    :type client: boto3.resources.base.ServiceResource
    """

    def __init__(self, config: S3Schema):
        """
        Initialize a new Amazon S3 storage.

        :param config: The S3 configuration schema.
        :type config: S3Schema

        .. versionadded:: 1.0.0
           Added the `S3Storage` class.

        :warning:
           Ensure that the AWS credentials and S3 bucket information are correctly provided.

        :seealso: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
        """
        self.bucket = config.bucket_name
        self.file_path = config.file_path
        self.client = boto3.resource(
            "s3",
            region_name=config.region_name,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
        )

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Read data from Amazon S3 storage.

        :return: Dictionary data from S3 storage.
        :rtype: Optional[Dict[str, Dict[str, Any]]]
        """
        try:
            cl = self.client.Object(self.bucket, self.file_path).get()
            obj = cl["Body"].read()
            if isinstance(obj, bytes):
                return json.loads(obj.decode("utf-8"))

            return obj
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return dict()

        return dict()

    def write(self, data: Dict[str, Any]):
        """
        Write all data to Amazon S3 storage.

        :param data: Dictionary data to store in S3.
        :type data: Dict[str, Any]

        :return: None
        :rtype: None
        """
        self.client.Object(self.bucket, self.file_path).put(Body=json.dumps(data))
