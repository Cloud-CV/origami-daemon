FROM python:3

RUN mkdir /origami-daemon
WORKDIR /origami-daemon

ADD . /origami-daemon

RUN pip install -e .

CMD [ "origamid" ]

CMD [ "celery", "-A", "origamid", "worker", "-l", "info" ]

CMD [ "origamid", "run_server" ]

EXPOSE 9002
