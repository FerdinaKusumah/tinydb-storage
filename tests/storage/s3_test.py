import json
from collections.abc import Iterator
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from tinydb import Query, TinyDB

from tinydbstorage import S3Schema, StorageConflictError
from tinydbstorage.storage import S3Storage

BUCKET = "tinydb-bucket"
KEY = "db/data.json"
SEEDED = {"_default": {"1": {"name": "a"}, "2": {"name": "b"}}}


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    with mock_aws():
        client = boto3.client("s3", region_name="ap-southeast-1")
        client.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-1"},
        )
        yield client


def config(**kwargs: Any) -> S3Schema:
    return S3Schema(
        bucket_name=kwargs.pop("bucket_name", BUCKET), file_path=KEY, **kwargs
    )


def open_db(**kwargs: Any) -> TinyDB:
    return TinyDB(storage=S3Storage, config=config(), **kwargs)


def stored(s3: Any) -> dict[str, Any]:
    return json.loads(s3.get_object(Bucket=BUCKET, Key=KEY)["Body"].read())


class TestReadWrite:
    def test_round_trip(self, s3: Any) -> None:
        open_db().table("users").insert_multiple([{"name": "a"}, {"name": "b"}])
        assert open_db().table("users").search(Query().name == "a") == [{"name": "a"}]
        assert (
            s3.head_object(Bucket=BUCKET, Key=KEY)["ContentType"] == "application/json"
        )

    def test_missing_object_is_an_empty_database(self, s3: Any) -> None:
        assert open_db().all() == []

    def test_other_read_errors_are_raised_and_nothing_is_written(self, s3: Any) -> None:
        # 0.1.0 read any error as an empty database, so the insert replaced everything.
        s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(SEEDED))

        class ReadDenied:
            def get_object(self, **_: Any) -> None:
                raise ClientError({"Error": {"Code": "AccessDenied"}}, "GetObject")

            def put_object(self, **kwargs: Any) -> Any:
                return s3.put_object(**kwargs)

        db = TinyDB(storage=S3Storage, config=config(), client=ReadDenied())
        with pytest.raises(ClientError) as error:
            db.insert({"name": "c"})
        assert error.value.response["Error"]["Code"] == "AccessDenied"
        assert stored(s3) == SEEDED

    def test_other_write_errors_are_raised(self, s3: Any) -> None:
        storage = S3Storage(config(bucket_name="no-such-bucket"), check_conflicts=False)
        with pytest.raises(ClientError):
            storage.write({})

    def test_repr(self, s3: Any) -> None:
        assert repr(S3Storage(config())) == f"S3Storage(s3://{BUCKET}/{KEY})"


class TestConflicts:
    def test_a_write_after_someone_else_wrote_is_refused(self, s3: Any) -> None:
        first, second = open_db(), open_db()
        first.insert({"name": "a"})
        assert len(second.all()) == 1
        first.insert({"name": "b"})
        with pytest.raises(StorageConflictError):
            second.storage.write({"_default": {"1": {"name": "stale"}}})
        assert [d["name"] for d in open_db().all()] == ["a", "b"]

    def test_creating_an_object_someone_else_just_created_is_refused(
        self, s3: Any
    ) -> None:
        db = open_db()
        assert db.all() == []
        s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(SEEDED))
        with pytest.raises(StorageConflictError):
            db.storage.write({"_default": {"1": {"name": "c"}}})
        assert stored(s3) == SEEDED

    def test_check_conflicts_off_is_last_write_wins(self, s3: Any) -> None:
        first, second = open_db(check_conflicts=False), open_db(check_conflicts=False)
        first.insert({"name": "a"})
        second.all()
        first.insert({"name": "b"})
        second.storage.write({"_default": {"1": {"name": "stale"}}})
        assert [d["name"] for d in open_db().all()] == ["stale"]

    def test_drop_tables_on_a_fresh_storage(self, s3: Any) -> None:
        s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(SEEDED))
        open_db().drop_tables()
        assert stored(s3) == {}


class TestClient:
    def test_an_injected_client_is_used(self, s3: Any) -> None:
        S3Storage(config(), client=s3).write({"_default": {}})
        assert stored(s3) == {"_default": {}}

    def test_the_client_is_built_from_the_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        monkeypatch.setattr(boto3, "client", lambda *a, **kw: calls.append((a, kw)))
        S3Storage(
            config(
                endpoint_url="http://minio:9000",
                access_key_id="k",
                secret_access_key="s",
            )
        )
        assert calls == [
            (
                ("s3",),
                {
                    "region_name": "ap-southeast-1",
                    "aws_access_key_id": "k",
                    "aws_secret_access_key": "s",
                    "endpoint_url": "http://minio:9000",
                },
            )
        ]

    def test_an_error_without_a_code_is_raised(self) -> None:
        class Broken:
            def get_object(self, **_: Any) -> None:
                raise ClientError({}, "GetObject")

        with pytest.raises(ClientError):
            S3Storage(config(), client=Broken()).read()


class TestUnusualStoredObjects:
    def test_an_empty_object_is_an_empty_database(self, s3: Any) -> None:
        s3.put_object(Bucket=BUCKET, Key=KEY, Body=b"")
        db = open_db()
        assert db.all() == []
        db.insert({"name": "a"})
        assert stored(s3) == {"_default": {"1": {"name": "a"}}}

    def test_an_unreadable_object_raises_and_is_kept(self, s3: Any) -> None:
        s3.put_object(Bucket=BUCKET, Key=KEY, Body=b"{broken")
        with pytest.raises(json.JSONDecodeError):
            open_db().insert({"name": "a"})
        assert s3.get_object(Bucket=BUCKET, Key=KEY)["Body"].read() == b"{broken"

    def test_unicode_round_trips(self, s3: Any) -> None:
        open_db().insert({"name": "José 🚀 日本"})
        assert open_db().all() == [{"name": "José 🚀 日本"}]

    def test_a_missing_bucket_raises(self, s3: Any) -> None:
        with pytest.raises(ClientError) as error:
            TinyDB(storage=S3Storage, config=config(bucket_name="no-such-bucket")).all()
        assert error.value.response["Error"]["Code"] == "NoSuchBucket"

    def test_an_object_deleted_after_the_read_is_a_conflict(self, s3: Any) -> None:
        db = open_db()
        db.insert({"name": "a"})
        db.all()
        s3.delete_object(Bucket=BUCKET, Key=KEY)
        with pytest.raises(StorageConflictError):
            db.storage.write({"_default": {"1": {"name": "stale"}}})
        with pytest.raises(ClientError):
            s3.head_object(Bucket=BUCKET, Key=KEY)
