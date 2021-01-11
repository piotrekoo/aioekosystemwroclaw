"""Define exception types."""


class EkosystemWroclawError(Exception):
    """Base Ekosystem Wrocław exception."""

    pass


class RequestError(EkosystemWroclawError):
    """An exception caused by an HTTP request error."""

    pass


class DataError(EkosystemWroclawError):
    """An exception caused by invalid data."""

    pass
