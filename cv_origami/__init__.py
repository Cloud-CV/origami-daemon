import logging

from .logger import OrigamiLogger

logger = OrigamiLogger(
    file_log_level=logging.DEBUG,
    console_log_level=logging.DEBUG)
