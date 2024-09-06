#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/24 22:43:44
# @file        : socket.py
# @description :

import socket
import queue
import threading
from datetime import datetime
from PythonScripts.logger import logger
from Device.device import Device
from Common.system_common import ensure_file_exists

class SocketDevice(Device):
    def __init__(self, name, host, port, log_path = '', rev_max_datalen=1024, timeout=10) -> None:
        super().__init__(name)
        self.host = host
        self.port = port
        self.log_file = log_path
        self.rev_max_datalen = rev_max_datalen
        self.timeout = timeout
        self.connection = None
        self.data_queue = queue.Queue()
        self.tmp_data_queue = queue.Queue()
        self.running = False
        self.read_thread = None
        self.save_data_thread = None

    def connect(self) -> bool:
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.host, self.port))
            logger.print_info(f"Socket {self.name} Connect")
            return True
        except Exception as e:
            logger.print_info(f"Failed to connect to {self.host}:{self.port}. Error: {e}")
            return False

    def disconnect(self) -> bool:
        if self.connection:
            self.connection.close()
            logger.print_info(f"Socket {self.name} disconnect")
        return True

    def write(self, data) -> bool:
        """
        发送数据到设备

        Args:
            data (str): 要发送的数据

        Returns:
            bool: 发送结果
        """
        self.queue_clear(self.tmp_data_queue)
        if self.connection:
            self.connection.sendall(data.encode('utf-8') + b'\n')
            return True
        else:
            logger.print_info("Socket not connect, cant't send.")
            return False

    def read(self, wait_timeout=1) -> bytes:
        """
        读取下发写命令之后的数据

        Args:
            None

        Returns:
            bytes: queue中的一行数据
        """
        try:
            data = self.tmp_data_queue.get(timeout=wait_timeout)
            return data
        except queue.Empty:
            logger.print_warning("Socket device tmp_data_queue is empty.")
            return b''

    def start_read_thread(self):
        """ 启动读取线程 """
        self.queue_clear(self.data_queue)
        self.queue_clear(self.tmp_data_queue)
        self.running = True
        self.read_thread = threading.Thread(target=self.__read_from_device)
        self.read_thread.start()

    def start_save_data_thread(self):
        """ 启动记录log线程 """
        self.save_data_thread = threading.Thread(target=self.__save_data_to_file)
        self.save_data_thread.start()

    def __read_from_device(self):
        """
        从设备读取数据并存放到缓冲区中，数据生产者

        Args:
            None

        Returns:
            None
        """
        logger.print_info("start read uart data.")
        while self.running:
            if self.connection:
                data = self.connection.recv(self.rev_max_datalen)
                if len(data) > 0:
                    self.data_queue.put(data)                    # 使用队列存储，方便存储到文件
                    self.tmp_data_queue.put(data)

    def __save_data_to_file(self):
        """
        将缓冲区数据保存到文件，数据消费者

        Args:
            none

        Returns:
            None
        """
        logger.print_info(f"start save socket data to {self.log_file}.")
        ensure_file_exists(self.log_file)                       # 检查log文件是否存在，不存在则创建
        while self.running:
            try:
                item = self.data_queue.get(timeout=1).decode('utf-8', errors='replace').strip()
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(self.log_file, 'a+') as file:
                    file.write(f"[{formatted_time} {self.case_name}] {item}\n")
                self.data_queue.task_done()                    # 标记任务完成
            except queue.Empty:
                continue