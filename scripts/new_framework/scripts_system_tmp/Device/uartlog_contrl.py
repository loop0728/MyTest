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
        self.data_queue = queue.Queue()           # 使用队列存储串口数据
        self.data_buffer = []                     # 使用列表存储串口数据
        self.data_buffer_threshold = 1024         # 超过threshold个数的元素会提示（用于评估新框架data_buffer消化的内存）
        self.data_buffer_lock = threading.Lock()  # 用于同步访问data_buffer的锁
        self.data_changed = threading.Event()     # 用于通知数据已改变的事件
        self.log_file = log_file
        self.read_thread = None
        self.save_data_thread = None
        self.running = True                       # 串口打开标记
        self.read_data_running = False            # 发送数据到socket标记

    def connect(self):
        """
        连接到串口
        """
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.serial_connection.is_open:
                logger.print_info(f"Connected to {self.port}")
                # 启动读取线程
                self.read_thread = threading.Thread(target=self._read_from_port)
                self.read_thread.daemon = True
                self.read_thread.start()
                # 启动记录log线程
                self.save_data_thread = threading.Thread(target=self._save_data_to_file)
                self.save_data_thread.daemon = True
                self.save_data_thread.start()
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
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join()

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
            self.serial_connection.write(data)
            return True
        else:
            logger.print_warning("Serial port is not open")
            return False

    def _read_from_port(self):
        """
        从串口读取数据并存放到缓冲区中，串口数据生产者

        Args:
            NA

        Returns:
            NA
        """
        while self.running:
            if self.serial_connection and self.serial_connection.is_open and self.serial_connection.in_waiting > 0:
                # data = self.serial_connection.read(self.serial_connection.in_waiting)
                data = self.serial_connection.readline()
                if data:
                    self.data_queue.put(data)                    # 使用队列存储，方便存储到文件
                    # if self.read_data_running:
                    #     with self.data_buffer_lock:
                    #         self.data_buffer.append(data)        # 使用list存储，方便转发到cilent端
                    #     self.data_changed.set()                  # 通知数据已改变


    def _save_data_to_file(self, case_name=''):
        """
        将缓冲区数据保存到文件，串口数据消费者

        Args:
            case_name: 添加case_name到log

        Returns:
            NA
        """
        # 检查log文件是否存在，不存在则创建
        ensure_folder_and_file(self.log_file)
        with open(self.log_file, 'a+') as file:
            while self.running:
                try:
                    item = self.data_queue.get(timeout=1).decode('utf-8')
                    if self.read_data_running:
                        with self.data_buffer_lock:
                            self.data_buffer.append(item)        # 使用list存储，方便转发到cilent端
                        self.data_changed.set()                  # 通知数据已改变
                    if case_name != '':
                        case_name = case_name.encode('utf-8')
                        file.write(case_name)
                    file.write(f"{item}")
                    self.data_queue.task_done()               # 标记任务完成
                except queue.Empty:
                    continue

    def read_data_and_send(self, send_socket, wait_timeout = 5):
        """
        获取串口一行中的数据
        :return: 缓冲区中的数据列表
        """
        data_buffer_len = 0
        bytes_data = b''
        while self.running and self.read_data_running:
            if self.data_changed.wait(wait_timeout):          # 等待数据改变事件，或超时
                with self.data_buffer_lock:
                    data_buffer_len = len(self.data_buffer)
                    if data_buffer_len > 0:
                        #data = self.data_buffer
                        data = self.data_buffer.pop()
                        bytes_data = b''.join(data)
                if data_buffer_len > 0:
                    if data_buffer_len > self.data_buffer_threshold:
                        logger.print_warning(f"the number of lines in data_buffer has exceeded {self.data_buffer_threshold}")
                    try:
                        send_socket.sendall(bytes_data)
                    except BrokenPipeError:
                        logger.print_warning("send_socket 连接已断开")
                        send_socket.close()
                        self.data_buffer.clear()              # 清空列表
                        #self.data_changed.clear()                     # 重置事件
            else:
                pass
                # logger.print_warning("Wait for {} seconds, there is no data on the serial port".format(wait_timeout))
        # logger.print_warning("serial running :({}) or read data running :({}) is not True".format(self.running, self.read_data_running))

    def get_buffer(self):
        """
        获取缓冲区中的数据
        :return: 缓冲区中的数据列表
        """
        return self.data_queue