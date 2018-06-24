WELCOME_TEXT = """\
\t                           Origami Daemon
\t                    ----------------------------
\t This utility is used to deploy and manage demos on CloudCV servers.
\t To view all the commands available use --help flag

\t                          @CloudCV Origami

\t                    x--------------------------x
"""

ORIGAMI_CONFIG_DIR = '.origami'
ORIGAMI_DEMOS_DIRNAME = 'demos'

DEFAULT_API_SERVER_PORT = 9002

LOGS_DIR = 'logs'
LOGS_FILE_MODE_REQ = 'w+'
DEFAULT_LOG_FILE = 'origami.log'

REQUIREMENTS_FILE = 'requirements.txt'
ENTRYPOINT_PYTHON_MODULE = 'main.py'
DOCKERFILE_FILE = 'Dockerfile'
ORIGAMI_ENV_FILE = '.origami'

BUNDLE_ZIP_MAX_COMPRESSED_SIZE = 500 * 1000 * 1000  # 500 MB
BUNDLE_ZIP_MAX_UNCOMPRESSED_SIZE = 1000 * 1000 * 1000  # 1000 MB
