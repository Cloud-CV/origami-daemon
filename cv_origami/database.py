import datetime

from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegerField
from .utils.file import get_origami_database_path

db_path = get_origami_database_path()
db = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = db


class DeployedDemos(BaseModel):
    """
    This table holds the information about the details regarding
    the demos deployed on the server. Each demo which has been deployed
    must have an entry in this table.

    The table has the following fields

    * demo_id: Demo unique ID provided by origami_server
    * container_id: container ID corresponding to demo deployed
    * docker_image: Image on which the container is based.
    * port: Each demo exposes one and only one PORT which should be reported here
    * timestamp: Timestamp corresponding to creation of container.
    """
    demo_id = CharField(unique=True)
    container_id = CharField(unique=True)
    docker_image = CharField(unique=True)
    port = IntegerField(unique=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
