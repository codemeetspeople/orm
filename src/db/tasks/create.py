from invoke import task
from db.utils import SQLGenerator


@task
def create(ctx):
    """Create db.sql and models"""

    generator = SQLGenerator()
    generator.generate()
