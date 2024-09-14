#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json
import re
from PythonScripts.variables import net_connect_port
from PythonScripts.logger import logger
import cProfile

class Client:
    """Device for obtaining server information."""

    DEVICE_TYPE = ("uart", "telnet", "socket")

    def __init__(
        self, case_name="", device_type="uart", device_name="uart", rev_max_datalen=1024
    ):
        self.case_name = case_name
        self.rev_max_datalen = rev_max_datalen
        self.device_type = device_type
        self.device_name = device_name
        self.delimiter = "mstar"
        self.host = "localhost"
        self.port = int(net_connect_port)
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            logger.print_info(f"client connect to server {self.host}:{self.port}")
        except Exception as e:
            logger.print_warning(f"maybe sever is offline:error[{e}]")
            raise
        self.is_open = True
        self._prepare_msg()
        if self.device_type != "uart":
            self._regiser_device(self.device_type, self.device_name)

        self.profiler = cProfile.Profile()

    def __del__(self):
        if self.is_open is True:
            self.close()

    def _send_msg_to_server(self, msg):
        """
        发送消息, 保证发送消息时统一格式

        Args:
            msg: dict: 发送的消息内容

        Returns:
            NA
        """
        result = False
        msg = json.dumps(msg)
        full_msg = f"{msg}{self.delimiter}"
        try:
            self.client_socket.sendall(full_msg.encode("utf-8"))
            result = True
        except socket.error as e:
            print(f"An error occurred: {e}")
        return result

    def _parasing_data(self, msg):
        """
        解析socket接收到的信息

        Args:
            msg: socket接收到数据

        Returns:
            list: 每个成员是以分隔符区分的字典
        """
        res_msg_list = []
        # tmprequest = re.split(self.delimiter, msg)
        # logger.print_info(f"thread_callfun Received no strip: {tmprequest}\n")
        msg = msg.strip(self.delimiter)
        res_msg_list = re.split(self.delimiter, msg)
        return res_msg_list

    def _send_to_server_and_check_response(self, msg, wait_timeout=5) -> bool:
        """
        发送命令，并检测发送是否成功

        Args:
            msg: socket接收到数据

        Returns:
            result: Bool True or False
        """
        result = False
        data = ""
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(wait_timeout)  # 设置5秒超时
        try:
            self._send_msg_to_server(msg)
            # print(f"_send_msg_to_server done, {msg}")
            response = self.client_socket.recv(self.rev_max_datalen)
            # print(f"response:{response}")
            if isinstance(response, bytes):
                response = response.decode("utf-8", errors="replace")
            response_msg_list = self._parasing_data(response)
            for item in response_msg_list:
                param = json.loads(item)
                # print(f'param: {param}')
                result = bool(param["status"] == "recv_ok")
                if "data" in param.keys():
                    data = param["data"]
                else:
                    print("data is not in param")
            # print(f'data is {data}')
        except Exception as e:
            logger.print_warning(f"Exception e:{e} {__file__}:"
								 f"{e.__traceback__.tb_lineno}")
            self.client_socket.settimeout(old_timeout)
            return False, data
        self.client_socket.settimeout(old_timeout)
        return result, data

    def _send_to_server_and_get_length(self, msg, wait_timeout=5):
        """
        发送命令，获取接收的长度

        Args:
            msg (str): socket接收到数据

        Returns:
            int: length
        """
        result = 0
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(wait_timeout)  # 设置5秒超时
        try:
            self._send_msg_to_server(msg)
            response = self.client_socket.recv(self.rev_max_datalen).decode(
                "utf-8", errors="replace"
            )
            response = response.strip(self.delimiter)
            param = json.loads(response)
            status = param["status"]
            data_len = int(param["len"])
            if status == "recv_ok":
                result = data_len
            else:
                result = -1
        except Exception as e:
            # logger.print_warning(f"Exception e:{e}")
            self.client_socket.settimeout(old_timeout)
            return -1
        self.client_socket.settimeout(old_timeout)
        return result

    def _prepare_msg(self) -> bool:
        """
        第一条消息, 更新case name, 进入线程池

        Args:
            None

        Returns:
            bool: result
        """
        msg = {
            "case_name": self.case_name,
            "cmd": "prepare_msg",
        }
        result, _ = self._send_to_server_and_check_response(msg)
        return result

    def _regiser_device(self, device_type, device_name) -> bool:
        """
        注册设备

        Args:
            device_type (str): 设备类型
            device_name (str): 设备名称

        Returns:
            bool: result
        """
        self.device_name = device_name
        msg = {
            "case_name": self.case_name,
            "cmd": "regiser_device",
            "device_type": device_type,
            "device_name": self.device_name,
        }
        result, _ = self._send_to_server_and_check_response(msg)
        return result

    def write(self, data) -> bool:
        """
        写数据

        Args:
            data (str): 写入的数据

        Returns:
            bool: result
        """
        msg = {
            "case_name": self.case_name,
            "cmd": "write",
            "data": data,
            "device_name": self.device_name,
        }
        result, _ = self._send_to_server_and_check_response(msg)
        return result

    def read(self, line=1, wait_timeout=5):
        """
        读取下发写命令之后的数据

        Args:
            line (int): 读取行数
            wait_timeout (int): 每行timeout

        Returns:
            bool,str: 前一次写命令之后的一行数据
        """
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(wait_timeout)  # 设置5秒超时
        result = False
        all_data = ""
        cnt = 0
        while line > 0:
            msg = {
                "case_name": self.case_name,
                "cmd": "read",
                "device_name": self.device_name,
                "timeout": wait_timeout,
            }
            self._send_msg_to_server(msg)
            print(f"_send_msg_to_server: {msg}")
            cnt = 0
            try:
                data = ""
                while True:
                    self.profiler.enable()
                    data += self.client_socket.recv(self.rev_max_datalen).decode(
                        "utf-8"
                    )
                    cnt += 1

                    if '\n' in data:
                        break
                #self.profiler.print_stats()
                self.profiler.disable()
                result = True
                all_data += data
                line -= 1  # 剩余行数-1
            except Exception as e:
                self.profiler.print_stats()
                self.profiler.disable()
                print(f"recv cnt:{cnt}")
                logger.print_warning(f"Exception e:{e} {__file__}:"
									 f"{e.__traceback__.tb_lineno}")
                self.client_socket.settimeout(old_timeout)
                result = False
                all_data += ""
                break
        # logger.print_info(f"Client: {all_data}")
        self.client_socket.settimeout(old_timeout)
        print(f"read return: {result}, {all_data}")
        return result, all_data

    def close(self) -> bool:
        """
        通知server端关闭设备

        Args:
            NA

        Returns:
            bool: True or False
        """
        msg = {
            "case_name": self.case_name,
            "cmd": "client_close",
            "device_name": self.device_name,
        }
        result = self._send_msg_to_server(msg)
        if result is True:
            self.client_socket.close()
            self.is_open = False
        return result

    def get_borad_cur_state(self):
        msg = {
            "case_name": self.case_name,
            "cmd": "get_borad_cur_state",
            "device_name": self.device_name,
        }
        result, status = self._send_to_server_and_check_response(msg)
        # print(f'status: {status}')
        return result, status

    def clear_borad_cur_state(self):
        msg = {
            "case_name": self.case_name,
            "cmd": "clear_borad_cur_state",
            "device_name": self.device_name,
        }
        result, _ = self._send_to_server_and_check_response(msg)
        return result