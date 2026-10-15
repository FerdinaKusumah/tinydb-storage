import json
import threading
from unittest import mock

import fakeredis
import pytest
import redis
from tinydb import Query, TinyDB

from tinydbstorage import StorageConflictError
from tinydbstorage.storage import RedisStorage

SEEDED = {"_default": {"1": {"name": "a"}, "2": {"name": "b"}}}


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


def client(server: fakeredis.FakeServer, **kwargs: object) -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(server=server, **kwargs)


def open_db(server: fakeredis.FakeServer, **kwargs: object) -> TinyDB:
    return TinyDB(storage=RedisStorage, client=client(server), **kwargs)


class TestReadWrite:
    def test_round_trip(self, server: fakeredis.FakeServer) -> None:
        db = open_db(server)
        db.table("users").insert_multiple([{"name": "a"}, {"name": "b"}])
        assert open_db(server).table("users").search(Query().name == "b") == [
            {"name": "b"}
        ]

    def test_missing_key_is_an_empty_database(
        self, server: fakeredis.FakeServer
    ) -> None:
        assert open_db(server).all() == []

    def test_works_with_decoded_responses(self, server: fakeredis.FakeServer) -> None:
        db = TinyDB(storage=RedisStorage, client=client(server, decode_responses=True))
        db.insert({"name": "a"})
        db.insert({"name": "b"})
        assert [d["name"] for d in db.all()] == ["a", "b"]

    def test_drop_tables_on_a_fresh_storage(self, server: fakeredis.FakeServer) -> None:
        client(server).set("tiny_db", json.dumps(SEEDED))
        open_db(server).drop_tables()
        assert json.loads(client(server).get("tiny_db")) == {}


class TestFailedRead:
    def test_a_failed_read_raises_and_keeps_the_data(
        self, server: fakeredis.FakeServer
    ) -> None:
        # 0.1.0 read this as an empty database, so the insert replaced everything.
        client(server).set("tiny_db", json.dumps(SEEDED))
        flaky = client(server)
        real_get = flaky.get
        calls = iter([real_get, mock.Mock(side_effect=redis.ConnectionError("blip"))])
        flaky.get = lambda key: next(calls, real_get)(key)
        db = TinyDB(storage=RedisStorage, client=flaky)
        with pytest.raises(redis.ConnectionError):
            db.insert({"name": "c"})
        assert json.loads(client(server).get("tiny_db")) == SEEDED


class TestKey:
    def test_default_key(self, server: fakeredis.FakeServer) -> None:
        open_db(server).insert({"name": "a"})
        assert client(server).exists("tiny_db")

    def test_custom_key(self, server: fakeredis.FakeServer) -> None:
        open_db(server, key="app").insert({"name": "a"})
        assert client(server).exists("app") and not client(server).exists("tiny_db")

    def test_legacy_prefix_sets_the_key_and_is_not_passed_to_redis(self) -> None:
        storage = RedisStorage(redis_uri="redis://localhost:6379/1", prefix="app")
        assert storage.key == "app"
        assert "prefix" not in storage.connection.connection_pool.connection_kwargs

    def test_needs_a_uri_or_a_client(self) -> None:
        with pytest.raises(ValueError):
            RedisStorage()


class TestConflicts:
    def test_a_write_after_someone_else_wrote_is_refused(
        self, server: fakeredis.FakeServer
    ) -> None:
        first, second = open_db(server), open_db(server)
        first.insert({"name": "a"})
        assert len(second.all()) == 1
        first.insert({"name": "b"})
        with pytest.raises(StorageConflictError):
            second.storage.write({"_default": {"1": {"name": "stale"}}})
        assert [d["name"] for d in open_db(server).all()] == ["a", "b"]

    def test_a_change_during_the_write_is_refused(
        self, server: fakeredis.FakeServer
    ) -> None:
        db = open_db(server)
        db.insert({"name": "a"})
        real_pipeline = db.storage.connection.pipeline

        def racing_pipeline() -> redis.client.Pipeline:
            pipe = real_pipeline()
            real_get = pipe.get

            def get_then_race(key: str) -> object:
                value = real_get(key)
                client(server).set("tiny_db", json.dumps(SEEDED))
                return value

            pipe.get = get_then_race
            return pipe

        db.storage.connection.pipeline = racing_pipeline
        with pytest.raises(StorageConflictError):
            db.insert({"name": "b"})
        assert json.loads(client(server).get("tiny_db")) == SEEDED

    def test_check_conflicts_off_is_last_write_wins(
        self, server: fakeredis.FakeServer
    ) -> None:
        first, second = open_db(server, check_conflicts=False), open_db(
            server, check_conflicts=False
        )
        first.insert({"name": "a"})
        second.all()
        first.insert({"name": "b"})
        second.storage.write({"_default": {"1": {"name": "stale"}}})
        assert [d["name"] for d in open_db(server).all()] == ["stale"]


