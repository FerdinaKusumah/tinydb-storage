import json
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError
from cachetools import cached, TTLCache
from tinydb.storages import Storage

from tinydbstorage.schema import S3ConfigSchema


class S3Storage(Storage):
    def __init__(self, config: S3ConfigSchema):
        """Initialize new object based on aws config schema
        :param config: object aws config schema
        """
        self.bucket = config.aws_bucket_name
        self.file = config.aws_file_path
        self.client = boto3.resource(
            "s3",
            region_name=config.aws_region_name,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def read(self) -> Dict[str, Any]:
        """Read data from s3 to buffer
        :return: dictionary data
        """
        try:
            cl = self.client.Object(self.bucket, self.file).get()
            obj = cl["Body"].read()
            if isinstance(obj, bytes):
                return json.loads(obj.decode("utf-8"))

            return obj
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return dict()

        return dict()

    def write(self, data: Dict[str, Any]) -> None:
        """Write data to s3 storage file
        :param data: dictionary data
        :return: boolean status
        """
        self.client.Object(self.bucket, self.file).put(Body=json.dumps(data))
        return None
