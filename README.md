# Origami-Daemon

This is a long running daemon process which deals with demo deployment and management on the CloudCV servers.

[Here](https://docs.google.com/document/d/128hrTVGwO9H7In6RJetpMSBTa7NpFg3BZdOUuVQQeIg/edit?usp=sharing) is the complete design documentation for the new demo creation pipeline which this tool deals with.

## Setup for development

```sh
$ git clone git@github.com:Cloud-CV/origami-daemon.git
$ cd origami-daemon
$ virtualenv venv
$ source venv/bin/activate
$ pip install -e .

# Start using cv_origami
$ cv_origami
```
