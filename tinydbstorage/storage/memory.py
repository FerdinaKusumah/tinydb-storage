from collections import defaultdict
from typing import Optional, Dict, Any

from tinydb.storages import Storage


class MemoryStorage(Storage):
    """
    Represents an in-memory storage implementation for TinyDB.

    This class extends the `Storage` class from the TinyDB library.

    Example usage:

    >>> db = TinyDB(storage=MemoryStorage)

    :versionadded: 1.0.0

    .. note::
       The `MemoryStorage` class extends `Storage` from TinyDB and inherits its methods.

    .. warning::
       In-memory storage is volatile. All data is lost when the program exits.

    :param internal_memory: The internal memory storage using a defaultdict.
    :type internal_memory: defaultdict
    """

    def __init__(self):
        """
        Initialize a new in-memory storage.

        Example usage:

        >>> storage = MemoryStorage()

        .. versionadded:: 1.0.0
           Added the `MemoryStorage` class.

        :warning:
           In-memory storage is volatile. All data is lost when the program exits.
        """
        super(MemoryStorage, self).__init__()
        self.internal_memory = defaultdict()

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Read data from the in-memory storage.

        :return: Dictionary data from the in-memory storage.
        :rtype: Optional[Dict[str, Dict[str, Any]]]
        """
        return self.internal_memory

    def write(self, data: Dict[str, Dict[str, Any]]):
        """
        Write all data to the in-memory storage.

        :param data: Dictionary data to store in memory.
        :type data: Dict[str, Dict[str, Any]]

        :return: The same dictionary data.
        """
        self.internal_memory = data
