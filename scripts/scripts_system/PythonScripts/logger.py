"""
@author: ocean.lin
@create on: 2022.09.05
"""

#__all__ = ['logger']

from typing import Union
from datetime import datetime

import logging

TYPE_OF_MESSAGE = Union[str, Exception, datetime]


class Logger(object):
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)

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


logger = Logger()
