import dataclasses

import pytest

from tinydbstorage import S3Schema


class TestS3Schema:
    def test_from_param_keeps_the_0_1_signature(self) -> None:
        schema = S3Schema.from_param(
            file_path="a/b.json",
            bucket_name="bucket",
            region_name="us-east-1",
            access_key_id="key",
            secret_access_key="secret",
        )
        assert schema == S3Schema(
            file_path="a/b.json",
            bucket_name="bucket",
            region_name="us-east-1",
            access_key_id="key",
            secret_access_key="secret",
        )

    def test_credentials_are_optional(self) -> None:
        assert S3Schema(file_path="a.json", bucket_name="bucket").client_kwargs() == {
            "region_name": "ap-southeast-1"
        }

    def test_client_kwargs_carry_every_set_field(self) -> None:
        schema = S3Schema.from_param(
            file_path="a.json",
            bucket_name="bucket",
            access_key_id="key",
            secret_access_key="secret",
            session_token="token",
            endpoint_url="https://r2.example",
        )
        assert schema.client_kwargs() == {
            "region_name": "ap-southeast-1",
            "aws_access_key_id": "key",
            "aws_secret_access_key": "secret",
            "aws_session_token": "token",
            "endpoint_url": "https://r2.example",
        }

    def test_is_immutable(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            S3Schema(file_path="a.json", bucket_name="bucket").bucket_name = "other"  # type: ignore[misc]
