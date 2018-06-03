import psycopg2
from psycopg2 import extras
import config

__all__ = (
    'get_connection',
)

connection = psycopg2.connect(**config.DATABASE)
connection.autocommit = True

cursor = connection.cursor(cursor_factory=extras.RealDictCursor)


def get_connection(_connection=cursor):
    return _connection
