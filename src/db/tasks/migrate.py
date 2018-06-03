from invoke import task
from db import get_cursor
import config
import os


@task
def migrate(ctx):
    """Migrate database"""

    with open(os.path.join(config.DB_SOURCE_DIR, 'db.sql'), 'r') as f:
        sql = f.read()

    with get_cursor() as cursor:
        cursor.execute(sql)
