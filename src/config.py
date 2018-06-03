import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.join(BASE_DIR, 'src')
DB_DIR = os.path.join(PROJECT_ROOT, 'db')
DB_SOURCE_DIR = os.path.join(DB_DIR, 'source')

DATABASE = {
    'user': 'blog',
    'dbname': 'blog',
    'password': 'blog',
    'host': 'localhost'
}

DATABASE_DSN = 'postgresql://{user}:{password}@{host}/{dbname}'.format(
    **DATABASE
)

