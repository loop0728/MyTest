#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/24 21:43:53
# @file        : serial_device.py
# @description :

import os
import time
import threading
import serial
import queue
from enum import Enum
from PythonScripts.logger import logger

def ensure_folder_and_file(path_to_file):
    """
    检查文件是否存在，不存在则创建
    :param path_to_file: 文件路径
    """
    directory = os.path.dirname(path_to_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"mkdir {directory}")
    if not os.path.exists(path_to_file):
        with open(path_to_file, 'w') as f:
            pass
        print(f"Create file {path_to_file}")
    else:
        print(f"{path_to_file} existed.")

class BootStage(Enum):
    E_BOOTSTAGE_UBOOT   = 1
    E_BOOTSTAGE_KERNEL  = 2
    E_BOOTSTAGE_BOOTING = 3

class SerialDevice:
    def __init__(self, port, log_file = '', baudrate=115200, timeout=1):
        """
        初始化串口设备
        :param port: 串口名称，如'/dev/ttyUSB0'(Linux)或'COM3'(Windows)
        :param baudrate: 波特率
        :param timeout: 读取超时时间
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.data_queue = queue.Queue()           # 使用队列存储完整串口数据，最后写入文件
        self.data_buffer = []                     # 使用列表存储case串口数据，用于命令解析
        self.data_buffer_threshold = 4096         # 超过threshold个数的元素就清空case log buffer（需要保证完整保存一条指令的返回数据，且在解析返回数据期间不会因case log size达到上限被清空）
        self.data_buffer_lock = threading.Lock()  # 用于同步访问data_buffer的锁
        self.data_buffer_rindex = 0               # data_buffer中当前读取的数据行的索引
        self.log_file = log_file
        self.log_prefix = ''
        self.recv_log_thread = None               # 接收串口日志线程
        self.save_log_thread = None               # 保存串口日志线程
        self.running = True                       # 串口打开标记
        self.uboot_prompt = 'SigmaStar #'
        self.kernel_prompt = '/ #'
        self.bootstage = BootStage.E_BOOTSTAGE_BOOTING

    def connect(self):
        """
        连接到串口
        """
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.serial_connection.is_open:
                logger.print_info(f"Connected to {self.port}")
                # 启动读取线程
                self.recv_log_thread = threading.Thread(target=self._read_from_port)
                self.recv_log_thread.daemon = True
                self.recv_log_thread.start()
                # 启动记录log线程
                self.save_log_thread = threading.Thread(target=self._save_data_to_file)
                self.save_log_thread.daemon = True
                self.save_log_thread.start()
        except serial.SerialException as e:
            logger.print_warning(f"Failed to connect to {self.port}: {e}")

    def disconnect(self):
        """
        断开串口连接

        Args:
            NA

        Returns:
            NA
        """

        self.running = False                     # 停止记录串口消息和保存串口log
        time.sleep(2)
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.print_info(f"Disconnected from {self.port}")
        if self.recv_log_thread and self.recv_log_thread.is_alive():
            self.recv_log_thread.join()
        if self.save_log_thread and self.save_log_thread.is_alive():
            self.save_log_thread.join()
            

    def send_data(self, data):
        """
        发送数据到串口

        Args:
            data: 要发送的数据，字节类型

        Returns:
            result: 发送结果,bool类型
        """
        data = data + b'\n'
        if self.serial_connection and self.serial_connection.is_open:
            with self.data_buffer_lock:
                if len(self.data_buffer) > 0:
                    self.data_buffer.clear()         # 清空列表
                self.data_buffer_rindex = 0
            self.serial_connection.write(data)
            return True
        else:
            logger.print_warning("Serial port is not open")
            return False

    def read_line(self, wait_timeout = 5000):
        """
        获取串口一行中的数据
        :return: 缓冲区中的数据列表
        """
        ret = False
        data = ''
        try_time = 0

        if self.serial_connection and self.serial_connection.is_open:
            while try_time < wait_timeout:
                with self.data_buffer_lock:
                    if len(self.data_buffer) > self.data_buffer_rindex:
                        data = self.data_buffer[self.data_buffer_rindex]
                        print(f'read line: {data}')
                        ret = True
                        self.data_buffer_rindex += 1
                        break
                    else:
                        time.sleep(0.001)
                        try_time += 1
                        continue
        else:
            logger.print_warning("Serial port is not open")
            ret = False
        
        if try_time == wait_timeout:
            logger.print_warning("data_buffer read_line time out")
            ret = False
        return ret, data

    def _read_from_port(self):
        """
        从串口读取数据并存放到缓冲区中，串口数据生产者

        Args:
            NA

        Returns:
            NA
        """
        while self.running:
            if self.serial_connection and self.serial_connection.is_open and self.serial_connection.in_waiting:
                data = self.serial_connection.readline()
                if data:
                    self.data_queue.put(data)                    # 使用队列存储，方便存储到文件


    def _save_data_to_file(self):
        """
        将缓冲区数据保存到文件，串口数据消费者

        Args:
            case_name: 添加case_name到log

        Returns:
            NA
        """
        # 检查log文件是否存在，不存在则创建
        ensure_folder_and_file(self.log_file)
        while self.running:
            with open(self.log_file, 'a+') as file:
                try:
                    item = self.data_queue.get(timeout=1).decode('utf-8')
                    if self.uboot_prompt in item:
                        self.bootstage = BootStage.E_BOOTSTAGE_UBOOT
                    if self.kernel_prompt in item:
                        self.bootstage = BootStage.E_BOOTSTAGE_KERNEL
                    with self.data_buffer_lock:
                        if len(self.data_buffer) >= self.data_buffer_threshold:
                            logger.print_warning(f"the number of lines in data_buffer has exceeded the limited buffer size {self.data_buffer_threshold}, clear buffer!")
                            self.data_buffer.clear()         # 清空列表
                            self.data_buffer_rindex = 0
                        self.data_buffer.append(item)        # 使用list存储，方便转发到cilent端
                    time_prefix = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time()))
                    if self.log_prefix != '':
                        log_prefix = '['+ self.log_prefix +']'
                        file.write(f"{time_prefix}{log_prefix}{item}")
                    else:
                        file.write(f"{time_prefix}{item}")
                    self.data_queue.task_done()               # 标记任务完成
                except queue.Empty:
                    continue
    
    def set_log_prefix(self, prefix):
        self.log_prefix = prefix
    
    def clear_log_prefix(self):
        self.log_prefix = ''
    
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
        self.bootstage = BootStage.E_BOOTSTAGE_BOOTING