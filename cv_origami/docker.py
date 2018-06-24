from __future__ import absolute_import

import docker
import logging

from .constants import DOCKER_UNIX_SOCKET

try:
    docker_client = docker.from_env()
except Exception as e:
    logging.warning('Environment variable are not set propery : {}'.format(e))
    docker_client = docker.DockerClient(base_url=DOCKER_UNIX_SOCKET)
