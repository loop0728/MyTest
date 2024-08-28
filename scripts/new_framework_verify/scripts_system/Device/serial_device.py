#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/24 21:43:53
# @file        : serial_device.py
# @description :

import time
import threading
import serial
import queue
from datetime import datetime
from PythonScripts.logger import logger
from Common.system_common import ensure_file_exists
from Device.device import Device

class SerialDevice(Device):
    def __init__(self, name, port, log_file = '', baudrate=115200, timeout=1) -> None:
        """
        初始化串口设备
        :param port: 串口名称，如'/dev/ttyUSB0'(Linux)或'COM3'(Windows)
        :param baudrate: 波特率
        :param timeout: 读取超时时间
        """
        super().__init__(name)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.log_file = log_file

        self.connection = None
        self.data_queue = queue.Queue()                # 使用队列存储完整串口数据
        self.tmp_data_queue = queue.Queue()            # 存储case串口数据
        self.read_thread = None
        self.running = False                           # 串口打开标记
        self.save_data_thread = None

    def connect(self) -> bool:
        """
        连接到串口

        Args:
            None

        Returns:
            bool: result
        """
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.connection.is_open:
                logger.print_info(f"Connected to {self.port} baudrate {self.baudrate}")
                self.running = True
                return True
            else:
                logger.print_warning(f"Failed to connect to {self.port}")
        except serial.SerialException as e:
            logger.print_warning(f"Failed to connect to {self.port}: {e}")
            return False

    def disconnect(self) -> bool:
        """
        断开串口连接

        Args:
            None

        Returns:
            bool: result
        """

        self.running = False                     # 停止记录串口消息和保存串口log
        time.sleep(2)
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.print_info(f"Disconnected from {self.port}")
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join()
            if self.save_data_thread and self.save_data_thread.is_alive():
                self.save_data_thread.join()
        return True

    def write(self, data) -> bool:
        """
        发送数据到设备

        Args:
            data (str): 要发送的数据

        Returns:
            bool: 发送结果
        """
        result = False
        curr_line = 0
        self.queue_clear(self.tmp_data_queue)
        if self.connection and self.connection.is_open:
            self.connection.write(data.encode('GBK') + b'\n')
            while curr_line < 10:                  # 等待回显的行数
                curr_data = self.read().decode('GBK')
                if data in curr_data or '?' in curr_data:
                    result = True
                    break
                else:
                    curr_line += 1
                    continue
        else:
            logger.print_warning("Serial port is not open")
        return result

    def read(self, wait_timeout = 2) -> bytes:
        """
        读取下发写命令之后的数据

        Args:
            None

        Returns:
            bytes: queue中的一行数据
        """
        try:
            data = self.tmp_data_queue.get(timeout=wait_timeout-0.5)
            # logger.print_warning(f"serial read: {data}")
            return data
        except queue.Empty:
            logger.print_warning("Serial device tmp_data_queue is empty.")
            return b''

    def start_read_thread(self):
        """ 启动读取线程 """
        self.queue_clear(self.data_queue)
        self.queue_clear(self.tmp_data_queue)
        self.read_thread = threading.Thread(target=self.__read_from_device)
        self.read_thread.start()

    def start_save_data_thread(self):
        """ 启动记录log线程 """
        self.save_data_thread = threading.Thread(target=self.__save_data_to_file)
        self.save_data_thread.start()

    def __read_from_device(self):
        """
        从串口读取数据并存放到缓冲区中，串口数据生产者

        Args:
            None

        Returns:
            None
        """
        logger.print_info("start read uart data.")
        while self.running:
            if self.connection and self.connection.is_open and self.connection.in_waiting > 0:
                # data = self.serial_connection.read(self.serial_connection.in_waiting)
                data = self.connection.readline()
                if len(data) > 0:
                    self.data_queue.put(data)                    # 使用队列存储，方便存储到文件
                    self.tmp_data_queue.put(data)

    def __save_data_to_file(self):
        """
        将缓冲区数据保存到文件，串口数据消费者

        Args:
            none

        Returns:
            None
        """
        logger.print_info(f"start save uart data to {self.log_file}.")
        ensure_file_exists(self.log_file)                       # 检查log文件是否存在，不存在则创建
        while self.running:
            try:
                item = self.data_queue.get(timeout=1).decode('GBK').strip()
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(self.log_file, 'a+') as file:
                    file.write(f"[{formatted_time} {self.case_name}] {item}\n")
                self.data_queue.task_done()                    # 标记任务完成
            except queue.Empty:
                continue