import datetime

import os
from peewee import SqliteDatabase, Model, CharField, DateTimeField, \
    IntegerField, ForeignKeyField, TextField

from .constants import DEMOS_PORT_COUNT_START, DEMOS_PORT_COUNT_END, \
    ORIGAMI_CONFIG_DIR, ORIGAMI_DB_NAME

db_path = os.path.join(os.environ['HOME'], ORIGAMI_CONFIG_DIR, ORIGAMI_DB_NAME)
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
    * image_id: Image on which the container is based.
    * port: Each demo exposes one and only one PORT which should be reported
        here
    * status: Status for the deployement of demo.
        - It can be one of running, stopped, redeploying, deploying, empty,
            error
    * timestamp: Timestamp corresponding to creation of container.
    """
    demo_id = CharField(unique=True, null=False)
    container_id = CharField(unique=True, null=True)
    image_id = CharField(unique=True, null=True)
    port = IntegerField(unique=True, null=True)
    status = CharField(null=False)
    timestamp = DateTimeField(default=datetime.datetime.now)


class Logs(BaseModel):
    """
    Logs relating to any demo which can be retrieved later on

    The Schema includes the following columns

    * demo: Foreign key corresponding to DeployedDemos
    """
    demo = ForeignKeyField(DeployedDemos, backref='logs')
    message = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)


def get_a_free_port():
    """
    Returns a PORT which is free by looking into the database for deployed
    demos.
    """
    demos = DeployedDemos.select(
        DeployedDemos.port).order_by(+DeployedDemos.port)

    port = DEMOS_PORT_COUNT_START
    for demo in demos:
        if port > DEMOS_PORT_COUNT_END:
            return None
        if demo.id != port:
            break
        else:
            port += 1
    return port


def bootstrap_db():
    db.create_tables([DeployedDemos, Logs])
