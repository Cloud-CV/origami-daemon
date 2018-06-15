import click
import logging
from flask import Flask
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from .constants import DEFAULT_API_SERVER_PORT, WELCOME_TEXT

app = Flask(__name__)
server = HTTPServer(WSGIContainer(app))


@app.route('/', methods=['GET'])
def welcome_text():
    """
    Returns the welcome text when a GET request is made to
    api root.

    Returns:
        WELCOME_TEXT (str): Origami description text.
    """
    return WELCOME_TEXT


@click.command()
@click.option('--port', default=DEFAULT_API_SERVER_PORT)
def run_server(port):
    """Starts the API server for the daemon.

    It starts an API server to provide an interface to interact with the
    application. The commands takes an argument `--port` to specify the
    port to start the API server to listen.

    Args:
        port (int): Port for API server to listen on
    """
    server.listen(port)
    logging.info('API server started on port : {}'.format(port))
    IOLoop.instance().start()
