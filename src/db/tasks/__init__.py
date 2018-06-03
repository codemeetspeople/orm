from invoke import Collection
from db.tasks.shell import shell
from db.tasks.create import create
from db.tasks.migrate import migrate

ns = Collection('db', shell)
ns.add_task(create)
ns.add_task(migrate)
