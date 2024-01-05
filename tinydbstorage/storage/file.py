from tinydb.storages import JSONStorage


class FileStorage(JSONStorage):
    """
    Represents a file-based storage implementation using JSON format.

    This class extends the `JSONStorage` class from the TinyDB library.

    :param path: The path to the JSON file.
    :type path: str
    :param create_dirs: Whether to create directories if they don't exist. Default is False.
    :type create_dirs: bool
    :param encoding: The character encoding to use. Default is None.
    :type encoding: str or None
    :param access_mode: The file access mode. Default is "r+".
    :type access_mode: str
    :param kwargs: Additional keyword arguments to pass to the parent class.

    Example usage:

    >>> db = TinyDB(storage=FileStorage, path='data.json', create_dirs=True, encoding='utf-8', access_mode='w')

    .. note::
       The `FileStorage` class extends `JSONStorage` from TinyDB and inherits its methods.

    .. warning::
       Make sure to handle file paths and permissions carefully to avoid data corruption.

    .. versionadded:: 1.0.0
       Added the `FileStorage` class.

    .. versionchanged:: 2.0.0
       Changed the default value of `create_dirs` to False.
    """

    def __init__(
        self, path: str, create_dirs=False, encoding=None, access_mode="r+", **kwargs
    ):
        """
        Initialize a FileStorage instance.

        :param path: The path to the JSON file.
        :type path: str
        :param create_dirs: Whether to create directories if they don't exist. Default is False.
        :type create_dirs: bool
        :param encoding: The character encoding to use. Default is None.
        :type encoding: str or None
        :param access_mode: The file access mode. Default is "r+".
        :type access_mode: str
        :param kwargs: Additional keyword arguments to pass to the parent class.
        """
        super(FileStorage, self).__init__(
            path, create_dirs, encoding, access_mode, **kwargs
        )

    def __repr__(self):
        return f"FileStorage at {id(self)}"
