# tinydb-storage

Tiny db storage extension, this is an unofficial from [tinydb](https://github.com/msiemens/tinydb). I'm creating this
extension based on my case only.


## Installation
```shell
pip install tinydbstorage
```

## Storage extension to use Tinydb

* Memory storage
* File storage
* Redis storage
* S3 storage

## Memory storage example

```python
import requests
from tinydb import TinyDB, Query
from tinydbstorage.storage import MemoryStorage

db = TinyDB(storage=MemoryStorage)

def insert_data():
    resp = requests.get("https://jsonplaceholder.typicode.com/users")
    db.table("users").insert_multiple(resp.json())
```

## File storage example

```python
import os

import requests
from tinydb import TinyDB, Query
from tinydbstorage.storage import FileStorage

db_path = os.path.join(os.path.dirname(__file__), "db.json")
db = TinyDB(path=db_path, storage=FileStorage)

def insert_data():
    resp = requests.get("https://jsonplaceholder.typicode.com/users")
    db.table("users").insert_multiple(resp.json())
```

## Redis storage example

```python
import requests
from tinydb import TinyDB, Query

from tinydbstorage.storage import RedisStorage

db = TinyDB(storage=RedisStorage, redis_uri="redis://:secret@localhost:6379/0")

def insert_data():
    resp = requests.get("https://jsonplaceholder.typicode.com/users")
    db.table("users").insert_multiple(resp.json())
```

## S3 storage example

```python
import requests
from tinydb import TinyDB, Query
from tinydbstorage.schema import S3Schema
from tinydbstorage.storage import S3Storage

config = S3Schema.from_param(
    bucket_name="foo",
    file_path="foo/bar/baz.json",
    region_name="ap-southeast-1",
    access_key_id="bar",
    secret_access_key="secretkey",
)

db = TinyDB(storage=S3Storage, config=config)

def insert_data():
    resp = requests.get("https://jsonplaceholder.typicode.com/users")
    db.table("users").insert_multiple(resp.json())
```

## Help & Bugs

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg)](https://github.com/FerdinaKusumah/tinydb-storage/issues)

If you are still confused or found a bug,
please [open the issue](https://github.com/FerdinaKusumah/tinydb-storage/issues). All bug reports are appreciated, some
features have not been tested yet due to lack of free time.

## License

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**tinydb-storage** released under MIT. See `LICENSE` for more details.
