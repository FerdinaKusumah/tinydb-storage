class StorageConflictError(RuntimeError):
    """The stored database changed after this storage read it, so writing would overwrite another writer."""
