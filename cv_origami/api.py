import click
import logging
from flask import Flask, request, jsonify
import six
import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from .constants import DEFAULT_API_SERVER_PORT, WELCOME_TEXT
from .utils.validation import validate_demo_bundle_zip, \
    preprocess_demo_bundle_zip
from .exceptions import InvalidDemoBundleException, OrigamiConfigException

app = Flask(__name__)
server = HTTPServer(WSGIContainer(app))


@app.route('/deploy_trigger/<demo_id>', methods=['POST'])
def trigger_deploy(demo_id):
    """
    This triggers a deploy of a demo on the server, the request should
    be a POST request with `bundle_path` in request body as parameter,
    this path should be local to the server.

    * For now we are considering only local deployments so we are assuming
    that both the origami_daemon and origami_server are running on the same
    server so origami server can give the local path to execute the build.
    """
    try:
        # six.string_types returns a tuple which is fine for isinstance but here
        # the type must be a concrete type.
        bundle_path = request.form.get('bundle_path', type=six.string_types[0])
        logging.info(
            "Triggering deploy for demo_id : {} with bundle_path : {}".format(
                demo_id, bundle_path))

        if bundle_path:
            validate_demo_bundle_zip(bundle_path)
            demo_dir = preprocess_demo_bundle_zip(bundle_path, demo_id)

            # Demo bundle has been verified and preprocessed
            # Create a model and start working on deployment.
            # model = Model(demo_id, demo_dir)

            return jsonify({
                'response':
                'BundleValidated',
                'message':
                'Deploy has been triggred for bundle : {}, checks stats'.format(
                    demo_dir)
            }), 200
        else:
            logging.warn('Bundle Path is not provided in POST parameters')
            return jsonify({
                'response':
                'InvalidRequestParameters',
                'message':
                'Required parameters : bundle_path and demo_id'
            }), 400

    except InvalidDemoBundleException as e:
        logging.warn("Demo bundle is invalid : {}".format(e))
        return jsonify({
            'response': 'InvalidDemoBundle',
            'message': 'The demo bundle provided is not valid',
            'reason': '{}'.format(e)
        }), 400

    except OrigamiConfigException:
        # If thie exception occurs, exit the server since it is not
        # configured properly.
        logging.error("Origami global config are not valid")
        sys.exit(1)


@app.route('/', methods=['GET'])
def welcome_text():
    """
    Returns the welcome text when a GET request is made to
    api root.

    Testing this route

    ..code_block :: bash
        $ curl -X GET 127.0.0.1:9002/

    Returns:
        WELCOME_TEXT (str): Origami description text.
    """
    return WELCOME_TEXT


def configure_flask_logging():
    """
    Configure logging for running python flask server.
    It is handled accordingly the global OrigamiLogger which was
    setup in the __init__.py
    """
    logger = logging.getLogger()
    handlers = logger.handlers

    app.logger.handlers = handlers


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
    configure_flask_logging()
    logging.info('API server started on port : {}'.format(port))
    IOLoop.instance().start()
