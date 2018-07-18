class FileExtensionException(ValueError):
    """File extension / format not supported."""
    pass


class DatabaseHeaderException(ValueError):
    """Excel database is found, but the header is bad."""
    pass


class NoDataError(ValueError):
    """No data is specified to be manipulated."""
    pass


class BadArgumentsException(KeyError):
    """The must be given args or kwargs is not supplied."""
    pass
