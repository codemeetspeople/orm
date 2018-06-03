__all__ = (
    'DatabaseError',
    'NotFoundError'
)


class DatabaseError(Exception):
    pass


class NotFoundError(Exception):
    pass
