import unittest

from tinydb import TinyDB, Query

from tinydbstorage.storage import MemoryStorage


class TestMemoryStorage(unittest.TestCase):
    def setUp(self):
        # Initialize TinyDB with MemoryStorage
        self.db = TinyDB(storage=MemoryStorage)

    def tearDown(self):
        # Close the TinyDB instance after each test
        self.db.close()

    def test_memorystorage_initialization(self):
        # Check if MemoryStorage initializes correctly
        self.assertIsInstance(self.db.storage, MemoryStorage)
        self.assertEqual(self.db.storage.internal_memory, {})

    def test_memorystorage_add_single_data(self):
        # Add single data entry to the in-memory storage
        data_to_add = {"key1": {"value": "A"}}
        self.db.insert(data_to_add)

        # Read data from the in-memory storage
        data_read = self.db.storage.read()

        # Check if the data read matches the data added
        self.assertEqual(data_read["_default"], {"1": {"key1": {"value": "A"}}})

    def test_memorystorage_add_multiple_data(self):
        # Add multiple data entries to the in-memory storage
        data_to_add = [{"key1": {"value": "A"}}, {"key2": {"value": "B"}}]
        self.db.insert_multiple(data_to_add)

        # Read data from the in-memory storage
        data_read = self.db.storage.read()

        # Check if the data read matches the data added
        self.assertEqual(
            data_read["_default"],
            {"1": {"key1": {"value": "A"}}, "2": {"key2": {"value": "B"}}},
        )

    def test_memorystorage_update_data(self):
        # Add initial data to the in-memory storage
        self.db.insert({"count": 7, "type": "apple"})

        # Update data in the in-memory storage
        updated_data = {"count": 2, "type": "apple"}
        self.db.update(updated_data)

        # Read the updated data from the in-memory storage
        data_read = self.db.storage.read()

        # Check if the data read reflects the updates
        self.assertEqual(data_read["_default"], {"1": {"count": 2, "type": "apple"}})

    def test_memorystorage_remove_data(self):
        # Add data to the in-memory storage
        self.db.insert_multiple(
            [{"count": 7, "type": "apple"}, {"count": 3, "type": "peach"}]
        )

        # Remove data from the in-memory storage
        self.db.remove(Query().type == "apple")

        # Read the remaining data from the in-memory storage
        data_read = self.db.storage.read()

        # Check if the data read reflects the removal
        self.assertEqual(data_read["_default"], {"2": {"count": 3, "type": "peach"}})

    def test_memorystorage_query_data(self):
        # Add data to the in-memory storage
        self.db.insert({"count": 7, "type": "apple"})
        self.db.insert({"count": 3, "type": "peach"})

        # Query data from the in-memory storage
        q = Query()
        queried_data = self.db.search(q.type == "apple")

        # Check if the queried data is correct
        self.assertEqual(queried_data, [{"count": 7, "type": "apple"}])


if __name__ == "__main__":
    unittest.main()
