from invoke import task
from db import get_connection
import config
import os


@task
def migrate(ctx):
    """Migrate database"""

    with open(os.path.join(config.DB_SOURCE_DIR, 'db.sql'), 'r') as f:
        sql = f.read()

    connection = get_connection()
    connection.execute(sql)
