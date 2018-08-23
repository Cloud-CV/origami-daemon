import click
import logging
import six
import sys
import os

from flask import Flask, request, jsonify, send_file, safe_join
from flask_cors import CORS
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from .constants import DEFAULT_API_SERVER_PORT, WELCOME_TEXT, \
    ORIGAMI_CONFIG_DIR, ORIGAMI_DB_NAME, ORIGAMI_DEPLOY_LOGS_DIR
from .utils.validation import validate_demo_bundle_zip, \
    preprocess_demo_bundle_zip
from .utils.file import validate_directory_access, get_origami_static_dir
from .exceptions import InvalidDemoBundleException, OrigamiConfigException, \
    OrigamiDockerConnectionError
from .api_response import resp_demo_does_not_exist, resp_invalid_deploy_params,\
    resp_invalid_demo_bundle, resp_demo_deployment_trig, resp_docker_api_error,\
    resp_no_demo_instance_exist
from . import tasks
from .database import Demos

STATIC_DIR = get_origami_static_dir()
if not STATIC_DIR:
    logging.error("ERROR in static directory for origami")
    sys.exit(1)

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app, resources={r"/*": {"origins": "*"}})
server = HTTPServer(WSGIContainer(app))


@app.route('/deploy_trigger/<demo_id>', methods=['POST'])
def trigger_deploy(demo_id):
    """
    This triggers a deploy of a demo on the server, the request should
    be a POST request with `bundle_path` in request body as parameter,
    this path should be local to the server.

    * For now we are considering only local deployments so we are assuming \
    that both the origami_daemon and origami_server are running on the same \
    server so origami server can give the local path to execute the build.

    .. code-block:: bash

        $ curl --include -X POST 127.0.0.1:9002/deploy_trigger/ff90c8 --data \
            "bundle_path=/valid/test.zip"

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: 103
        Server: TornadoServer/5.0.2

        {
          'response': 'BundleValidated',
          'message': 'Deploy has been triggred for bundle : /ff90c8, checks \
            stats'
        }


    .. code-block:: bash

        $ curl --include -X POST 127.0.0.1:9002/deploy_trigger/ff90c8

        HTTP/1.1 400 BAD REQUEST
        Content-Type: application/json
        Content-Length: 97
        Server: TornadoServer/5.0.2

        {
          'response': 'InvalidRequestParameters',
          'message': 'Required parameters : bundle_path and demo_id'
        }

    .. code-block:: bash

        $ curl --include -X POST 127.0.0.1:9002/deploy_trigger/ff90c8 \
            "bundle_path=/invalid/test.zip"

        HTTP/1.1 400 BAD REQUEST
        Content-Type: application/json
        Content-Length: 124
        Server: TornadoServer/5.0.2

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
            logging.info('Handing over the task to celery worker')
            tasks.deploy_demo.delay(demo_id, demo_dir)
            return resp_demo_deployment_trig(demo_dir)

        else:
            logging.warn('Bundle Path is not provided in POST parameters')
            return resp_invalid_deploy_params()

    except InvalidDemoBundleException as e:
        logging.warn("Demo bundle is invalid : {}".format(e))
        return resp_invalid_demo_bundle(e)

    except OrigamiConfigException:
        # If thie exception occurs, exit the server since it is not
        # configured properly.
        logging.error("Origami global config are not valid")
        sys.exit(1)


@app.route('/demo/port/<demo_id>', methods=['GET'])
def demo_port(demo_id):
    """
    Returns the current port of the demo with the provided
    demo_id from the Demos table. It does not check for the status
    of the demo and neither it updates it. It simply returns the port
    from the table.

    .. code-block:: bash

        $ curl --include -X GET 127.0.0.1:9002/demo/port/ffc806

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: 14
        Server: TornadoServer/5.0.2

        {
            "port": 20000
        }
    """
    demo = Demos.get_or_none(Demos.demo_id == demo_id)
    if demo:
        tasks.update_demo_status(demo)
        # Returns the demo status
        return jsonify({'port': demo.port})
    else:
        # No demo with the provided demo ID found, return bad request.
        return resp_demo_does_not_exist(demo_id)


@app.route('/demo/status/<demo_id>', methods=['GET'])
def demo_status(demo_id):
    """
    Returns the current status of the demo with the provided
    demo_id from the Demos table.

    .. code-block:: bash

        $ curl --include -X GET 127.0.0.1:9002/demo/status/ffc806

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: 33
        Server: TornadoServer/5.0.2

        {
            "demo_id": 1,
            "port": 20000,
            "status": "running"
        }


    .. code-block:: bash

        $ curl --include -X GET 127.0.0.1:9002/demo/status/invaild_demo

        HTTP/1.1 400 BAD REQUEST
        Content-Type: application/json
        Content-Length: 93
        Server: TornadoServer/5.0.2

        {
            "message": "Demo ffc80f6 does not exist, try deploying first",
            "response": "DemoDoesNotExist"
        }

    """
    demo = Demos.get_or_none(Demos.demo_id == demo_id)
    if demo:
        # Returns the demo status
        return jsonify({
            'demo_id': demo.id,
            'port': demo.port,
            'status': demo.status
        })
    else:
        # No demo with the provided demo ID found, return bad request.
        return resp_demo_does_not_exist(demo_id)


@app.route('/demo/remove/<demo_id>', methods=['DELETE'])
def remove_demo_instance(demo_id):
    """
    Remove demo docker container instance if it exist. This first checks
    if the provided demo id has a container running, by first looking into
    demo table and then checking containers.

    .. code-block:: bash

        $ curl --include -X DELETE 127.0.0.1:9002/demo/remove/running_demo

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: 85
        Server: TornadoServer/5.0.2

        {
            "message": "Instance for demo(ffc806) removed",
            "response": "RemovedDeployedInstance"
        }


    .. code-block:: bash

        $ curl --include -X DELETE 127.0.0.1:9002/demo/remove/non_running_demo

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: 76
        Server: TornadoServer/5.0.2

        {
            "message": "No demo instance found for ffc806",
            "response": "NoDemoInstance"
        }
    """
    try:
        demo = tasks.remove_demo_instance_if_exist.delay(demo_id)
        if demo:
            # A demo instance was found and was removed.
            return jsonify({
                'response':
                'TriggeredRemoveDeployedInstance',
                'message':
                'Removal of demo instance with id: {} initiated'.format(demo_id)
            }), 200
        else:
            # No docker instance for the demo found.
            return resp_no_demo_instance_exist(demo_id)

    except OrigamiDockerConnectionError as e:
        # Error while communicating using Docker API.
        return resp_docker_api_error(e)


@app.route('/static/logs/<uid>', methods=['GET'])
def get_logs(uid):
    """
    Return log file for the provided log ID
    """
    demo = Demos.get_or_none(Demos.demo_id == uid)
    logs_id = demo.log_id if demo else uid

    logfile = safe_join(
        os.path.join(STATIC_DIR, ORIGAMI_DEPLOY_LOGS_DIR), logs_id)
    if os.path.exists(logfile):
        return send_file(logfile)

    return jsonify({'response': 'InvalidDemoLogsRequested'}), 400


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


# Origami BOOTSETP functions.
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
    """
    Configure database for origamid, it creates a new
    database with the required schema if no database exist in origami
    config directory.
    """
    logging.info('Configuring database')
    db_path = os.path.join(base_dir, ORIGAMI_DB_NAME)
    if not os.path.exists(db_path):
        logging.warn('No database found, creating new.')
        from .database import bootstrap_db
        bootstrap_db()
    logging.info('Database configured')


def run_origami_bootsteps():
    """
    Run bootsteps to configure origamid.
    This includes the following

    * Configure web server logging
    * Configure Database
    * Validating origami configs.
    """
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
