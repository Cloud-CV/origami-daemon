# Origami-Daemon

This is a long running daemon process which deals with demo deployment and management on the CloudCV servers.

[Here](https://docs.google.com/document/d/128hrTVGwO9H7In6RJetpMSBTa7NpFg3BZdOUuVQQeIg/edit?usp=sharing) is the complete design documentation for the new demo creation pipeline which this tool deals with.

## Getting started

Build and run the Docker image using the following commands:

```sh
$ docker-compose up
```

## Setup for development

To get started with the development follow the following steps.

```sh
$ git clone git@github.com:Cloud-CV/origami-daemon.git
$ cd origami-daemon
$ virtualenv venv
$ source venv/bin/activate
$ pip install -e .

# Start using origamid
$ origamid

# Run celery workers
# Make sure that rabbitmq-server is running
$ celery -A origamid worker -l info

# Run server
$ origamid run_server
```

### Testing

This project uses tox for testing purposes. To set up testing environment install test-requirements.txt

`pip install -r dev-requirements.txt`

### Documentation

Documentation for the project can be found in [docs](/docs)

* The project uses sphinx for building documentation coupled with read the docs theme.

#### Run tests

`tox`

## Wiki

* New Demo Creation pipeline ([Wiki link](https://github.com/Cloud-CV/origami-daemon/wiki))
