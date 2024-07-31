"""
@author: ocean.lin
@create on: 2022.09.05
"""

#__all__ = ['logger']

from typing import Union
from datetime import datetime
import time
import logging
import inspect
from logging.handlers import RotatingFileHandler
TYPE_OF_MESSAGE = Union[str, Exception, datetime]

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logger(object):
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
       # 创建一个handler，用于写入日志文件，并设置回滚模式
        #fh = RotatingFileHandler('test.log', maxBytes=1024*1024, backupCount=5)
        #fh.setLevel(logging.DEBUG)
        #fh.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        #self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)
    
    def print_line_info(self, func):
        def wrapper(*args, **kwargs):
            frame = inspect.currentframe().f_back
            filename = frame.f_code.co_filename
            function_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self.print_info(f"File: {filename}, Function: {function_name}, Line: {line_number}")
            return func(*args, **kwargs)
        return wrapper

    def info(self, message: TYPE_OF_MESSAGE, task_name: str = None):
        """
        info日志
        :param message: 信息
        :param task_name: 任务名称
        """
        if task_name is not None:
            message = '[%s]: %s' % (task_name, message)
        self.logger.info(message)

    def warning(self, message: TYPE_OF_MESSAGE, task_name: str = None):
        """
        warning日志
        :param message: 信息
        :param task_name: 任务名称
        """
        if task_name is not None:
            message = '[%s]: %s' % (task_name, message)
        self.logger.warning(message)

    def error(self, message: TYPE_OF_MESSAGE, task_name: str = None):
        """
        error日志
        :param message: 信息
        :param task_name: 任务名称
        """
        if task_name is not None:
            message = '[%s]: %s' % (task_name, message)
        self.logger.error(message)

    def exception(self, message: TYPE_OF_MESSAGE):
        """
        exception日志
        :param message: 信息
        """
        self.logger.exception(message)

    def print_info(self, message: TYPE_OF_MESSAGE, task_name: str = None):
        if task_name is not None:
            message = '[%s]: %s' % (task_name, message)
        message = time.strftime('[%Y.%m.%d %H:%M:%S] ', time.localtime(time.time())) + message
        print(message)

    def print_warning(self, message: TYPE_OF_MESSAGE, task_name: str = None):
        if task_name is not None:
            message = '[%s]: %s' % (task_name, message)
        message = Colors.WARNING + time.strftime('[%Y.%m.%d %H:%M:%S] ', time.localtime(time.time())) + message + Colors.ENDC
        print(message)

    def print_error(self, message: TYPE_OF_MESSAGE, task_name: str = None):
        if task_name is not None:
            message = '[%s]: %s' % (task_name, message)
        message = Colors.FAIL + time.strftime('[%Y.%m.%d %H:%M:%S] ', time.localtime(time.time())) + message + Colors.ENDC
        print(message)


logger = Logger()
