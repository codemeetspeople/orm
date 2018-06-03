from invoke import Collection

from commons.tasks.shell import shell
from db.tasks import ns as db_tasks

ns = Collection()
ns.add_task(shell)
ns.add_collection(db_tasks)
