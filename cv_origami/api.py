import click
import logging
import six
import sys
import os

from flask import Flask, request, jsonify
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from .constants import DEFAULT_API_SERVER_PORT, WELCOME_TEXT, \
    ORIGAMI_CONFIG_DIR, ORIGAMI_DB_NAME
from .utils.validation import validate_demo_bundle_zip, \
    preprocess_demo_bundle_zip
from .utils.file import validate_directory_access
from .exceptions import InvalidDemoBundleException, OrigamiConfigException
from . import tasks

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

    curl -X POST 127.0.0.1:9002/deploy_trigger/ff90c8 --data "bundle_path=
        /tmp/test.zip"

    Possible responses:

    200 OK
    {
      'response': 'BundleValidated',
      'message': 'Deploy has been triggred for bundle : /ff90c8, checks stats'
    }

    400 BAD_REQUEST
    {
      'response': 'InvalidRequestParameters',
      'message': 'Required parameters : bundle_path and demo_id'
    }

    400 BAD_REQUEST
    {
      'response': 'InvalidDemoBundle',
      'message': 'The demo bundle provided is not valid',
      'reason': 'requirements.txt was not valid'
    }

    Args:
        demo_id: Id of the demo to be deployed
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
            # Start a worker process to deploy the demo, this must be
            # asynchronous.
            tasks.deploy_demo.delay(demo_id, demo_dir)

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
    logging.info('Setting up logger for the flask server')
    logger = logging.getLogger()
    handlers = logger.handlers

    app.logger.handlers = handlers


def configure_origami_db(base_dir):
    db_path = os.path.join(base_dir, ORIGAMI_DB_NAME)
    if not os.path.exists(db_path):
        logging.warn('No database found, creating new.')
        from .database import bootstrap_db
        bootstrap_db()


def run_origami_bootsteps():
    logging.info('Running origami bootsteps')
    origami_config_dir = os.path.join(os.environ['HOME'], ORIGAMI_CONFIG_DIR)
    if not os.path.isdir(origami_config_dir):
        logging.info('Config directory does not exist, creating...')
        os.makedirs(origami_config_dir, mode=0o755, exist_ok=True)

    if not validate_directory_access(origami_config_dir, 'w+'):
        logging.error(
            'Permissions are not valid for {}'.format(origami_config_dir))
        sys.exit(1)

    configure_flask_logging()
    configure_origami_db(origami_config_dir)
    logging.info('Bootsteps completed...')


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
    run_origami_bootsteps()
    logging.info('API server started on port : {}'.format(port))
    IOLoop.instance().start()
