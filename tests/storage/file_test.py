import os
import tempfile
import unittest

from tinydb import TinyDB, Query

from tinydbstorage.storage import FileStorage


class TestFileStorage(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

    def tearDown(self):
        # Explicitly close the TinyDB instance before removing the temporary file
        if hasattr(self, "db") and isinstance(self.db, TinyDB):
            self.db.close()

        # Delete the temporary file after testing
        os.remove(self.temp_file.name)

    def test_filestorage_creation(self):
        # Initialize the TinyDB instance correctly
        self.db = TinyDB(path=self.temp_file.name, storage=FileStorage)

        # Add some data
        data = {"key": "value"}
        self.db.insert(data)

        # Check if the data is stored and retrieved correctly
        result = self.db.all()
        self.assertEqual(result, [data])

    def test_filestorage_multiple_inserts(self):
        # Initialize the TinyDB instance correctly
        self.db = TinyDB(path=self.temp_file.name, storage=FileStorage)

        # Add multiple data entries
        data_list = [
            {"id": 1, "value": "A"},
            {"id": 2, "value": "B"},
            {"id": 3, "value": "C"},
        ]
        self.db.insert_multiple(data_list)

        # Check if all data entries are stored and retrieved correctly
        result = self.db.all()
        self.assertEqual(result, data_list)

    def test_filestorage_update(self):
        # Initialize the TinyDB instance correctly
        self.db = TinyDB(path=self.temp_file.name, storage=FileStorage)
        query = Query()
        # Add initial data
        initial_data = {"key": "value"}
        self.db.insert(initial_data)

        # Update the existing data
        updated_data = {"key": "new_value"}
        self.db.update(updated_data, query.key == "value")

        # Check if the data is updated correctly
        result = self.db.all()
        self.assertEqual(result, [updated_data])

    def test_filestorage_remove(self):
        # Initialize the TinyDB instance correctly
        self.db = TinyDB(path=self.temp_file.name, storage=FileStorage)

        # Add some data
        data = {"key": "value"}
        self.db.insert(data)

        # Use the Query class to build the query
        query = Query()

        # Remove the data entry using the query
        self.db.remove(query.key == "value")

        # Check if the data is removed correctly
        result = self.db.all()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
