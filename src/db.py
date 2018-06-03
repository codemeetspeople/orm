import psycopg2
from psycopg2 import extras

__all__ = (
    'get_connection',
)

connection_params = {
    'user': 'blog',
    'dbname': 'blog',
    'password': 'blog'
}

connection = psycopg2.connect(**connection_params)
connection.autocommit = True

cursor = connection.cursor(cursor_factory=extras.RealDictCursor)


def get_connection(_connection=cursor):
    return _connection
