from contextlib import contextmanager

from psycopg2 import extras
from psycopg2 import pool

import config

__all__ = (
    'get_cursor',
)

MIN = 1
MAX = 10

db_pool = pool.SimpleConnectionPool(MIN, MAX, **config.DATABASE)


@contextmanager
def get_cursor(_pool=db_pool):
    connection = db_pool.getconn()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
    try:
        yield cursor
        connection.commit()
    finally:
        db_pool.putconn(connection)
