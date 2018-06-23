# For python2 and stuff
from __future__ import absolute_import, unicode_literals

import logging
import os
from docker.errors import NotFound, APIError, BuildError

from .celery import app
from .constants import ORIGAMI_CONFIG_DIR, ORIGAMI_DEMOS_DIRNAME, \
    ORIGAMI_WRAPPED_DEMO_PORT
from .database import DeployedDemos, get_a_free_port
from .docker import docker_client


@app.task()
def deploy_demo(demo_id, demo_dir):
    """
    Checks for the existence of demo container and redploy it if it exist

    Args:
        demo_id: Demo ID for the demo to be deployed(this is a unique ID from
            origami database)
        demo_dir: Absolute path to the demo directory where it was unzipped.
    """
    logging.info('Starting task to deploy demo with id : {}'.format(demo_id))
    # Before doing anything get the previously created image if any.
    demo = DeployedDemos.get_or_none(DeployedDemos.demo_id == demo_id)
    if demo:
        # An existing instance for the demo was found, change the state to
        # redeploying
        demo.status = 'redeploying'
        demo.save()

        if demo.container_id and not demo.status == 'empty':
            # If there exist a demo which is not empty then it should be
            # redeployed by first deleting the already running instance.
            logging.info('Demo is already deployed, trying for redployment.')
            try:
                container = docker_client.get(demo.container_id)
                logging.info('Demo {} is in {} state'.format(
                    demo_id, container.status))

                container.stop(timeout=5)
                container.remove()
            except NotFound:
                logging.info('No container instance found for demo')
            except APIError as e:
                logging.error(
                    'Error while communicating to to docker API: {}'.format(e))
                demo.status = 'error'
                demo.save()
                return

    else:
        demo = DeployedDemos(demo_id=demo_id, status='deploying')

    # Get the dockerfile from the demo dir from ORIGAMI_CONFIG_HOME
    dockerfile_dir = os.path.join(os.environ['HOME'], ORIGAMI_CONFIG_DIR,
                                  ORIGAMI_DEMOS_DIRNAME, demo_id)
    try:
        image = docker_client.images.build(path=dockerfile_dir)[0]
        demo.image_id = image.id

        # Run a new container instance for the demo.
        if not demo.port:
            port = get_a_free_port()
            demo.port = port

        port_map = '{}/tcp'.format(ORIGAMI_WRAPPED_DEMO_PORT)
        cont = docker_client.containers.run(
            image.id, detach=True, name=demo_id, ports={port_map: demo.port})

        demo.container_id = cont.id
        demo.status = 'running'

    except BuildError as e:
        logging.error('Error while building image for {} : {}'.format(
            demo_id, e))
        demo.status = 'error'
    except APIError as e:
        logging.error(
            'Error while communicating to to docker API: {}'.format(e))
        demo.status = 'error'

    demo.save()