class TestClose:
    def test_an_injected_client_is_left_open(
        self, server: fakeredis.FakeServer
    ) -> None:
        own = client(server)
        TinyDB(storage=RedisStorage, client=own).close()
        assert own.ping()

    def test_its_own_connection_is_closed(self) -> None:
        storage = RedisStorage(redis_uri="redis://localhost:6379/1")
        with mock.patch.object(storage.connection, "close") as close:
            storage.close()
        close.assert_called_once()

    def test_repr(self) -> None:
        assert (
            repr(RedisStorage(redis_uri="redis://localhost:6379/1", key="app"))
            == "RedisStorage(key='app')"
        )


class TestUnusualStoredValues:
    def test_an_empty_value_is_an_empty_database(
        self, server: fakeredis.FakeServer
    ) -> None:
        client(server).set("tiny_db", "")
        db = open_db(server)
        assert db.all() == []
        db.insert({"name": "a"})
        assert open_db(server).all() == [{"name": "a"}]

    @pytest.mark.parametrize(
        ("stored_value", "error"),
        [
            ("{broken", json.JSONDecodeError),
            (b"\xff\xfe", UnicodeDecodeError),
        ],
    )
    def test_an_unreadable_value_raises_and_is_kept(
        self, server: fakeredis.FakeServer, stored_value: object, error: type
    ) -> None:
        client(server).set("tiny_db", stored_value)
        with pytest.raises(error):
            open_db(server).insert({"name": "a"})
        assert client(server).get("tiny_db") == (
            stored_value if isinstance(stored_value, bytes) else stored_value.encode()
        )

    def test_a_key_of_another_type_raises(self, server: fakeredis.FakeServer) -> None:
        client(server).hset("tiny_db", "field", "value")
        with pytest.raises(redis.ResponseError):
            open_db(server).all()

    def test_unicode_round_trips(self, server: fakeredis.FakeServer) -> None:
        open_db(server).insert({"name": "José 🚀 日本"})
        assert open_db(server).all() == [{"name": "José 🚀 日本"}]

    def test_a_value_json_cannot_hold_fails_before_writing(
        self, server: fakeredis.FakeServer
    ) -> None:
        client(server).set("tiny_db", json.dumps(SEEDED))
        with pytest.raises(TypeError):
            open_db(server).insert({"name": object()})
        assert json.loads(client(server).get("tiny_db")) == SEEDED


class TestOtherWriters:
    def test_a_key_deleted_after_the_read_is_a_conflict(
        self, server: fakeredis.FakeServer
    ) -> None:
        db = open_db(server)
        db.insert({"name": "a"})
        db.all()
        client(server).delete("tiny_db")
        with pytest.raises(StorageConflictError):
            db.storage.write({"_default": {"1": {"name": "stale"}}})
        assert not client(server).exists("tiny_db")

    def test_a_key_created_after_reading_it_missing_is_a_conflict(
        self, server: fakeredis.FakeServer
    ) -> None:
        db = open_db(server)
        assert db.all() == []
        client(server).set("tiny_db", json.dumps(SEEDED))
        with pytest.raises(StorageConflictError):
            db.storage.write({"_default": {"1": {"name": "c"}}})
        assert json.loads(client(server).get("tiny_db")) == SEEDED

    def test_a_cached_document_id_taken_by_another_writer_raises(
        self, server: fakeredis.FakeServer
    ) -> None:
        # TinyDB caches the next ID per table, which is why the README retries with a new TinyDB.
        first, second = open_db(server), open_db(server)
        second.insert({"name": "b1"})
        first.insert({"name": "a1"})
        with pytest.raises(ValueError, match="already exists"):
            second.insert({"name": "b2"})
        assert [d["name"] for d in open_db(server).all()] == ["b1", "a1"]

    def test_concurrent_writers_retrying_as_the_readme_says_lose_nothing(
        self, server: fakeredis.FakeServer
    ) -> None:
        writers, inserts = 4, 25

        def write(writer: int) -> None:
            for n in range(inserts):
                while True:
                    try:
                        open_db(server).insert({"writer": writer, "n": n})
                        break
                    except (StorageConflictError, ValueError):
                        continue

        threads = [threading.Thread(target=write, args=(w,)) for w in range(writers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        stored = {(d["writer"], d["n"]) for d in open_db(server).all()}
        assert stored == {(w, n) for w in range(writers) for n in range(inserts)}
