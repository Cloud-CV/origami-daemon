from __future__ import absolute_import, unicode_literals

import logging

from .celery import app


@app.task()
def deploy_demo(demo_id, demo_dir):
    logging.info('Starting task to deploy demo with id : {}'.format(demo_id))
    return
