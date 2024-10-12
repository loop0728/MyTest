"""sysapp logger."""

import logging
import inspect
from colorlog import ColoredFormatter

LOG_LEVEL = logging.DEBUG
# pylint: disable=C0103
formatter = ColoredFormatter(
    "%(log_color)s[%(asctime)s] [%(filename)s] [line:%(lineno)s] [%(levelname)s] %(message)s",
    datefmt='%Y.%m.%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red',
    }
)

logger = logging.getLogger('debug_logger')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(LOG_LEVEL)


class SysappPrint:
    """Other print info."""

    @staticmethod
    def print_line_info(func):
        """Print line info."""

        def wrapper(*args, **kwargs):
            frame = inspect.currentframe().f_back
            filename = frame.f_code.co_filename
            function_name = frame.f_code.co_name
            line_number = frame.f_lineno
            print(
                f"File: {filename}, Function: {function_name}, Line: {line_number}"
            )
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def print_definition_info(func):
        """Print line info of defdefinition."""

        def wrapper(*args, **kwargs):
            filename = inspect.getfile(func)
            line_number = func.__code__.co_firstlineno
            function_name = func.__name__

            print(
                f"Defined in: {filename}, Function: {function_name}, Line: {line_number}"
            )
            return func(*args, **kwargs)

        return wrapper

sysapp_print = SysappPrint()
