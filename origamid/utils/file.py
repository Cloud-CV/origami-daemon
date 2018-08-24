import os
import shutil
import tempfile
import zipfile
import logging


from ..constants import LOGS_DIR, LOGS_FILE_MODE_REQ, ORIGAMI_CONFIG_DIR, \
    ORIGAMI_DEMOS_DIRNAME, ORIGAMI_STATIC_DIR, ORIGAMI_DEPLOY_LOGS_DIR
from ..exceptions import OrigamiConfigException


def validate_directory_access(path, mode):
    """
    Check if a directory can be accessed in the specified mode by the current
    user.

    Args:
        path (str): Path to check the access rights of.
        mode (str): access mode we want to validate for the path

    Returns:
        (bool): True or False based on the availability of the access rights to
            the user for the provided path.
    """
    try:
        tempfile.NamedTemporaryFile(mode=mode, dir=path, delete=True)
    except (IOError, OSError):
        return False
    return True


def get_log_path(log_file):
    """
    Returns the log file path from the log file name provided as an argument.
    If the log file directory does not have permission for user it returns none

    Args:
        log_file (str): Name of the log file.

    Returns:
        log_file_path (str, None): Complete path of the log file
    """
    logs_dir = os.path.abspath(LOGS_DIR)
    if validate_directory_access(os.path.dirname(logs_dir), LOGS_FILE_MODE_REQ):
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)
        log_file_path = os.path.join(logs_dir, log_file)
        return log_file_path
    else:
        return None


def extract_zip_to_dir(zip_path, extract_path):
    """
    Extracts a ZIP file to the desired location, make sure that before any call
    to this function the paths zip_path and extract_path must be verified.

    Args:
        zip_path: absolute path of the zip file
        extract_path: absolute path to where the zip is to be extracted.
    """
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(extract_path)
    zip_ref.close()


def get_model_bundles_base_dir():
    """
    Returns the gloabal directory absolute path where the demo bundles
    are present. This is simply $HOME/.origami/demos

    If the function returns None it implies that directory permissions are
    not valid.
    """
    try:
        dirpath = os.path.join(os.environ['HOME'], ORIGAMI_CONFIG_DIR,
                               ORIGAMI_DEMOS_DIRNAME)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath, mode=0o755, exist_ok=True)
        if validate_directory_access(dirpath, 'w+'):
            return dirpath
    except OSError as e:
        logging.error(
            'OSError while validating demo bundles directory : {}'.format(e))
    return None


def get_origami_static_dir():
    """
    Returns the absolute path to the static directory served by origami-daemon.
    Which simply resolves to for now `$HOME/.origami/static/`
    """
    try:
        dirpath = os.path.join(os.environ['HOME'], ORIGAMI_CONFIG_DIR,
                               ORIGAMI_STATIC_DIR)
        logs_dir = os.path.join(dirpath, ORIGAMI_DEPLOY_LOGS_DIR)
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir, mode=0o755, exist_ok=True)
        if validate_directory_access(dirpath, 'w+'):
            return dirpath
    except OSError as e:
        logging.error(
            'OSError while validating api static directory : {}'.format(e))
    return None


def clean_directory(directory):
    """
    Clean the provided directory, does nothing if the directory path
    is not a valid directory.

    shutil as of version 3.3 also have rmtree.avoids_symlink_attacks
    which avoids any sort of symlink attacks.

    Raises:
        OrigmaiConfigException: The only reason why rmtree might fail is
            when permission are not set properly so raise this.
    """

    def panic_invaild_bootstrap():
        raise OrigamiConfigException(
            "Invalid bootstrapping for daemon, cannot clean directory")

    if os.path.isdir(directory):
        shutil.rmtree(
            directory, ignore_errors=False, onerror=panic_invaild_bootstrap)
