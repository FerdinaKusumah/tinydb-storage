from collections import defaultdict
from typing import Optional, Dict, Any

from tinydb.storages import Storage


class MemoryStorage(Storage):
    def __init__(self):
        """Initialize new storage"""
        super(MemoryStorage, self).__init__()
        self.internal_memory = defaultdict()

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """Read data from memory storage
        :return: dictionary data from memory storage
        """
        return self.internal_memory

    def write(self, data: Dict[str, Dict[str, Any]]):
        """Write all data to memory storage
        :param data: dictionary data storage
        :return: dictionary data
        """
        self.internal_memory = data
