#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/02 11:39:35
# @file        : telnet.py
# @description :

import telnetlib
import queue
import threading
from datetime import datetime
from PythonScripts.logger import logger
from Common.system_common import ensure_file_exists
from Device.device import Device

class BoundedQueue(queue.Queue):
    def __init__(self, maxsize) -> None:
        super().__init__(maxsize)
        self._maxsize = maxsize

    def put(self, item, block=True, timeout=None):
        if self.full():
            super().get()              # 重写队列的类，在队列满的情况下丢掉一个旧的数据
        super().put(item, block, timeout)

class TelnetDevice(Device):
    def __init__(self, name, host, port, log_path = '', timeout=10) -> None:
        """
        初始化Telnet客户端
        :param host: Telnet服务器的主机名或IP地址
        :param port: Telnet服务器的端口号
        :param timeout: 连接超时时间（秒）
        """
        super().__init__(name)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.log_file = log_path
        self.connection = None
        self.data_queue = queue.Queue()
        self.tmp_data_queue = queue.Queue()
        self.running = False
        self.read_thread = None
        self.save_data_thread = None
        self.username = 'root'
        self.password = ''

    def connect(self) -> bool:
        """
        连接到Telnet服务器

        Args:
            None

        Returns:
            bool: result
        """
        try:
            # logger.print_info(f"telnet connect:{self.host}:{self.port}")
            self.connection = telnetlib.Telnet(self.host, self.port, self.timeout)
            try:
                # 输入登录用户名
                self.connection.read_until(b'login:', self.timeout)
                self.connection.write(self.username.encode('utf-8') + b"\n")
                # 输入登录密码
                self.connection.read_until(b'Password:', self.timeout)
                self.connection.write(self.password.encode('utf-8') + b"\n")
            except Exception as e:
                logger.print_info("Telnet no need login.")
            logger.print_info(f"Telnet connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.print_error(f"Telnet failed to connect to {self.host}:{self.port}. Error: {e}")
            return False

    def disconnect(self) -> bool:
        """
        关闭Telnet连接

        Args:
            None

        Returns:
            bool: result
        """
        self.running = False
        self.queue_clear(self.data_queue)
        self.queue_clear(self.tmp_data_queue)
        if self.connection:
            self.connection.close()
            logger.print_info(f"Connection to {self.host}:{self.port} closed.")
        return True

    def write(self, data) -> bool:
        """
        发送数据到设备

        Args:
            data (str): 要发送的数据，字节类型

        Returns:
            bool: 发送结果
        """
        result = False
        curr_line = 0
        self.queue_clear(self.tmp_data_queue)
        if self.connection:
            self.connection.write(data.encode('utf-8') + b'\n')
            while curr_line < 10:                  # 等待回显的行数
                curr_data = self.read().decode('utf-8', errors='replace')
                if data in curr_data:
                    result = True
                    break
                else:
                    curr_line += 1
                    continue
        else:
            logger.print_warning("Not connected!")
        return result

    def read(self, wait_timeout = 2) -> bytes:
        """
        读取队列中的数据

        Args:
            wait_timeout (int): 读取数据超时时间

        Returns:
            bytes: queue中的一行数据
        """
        # logger.print_warning("Telnet read.")
        try:
            data = self.tmp_data_queue.get(timeout=wait_timeout-0.5)
            return data
        except queue.Empty:
            logger.print_warning("Telnet tmp_data_queue is empty.")
            return ''

    def start_read_thread(self):
        """ 启动读取线程 """
        self.queue_clear(self.data_queue)
        self.queue_clear(self.tmp_data_queue)
        self.running = True
        self.read_thread = threading.Thread(target=self.__read_from_telnet)
        self.read_thread.start()

    def start_save_data_thread(self):
        """ 启动记录log线程 """
        self.save_data_thread = threading.Thread(target=self.__save_data_to_file)
        self.save_data_thread.start()

    def __read_from_telnet(self, timeout = 0.5):
        """
        从telnet读取数据并存放到缓冲区中

        Args:
            None

        Returns:
            None
        """
        while self.running:
            if self.connection:
                try:
                    data  = self.connection.read_until(b'\n', timeout)
                    if len(data) > 0:
                        self.data_queue.put(data)                    # 存储到队列
                        self.tmp_data_queue.put(data)
                except EOFError:
                    break
                except Exception as e:
                    break

    def __save_data_to_file(self):
        """
        将缓冲区数据保存到文件

        Args:
            None

        Returns:
            None
        """
        ensure_file_exists(self.log_file)                       # 检查log文件是否存在，不存在则创建
        while self.running:
            try:
                item = self.data_queue.get(timeout=1).decode('utf-8', errors='replace').strip()
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(self.log_file, 'a+') as file:
                    file.write(f"[{formatted_time} {self.case_name}] {item}\n")
                self.data_queue.task_done()                  # 标记任务完成
            except queue.Empty:
                continue
