from dataclasses import dataclass
from typing import Optional

from tinydbstorage.constants import DEFAULT_S3_REGION


@dataclass(frozen=True)
class S3Schema:
    """Where an S3Storage keeps its database, and how to reach it.

    Credentials are optional: left out, boto3 uses its default chain
    (environment, shared config, instance or task role). Set `endpoint_url`
    for S3-compatible services such as MinIO or Cloudflare R2.
    """

    file_path: str
    bucket_name: str
    region_name: str = DEFAULT_S3_REGION
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    endpoint_url: Optional[str] = None

    @classmethod
    def from_param(
        cls,
        file_path: str,
        bucket_name: str,
        region_name: str = DEFAULT_S3_REGION,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        session_token: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ) -> "S3Schema":
        return cls(
            file_path=file_path,
            bucket_name=bucket_name,
            region_name=region_name,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            endpoint_url=endpoint_url,
        )

    def client_kwargs(self) -> dict[str, str]:
        kwargs = {
            "region_name": self.region_name,
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "aws_session_token": self.session_token,
            "endpoint_url": self.endpoint_url,
        }
        return {name: value for name, value in kwargs.items() if value is not None}
