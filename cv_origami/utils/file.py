import os
import tempfile

from cv_origami.constants import LOGS_DIR, LOGS_FILE_MODE_REQ


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
