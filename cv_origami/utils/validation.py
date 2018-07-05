try:
    from pip.req import parse_requirements
except ImportError:
    # For pip version >= 10
    from pip._internal.req import parse_requirements

import os
import zipfile

from .file import get_model_bundles_base_dir, extract_zip_to_dir, \
    clean_directory
from ..exceptions import InvalidDemoBundleException, OrigamiConfigException
from ..constants import REQUIREMENTS_FILE, ENTRYPOINT_PYTHON_MODULE, \
    DOCKERFILE_FILE, ORIGAMI_ENV_FILE, DEMO_SETUP_FILE


def validate_requirements_file(file_path):
    """
    Validate a python requirments.txt

    It uses pip parse_requirements function to check whether
    the requirements file in context is valid or not for parsing.

    Args:
        file_path (str): Absolute path to requirements file.

    Raises:
        InvalidDemoBundleException: Requirements file is not valid.
    """
    try:
        reqs = parse_requirements(file_path, session=False)
        requirements = []
        for r in reqs:
            requirements.append(r.req)
        if not requirements:
            raise InvalidDemoBundleException("Requirements file is empty.")
    except Exception:
        raise InvalidDemoBundleException("Requirements file is not valid")


def validate_dockerfile(file_path):
    """
    This is too expensive it is equivilant to creating an Image from the
    dockerfile there is no option to lexically validate Dockerfile in docker-py
    if they add such a feature implement this.

    There is no API endpoint for this as of v1.37 docker engine
    """
    pass


def validate_origami_env_file(file_path):
    """
    Validates the origmai environment file provided with the bundle.

    The environment variables must be separated by new lines with the
    followin format.

    .. code-block:: python
        ENV_VAR_1=variable1
        ENV_VAR_2=variable2

    Args:
        file_path (str): Absolute file path for the environment file.

    Raises:
        InvalidDemoBundleException: Raised if the environement file is invalid
    """
    with open(file_path, 'r') as file:
        contents = file.read()
        lines = filter(lambda line: (line != ''),
                       [line.strip() for line in contents.split('\n')])
        if not all(len(x.split('=')) == 2 for x in lines):
            raise InvalidDemoBundleException("origami env file is invalid")


def check_setup_file(file_path):
    """
    Check for the setup.sh file in the bundled zip, if the file does not exist
    it creates a dummy script and add ``exit 0;`` to it so that it gracefully
    executes.

    If the file exist in the bundle then change the permisssions of the script
    to make it executable.
    """
    if not os.path.exists(file_path):
        open(file_path, 'w').write('exit 0;')
    os.chmod(file_path, 0o755)


def preprocess_demo_bundle_zip(bundle_path, demo_id):
    """
    This function preprocesses the demo bundle zip. It takes the path to
    zip and demo_id of the demo and validates the required files for
    the demo.

    Args:
        bundle_path (str): Path to demo bundle zip
        demo_id (str): Unique demo ID for the given demo.

    Returns:
        demo_dir (str): Path to the extracted demo directory on the disk.

    Raises:
        OrigamiConfigException: An error while setting up origami daemon.
    """
    base_dir = get_model_bundles_base_dir()
    if not base_dir:
        raise OrigamiConfigException(
            "Config directory does not have valid permissions")

    demo_dir = os.path.join(base_dir, demo_id)
    clean_directory(demo_dir)
    extract_zip_to_dir(bundle_path, demo_dir)

    # Validate the required files for the demo bundle
    # main.py Dockerfile requirements.txt .origami
    validate_requirements_file(os.path.join(demo_dir, REQUIREMENTS_FILE))
    validate_dockerfile(os.path.join(demo_dir, DOCKERFILE_FILE))
    validate_origami_env_file(os.path.join(demo_dir, ORIGAMI_ENV_FILE))
    check_setup_file(os.path.join(demo_dir, DEMO_SETUP_FILE))

    return demo_dir


def validate_demo_bundle_zip(bundle_path):
    """
    Checks if the bundle path provided is a valid path or not.
    Also check the permissions so that we must have atleast read permission
    for the demo bundle.

    The function checks if all the requried files exists in the bundled ZIP.
    The required files are

    * .origami -> Origami environment file
    * Dockerfile -> Dockerfile to build the demo container.
    * main.py -> Main entrypoint to your python code bundled with origami_lib
    * requirements.txt -> Requirements file for your python demo.

    Args:
        bundle_path: Path to bundled zip for the demo.

    Exceptions:
        InvalidDemoBundleException: The demo bundle is not valid.
    """
    if os.path.isabs(bundle_path) and zipfile.is_zipfile(
            bundle_path) and os.access(bundle_path, os.R_OK):

        z = zipfile.ZipFile(bundle_path).namelist()
        files = [os.path.basename(k) for k in z]
        req_files = [
            ORIGAMI_ENV_FILE, DOCKERFILE_FILE, ENTRYPOINT_PYTHON_MODULE,
            REQUIREMENTS_FILE
        ]
        # Check if all the required files are present.
        if not all(x in files for x in req_files):
            raise InvalidDemoBundleException(
                'Make sure the bundle has {}'.format(', '.join(req_files)))

    else:
        raise InvalidDemoBundleException("Demo bundle path is not valid")
