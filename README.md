# tinydb-storage

[![CI](https://github.com/FerdinaKusumah/tinydb-storage/actions/workflows/ci.yml/badge.svg)](https://github.com/FerdinaKusumah/tinydb-storage/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tinydbstorage.svg)](https://pypi.org/project/tinydbstorage/)
[![Python](https://img.shields.io/pypi/pyversions/tinydbstorage.svg)](https://pypi.org/project/tinydbstorage/)

> **Note:** this is an independent project. It is not an official TinyDB package and is not affiliated with or endorsed
> by the TinyDB project or its maintainers.

Storage extensions for [TinyDB](https://github.com/msiemens/tinydb). Keep a TinyDB database in **Redis** or **S3**
(including S3-compatible services such as MinIO and Cloudflare R2) instead of a local file.

Both storages keep the whole database as one JSON value, like TinyDB's own `JSONStorage`, and they never silently lose
data:

* A failed read raises the error. It is never mistaken for an empty database, so the next write can't replace your data.
* A write fails with `StorageConflictError` when another process changed the database after this one read it, instead of
  overwriting that change. Redis uses `WATCH`, S3 uses conditional writes (`If-Match` / `If-None-Match`).

## Installation

Install the extra for the storage you use:

```shell
pip install "tinydbstorage[redis]"   # RedisStorage
pip install "tinydbstorage[s3]"      # S3Storage
pip install "tinydbstorage[all]"     # both
```

Requires Python 3.10+ and TinyDB 4.8+.

## Redis storage example

```python
from tinydb import TinyDB, Query
from tinydbstorage.storage import RedisStorage

db = TinyDB(storage=RedisStorage, redis_uri="redis://:secret@localhost:6379/0")
db.table("users").insert({"name": "John"})
db.table("users").search(Query().name == "John")
```

Options:

* `key`: the Redis key holding the database. Default `tiny_db`.
* `client`: an existing `redis.Redis` client instead of `redis_uri`. It is left open when the database closes.
* Any other keyword argument goes to `redis.Redis.from_url`, for example `socket_timeout=5`.

## S3 storage example

```python
from tinydb import TinyDB
from tinydbstorage import S3Schema
from tinydbstorage.storage import S3Storage

config = S3Schema(bucket_name="foo", file_path="foo/bar/baz.json", region_name="ap-southeast-1")
db = TinyDB(storage=S3Storage, config=config)
db.table("users").insert({"name": "John"})
```

Credentials are optional. Left out, boto3 uses its default chain: environment variables, `~/.aws` config, or the
instance/task role. To pass them explicitly:

```python
config = S3Schema.from_param(
    bucket_name="foo",
    file_path="foo/bar/baz.json",
    region_name="ap-southeast-1",
    access_key_id="bar",
    secret_access_key="secretkey",
)
```

For MinIO, Cloudflare R2 and other S3-compatible services, set `endpoint_url`:

```python
config = S3Schema(bucket_name="foo", file_path="db.json", endpoint_url="http://localhost:9000")
```

You can also pass your own boto3 S3 client with `client=`.

## Concurrent writers

Two processes can share one database. If one writes after the other read, the second write raises
`StorageConflictError` and nothing is overwritten. Retry the operation, which reads the latest data first.

An insert needs one more step. TinyDB remembers the next document ID per table, so when another process inserted
first, the insert can also fail with `ValueError: Document with ID ... already exists`. Nothing is written in that
case either. Retry inserts with a new `TinyDB`, which reads the IDs again:

```python
import redis
from tinydb import TinyDB
from tinydbstorage import StorageConflictError
from tinydbstorage.storage import RedisStorage

client = redis.Redis.from_url("redis://localhost:6379/0")

for attempt in range(5):
    try:
        TinyDB(storage=RedisStorage, client=client).insert({"name": "John"})
        break
    except (StorageConflictError, ValueError):
        if attempt == 4:
            raise
```

Updates and removes don't use the ID counter, so retrying them on the same `db` is enough.

If your service doesn't support conditional writes, or you want the old last-write-wins behaviour, pass
`check_conflicts=False` to the storage.

## Joining tables across storages

[tinydbjoin](https://github.com/FerdinaKusumah/tinydb-join) joins TinyDB tables in memory, wherever each one is stored,
for example customers in Redis and orders in a local JSON file:

```python
from tinydb import TinyDB
from tinydbjoin import Join
from tinydbstorage.storage import RedisStorage

customers = TinyDB(storage=RedisStorage, redis_uri="redis://localhost:6379/0").table("customers")
orders = TinyDB("orders.json").table("orders")

Join.inner(orders, customers, on=("customer_id", "id"))  # [(order, customer), ...]
```

## Development

```shell
make install   # poetry install --all-extras
make test      # pytest with coverage
make format    # black
```

The tests run against in-process fakes (fakeredis and moto), so no Redis server or AWS account is needed.

## Help & Bugs

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg)](https://github.com/FerdinaKusumah/tinydb-storage/issues)

If you are still confused or found a bug,
please [open the issue](https://github.com/FerdinaKusumah/tinydb-storage/issues). All bug reports are appreciated.

## License

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**tinydb-storage** released under MIT. See `LICENSE` for more details.
