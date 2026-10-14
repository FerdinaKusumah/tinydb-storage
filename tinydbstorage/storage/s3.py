import json
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError
from tinydb.storages import Storage

from tinydbstorage.constants import (
    JSON_CONTENT_TYPE,
    S3_CONFLICT_CODES,
    S3_MISSING_OBJECT_CODES,
)
from tinydbstorage.errors import StorageConflictError
from tinydbstorage.schema.s3 import S3Schema

JsonData = dict[str, dict[str, Any]]
_UNREAD = object()


class S3Storage(Storage):
    """TinyDB storage that keeps the whole database as one JSON object in S3.

    A missing object reads as an empty database; any other error is raised.
    Writes are conditional on the ETag last read (If-Match, or If-None-Match
    for a new object), so a write fails with StorageConflictError instead of
    overwriting another writer. `check_conflicts=False` disables that, for
    S3-compatible services without conditional writes.

    >>> db = TinyDB(storage=S3Storage, config=S3Schema(bucket_name="foo", file_path="db.json"))
    """

    def __init__(
        self, config: S3Schema, client: Any = None, check_conflicts: bool = True
    ) -> None:
        self.bucket = config.bucket_name
        self.file_path = config.file_path
        self.client = (
            client
            if client is not None
            else boto3.client("s3", **config.client_kwargs())
        )
        self.check_conflicts = check_conflicts
        self._etag: Any = _UNREAD

    def read(self) -> Optional[JsonData]:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self.file_path)
        except ClientError as e:
            if self._code(e) not in S3_MISSING_OBJECT_CODES:
                raise
            self._etag = None
            return None
        self._etag = obj["ETag"]
        return json.loads(obj["Body"].read())

    def write(self, data: JsonData) -> None:
        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Key=self.file_path,
                Body=json.dumps(data).encode(),
                ContentType=JSON_CONTENT_TYPE,
                **self._precondition(),
            )
        except ClientError as e:
            if self.check_conflicts and self._code(e) in S3_CONFLICT_CODES:
                raise StorageConflictError(
                    f"s3://{self.bucket}/{self.file_path} changed since it was read"
                ) from e
            raise
        self._etag = response["ETag"]

    def _precondition(self) -> dict[str, str]:
        if not self.check_conflicts or self._etag is _UNREAD:
            return {}
        return {"IfMatch": self._etag} if self._etag else {"IfNoneMatch": "*"}

    @staticmethod
    def _code(error: ClientError) -> str:
        return str(error.response.get("Error", {}).get("Code", ""))

    def __repr__(self) -> str:
        return f"S3Storage(s3://{self.bucket}/{self.file_path})"
