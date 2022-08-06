from tinydb.storages import JSONStorage


class FileStorage(JSONStorage):
    def __init__(
        self, path: str, create_dirs=False, encoding=None, access_mode="r+", **kwargs
    ):
        """Inherit only from main json storage
        :param path: string path file
        :param create_dirs: is create new directory
        :param encoding: encoding text file
        :param access_mode: access mode for this storage
        :param kwargs: kwargs
        """
        super(FileStorage, self).__init__(
            path, create_dirs, encoding, access_mode, **kwargs
        )
