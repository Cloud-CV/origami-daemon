from __future__ import absolute_import

from celery import Celery

app = Celery('origamid', broker='amqp://', include=['origamid.tasks'])

if __name__ == '__main__':
    app.start()
