#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/02 14:43:52
# @file        : device.py
# @description :

from abc import ABC, abstractmethod
from enum import Enum

class BootStage(Enum):
    E_BOOTSTAGE_UBOOT   = 1
    E_BOOTSTAGE_KERNEL  = 2
    E_BOOTSTAGE_UNKNOWN = 3

class Device(ABC):
    def __init__(self, name) -> None:
        """
        初始化设备
        :param name: device name
        """
        self.name = name
        self.case_name = ''
        self.uboot_prompt  = 'SigmaStar #'
        self.kernel_prompt = '/ #'
        self.bootstage = BootStage.E_BOOTSTAGE_UNKNOWN

    @abstractmethod
    def connect(self) -> bool:
        """
        连接设备, 这是一个抽象方法，子类必须实现它
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        关闭连接, 这是一个抽象方法，子类必须实现它
        """
        pass

    @abstractmethod
    def write(self, data) -> bool:
        """
        发送数据到设备, 这是一个抽象方法，子类必须实现它

        Args:
            data (str): 要发送的数据

        Returns:
            bool: result
        """
        pass

    @abstractmethod
    def read(self) -> bytes:
        """
        从缓冲区中读取一行数据并返回, 这是一个抽象方法，子类必须实现它

        Args:
            None

        Returns:
            bool: result
        """
        pass

    def start_read_thread(self) -> None:
        """ 启动读取线程 """
        pass

    def start_save_data_thread(self) -> None:
        """ 启动记录log线程 """
        pass

    def queue_clear(self, queue):
        """
        清空缓冲区

        Args:
            queue (queue): queue name

        Returns:
            NA
        """
        while not queue.empty():
            queue.get_nowait()

    def set_case_name(self, case_name):
        """
        设置case name

        Args:
            case_name (str): case name

        Returns:
            NA
        """
        self.case_name = case_name

    def get_case_name(self):
        """
        获取case name

        Args:
            NA

        Returns:
            str: case name
        """
        return self.case_name

    def get_bootstage(self):
        status = ''
        if self.bootstage == BootStage.E_BOOTSTAGE_UBOOT:
            status = 'at uboot'
        elif self.bootstage == BootStage.E_BOOTSTAGE_KERNEL:
            status = 'at kernel'
        else:
            status = 'Unknow'
        return status

    def clear_bootstage(self):
        self.bootstage = BootStage.E_BOOTSTAGE_UNKNOWN
