from __future__ import absolute_import

from celery import Celery

app = Celery('cv_origami', broker='amqp://', include=['cv_origami.tasks'])

if __name__ == '__main__':
    app.start()
