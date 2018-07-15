Introduction
------------

Origami Daemon is a utility tool to automate the demo deployment process on CloudCV servers(This can also be used by users for
managing the deployment of demos on user provided server).
It can be thought of a long running process on the server which manages the procedure of deploying demos in a containerized
environment on the server by interacting with `dockerd`. It exposes a nice JSON REST API as an interface for interaction. The
API is built on top of `flask` and `tornado` providing utility a robust and flexible interface.

In a normal flow, Origami Server interacts with this process to deploy user demos. But it can be used directly by the user
for managing demos on his own server. Due to its clean and thorough documentation API is quite easy to use.

It internally uses a lite SQLite database to log transactions and demo status, which can be accessed using provided API
routes. One of the major component of the application is the logger module, which logs each and every transaction/step that
occurs in the daemon. The logger uses custom formatter built on top of python logging module and provides support for both
console and file logging.

One major component of origamid is celery tasks. Origamid does not process all the tasks in the normal flow but rather uses
celery workers to carry out the tasks asynchronously. Celery workers process heavy and blocking tasks like demo deployment and
redeployment.

To get started with `origamid` follow the instructions provided in [README](https://github.com/Cloud-CV/origami-daemon)
