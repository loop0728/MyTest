#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json

from PythonScripts.variables import net_connect_port
from PythonScripts.logger import logger

class Client():
    def __init__(self, case_name='', device_type='uart', device_name='uart', rev_max_datalen=1024):
        self.case_name = case_name
        self.rev_max_datalen = rev_max_datalen
        self.device_type = device_type
        self.device_name = device_name
        self.delimiter = 'mstar'
        self.data_length = 0
        self.host = 'localhost'
        self.port = int(net_connect_port)
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            logger.print_info(f'client connect to server {self.host}:{self.port}')
        except Exception as e:
            logger.print_warning(f'maybe sever is offline:error[{e}]')
            raise
        self.is_open = True
        self.prepare_msg()
        if self.device_type != 'uart':
            self.regiser_device(self.device_type, self.device_name)

    def send_msg_to_server(self, msg):
        """
        发送消息, 保证发送消息时统一格式

        Args:
            msg: dict: 发送的消息内容

        Returns:
            NA
        """
        msg = json.dumps(msg)
        full_msg = f"{msg}{self.delimiter}"
        self.client_socket.sendall(full_msg.encode('utf-8'))

    def send_to_server_and_check_response(self, msg, wait_timeout = 5) -> bool:
        """
        发送命令，并检测发送是否成功

        Args:
            msg (str): socket接收到数据

        Returns:
            bool: True or False
        """
        result = False
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(wait_timeout)       # 设置5秒超时
        try:
            self.send_msg_to_server(msg)
            response = self.client_socket.recv(self.rev_max_datalen).decode('utf-8')
            if 'recv_ok' in response:
                result = True
            else:
                result = False
        except Exception as e:
            # logger.print_warning(f"Exception e:{e}")
            self.client_socket.settimeout(old_timeout)
            return False
        self.client_socket.settimeout(old_timeout)
        return result

    def send_to_server_and_get_length(self, msg, wait_timeout = 5):
        """
        发送命令，获取接收的长度

        Args:
            msg (str): socket接收到数据

        Returns:
            int: length
        """
        result = 0
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(wait_timeout)       # 设置5秒超时
        try:
            self.send_msg_to_server(msg)
            response = self.client_socket.recv(self.rev_max_datalen).decode('utf-8')
            response = response.strip(self.delimiter)
            param = json.loads(response)
            status = param['status']
            data_len = int(param['len'])
            if status == 'recv_ok':
                result = data_len
            else:
                result = -1
        except Exception as e:
            # logger.print_warning(f"Exception e:{e}")
            self.client_socket.settimeout(old_timeout)
            return -1
        self.client_socket.settimeout(old_timeout)
        return result

    def prepare_msg(self) -> bool:
        """
        第一条消息, 更新case name, 进入线程池

        Args:
            None

        Returns:
            bool: result
        """
        msg = {"case_name": self.case_name, "cmd": "prepare_msg", "case_name": self.case_name}
        result = self.send_to_server_and_check_response(msg)
        return result

    def regiser_device(self, device_type, device_name) -> bool:
        """
        注册设备

        Args:
            device_type (str): 设备类型
            device_name (str): 设备名称

        Returns:
            bool: result
        """
        self.device_name = device_name
        msg = {"case_name": self.case_name, "cmd": "regiser_device", "device_type": device_type, "device_name": self.device_name}
        result = self.send_to_server_and_check_response(msg)
        return result

    def write(self, data) -> bool:
        """
        写数据

        Args:
            data (str): 写入的数据

        Returns:
            bool: result
        """
        msg = {"case_name": self.case_name, "cmd": "write", "data": data, "device_name": self.device_name}
        result = self.send_to_server_and_check_response(msg)
        return result

    def read(self, line = 1, wait_timeout = 5):
        """
        读取下发写命令之后的数据

        Args:
            line (int): 读取行数
            wait_timeout (int): 每行timeout

        Returns:
            bool,str: 前一次写命令之后的一行数据
        """
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(wait_timeout)       # 设置5秒超时
        result = False
        all_data = ''
        while line > 0:
            msg = {"case_name": self.case_name, "cmd": "read", "device_name": self.device_name, "timeout": wait_timeout}
            self.data_length = self.send_to_server_and_get_length(msg)
            if self.data_length == 0:
                result = False
                all_data += b''
                break
            try:
                data = b''
                while len(data) < self.data_length:
                    to_read = min(self.data_length - len(data), self.rev_max_datalen)
                    data += self.client_socket.recv(to_read)
                data = data.decode('GBK')
                self.client_socket.settimeout(old_timeout)
                result = True
                all_data += data
                line -= 1                             # 剩余行数-1
            except Exception as e:
                logger.print_warning(f"Exception e:{e}")
                self.client_socket.settimeout(old_timeout)
                result = False
                all_data += ''
                break
        return result,all_data

    def close(self) -> bool:
        """
        通知server端关闭设备

        Args:
            NA

        Returns:
            bool: True or False
        """
        msg = {"case_name": self.case_name,"cmd": "client_close", "device_name": self.device_name}
        result = self.send_msg_to_server(msg)
        if result is True:
            self.client_socket.close()
            self.is_open = False
        return result