from .utils.file import get_log_path
from .constants import LOGS_FILE_MODE_REQ, DEFAULT_LOG_FILE

import sys
import logging

# ANSI Color codes
# Don't put these in constants.py let them be here only, I don't think we will
# be needing them anywhere else.
TERMINAL_COLOR_BLUE = '\033[94m'
TERMINAL_COLOR_GREEN = '\033[92m'
TERMINAL_COLOR_YELLOW = '\033[93m'
TERMINAL_COLOR_RED = '\033[91m'
TERMINAL_COLOR_END = '\033[0m'


class OrigamiLogger(object):
    """
    Custom class for setting up logging for CV_Origami.

    Attributes:
        log_level: Root logger log level
        file_log_level: File logger log level
        console_log_level: Console logger log level
    """
    log_level = logging.DEBUG
    file_log_level = logging.INFO
    console_log_level = logging.INFO

    def __init__(self, file_log_level=None, console_log_level=None):
        """
        Creates an instance of Origami logger.

        By default creating an instance of this class enables console logging
        in minimilistic format. To enable file_logging with a custom level send
        the ``file_log_level`` parameter.

        A custom log level for console logger can also be provided using
        ``console_log_level`` parameter.

        .. code-block:: python
            from logger import OrigamiLogger
            import logging

            logger = OrigamiLogger(file_log_level=logging.DEBUG,
                console_log_level=logging.INFO)

            logging.info("Info level log")

            logger.disable_console_logging()
            logging.info("This won't be logged to the console")

            logger.enable_console_logging(level=logging.WARN)
            logging.warn("This will be logged to console as a warning")

        Args:
            file_log_level: Level for file logger.
            console_log_level: Log level for console logger.
        """
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        logger.handlers = []

        if console_log_level:
            self.console_log_level = console_log_level

        # By default only minimal console logging is enabled
        self.enable_console_logging()

        if file_log_level:
            self.file_log_level = file_log_level
            self.enable_file_logging()

    def _get_verbose_console_formatter(self):
        """
        A more verbose console formatter, the format of the message is

        `2018-06-15 11:19:44 | main.py | INFO | root | The actual log message`

        Returns:
            console_formatter (logging.Formatter): A format with a verbose log
                message.
        """
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(filename)s | %(levelname)s |'
            ' %(name)s | %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")

        return console_formatter

    def _get_minimal_console_formatter(self):
        """
        Retuns a minimal console formatter, the format of the message is

        ` [+] Here is an info log
          [!] Here is a warning log
          [-] This is an error log `

        Returns:
            console_formatter (logging.Formatter): A format with a minimal log
                message.
        """
        console_formatter = CustomConsoleFormatter()

        return console_formatter

    def _get_file_formatter(self):
        """
        Returns a file formatter to work with for logging purposes, file logs
        are verbose and includes most of the details. For example

        ```
        INFO | root | 2018-06-15 11:22:02 | main.py | 17 | This is an info log
        WARNING | root | 2018-06-15 11:22:02 | main.py | 18 | This is a warning log
        ERROR | root | 2018-06-15 11:22:02 | main.py | 19 | This is an error log
        DEBUG | root | 2018-06-15 11:22:02 | main.py | 20 | This is an error log
        ```

        Returns:
            file_formatter (logging.Formatter): The file fomatter.
        """
        file_formatter = logging.Formatter(
            fmt='%(levelname)s | %(name)s | '
            '%(asctime)s | %(filename)s | %(lineno)d | '
            '%(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")

        return file_formatter

    def enable_console_logging(self, verbose=False, level=None):
        """
        This enable console logging.

        Console logging by defalut uses minimalistic console formatter so as
        not to bloat the console. If a more verbose console log is needed send
        the ``verbose`` parameter as ``True``

        For this to work properly with custom formatter ``CustomConsoleFormatter``
        like in the case of verbose=False file_handlers should be before
        console_handlerssince FileHandler inherits from StreamHandler which
        conflicts the log message format in FileLogger.

        Args:
            verbose (bool): Set verbosity for console formatting
            level (logging.Level): Max log level for the logger.
        """
        logger = logging.getLogger()
        if not level:
            level = self.console_log_level

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = self._get_minimal_console_formatter()
        if verbose:
            formatter = self._get_verbose_console_formatter()
        console_handler.setFormatter(formatter)

        logger_handlers = []
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                logger_handlers.append(handler)

        logger_handlers.append(console_handler)

        logger.handlers = logger_handlers

    def disable_console_logging(self):
        """
        Removes all the non FileHandlers from logger handlers, since
        for this implementation we are mainly concerned with file and
        console loggers this necesserily removes all ConsoleHandlers disabling
        any console logging.
        """
        logger = logging.getLogger()
        for handler in logging.handlers:
            # We cannot check for logging.StreamHandler here as FileHandler
            # inherits StreamHandler so all handlers will be removed.
            if not isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)

    def enable_file_logging(self, level=None):
        """
        File logging are quite verbose by default, if you want to change the
        format of the log change the formatter in ``_get_file_formatter()``

        Args:
            level (logging.Level): Max log level for the logger.
        """
        logger = logging.getLogger()
        if not level:
            level = self.file_log_level

        file_handler = logging.FileHandler(
            get_log_path(DEFAULT_LOG_FILE), mode=LOGS_FILE_MODE_REQ)
        file_handler.setLevel(level)
        file_handler.setFormatter(self._get_file_formatter())

        logger_handlers = [file_handler]
        for handler in logger.handlers:
            if not isinstance(handler, logging.FileHandler):
                logger_handlers.append(handler)

        logger.handlers = logger_handlers

    def disable_file_logging(self):
        """
        Removes all the non FileHandlers from our logger handlers
        """
        logger = logging.getLogger()
        for handler in logging.handlers:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)


class CustomConsoleFormatter(logging.Formatter):
    """
    Custom formatter to show logging messages differently on Console

    Attributes:
        error_fmt: Error format string for log
        warn_fmt: Warn format string for log
        debug_fmt: Debug format string for log
        info_fmt: Info format string for log
    """
    error_fmt = TERMINAL_COLOR_RED + '[-] {}' + TERMINAL_COLOR_END
    warn_fmt = TERMINAL_COLOR_YELLOW + '[!] {}' + TERMINAL_COLOR_END
    debug_fmt = TERMINAL_COLOR_GREEN + '[*] {}' + TERMINAL_COLOR_END
    info_fmt = TERMINAL_COLOR_BLUE + '[+] {}' + TERMINAL_COLOR_END

    def format(self, record):
        """ Choose format according to record level
        It overrides the method from logging.Formatter which formats the log
        message

        Args:
            record (dict): Record to format

        Returns:
            result (str): Formatted string according to log level.
        """

        # Replace the original message with one customized by logging level
        if record.levelno == logging.DEBUG:
            record.msg = self.debug_fmt.format(record.msg)
        elif record.levelno == logging.INFO:
            record.msg = self.info_fmt.format(record.msg)
        elif record.levelno == logging.ERROR:
            record.msg = self.error_fmt.format(record.msg)
        elif record.levelno == logging.WARN:
            record.msg = self.warn_fmt.format(record.msg)

        # Call the original formatter class to do the grunt work
        result = super(CustomConsoleFormatter, self).format(record)

        return result
