#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import socket
import threading
import json
import re
from concurrent.futures import ThreadPoolExecutor

from PythonScripts.variables import net_connect_port, log_path, uart_port, relay_port, dev_uart, board_ip
from PythonScripts.logger import logger

from Device.serial_device import SerialDevice
from Device.telnet import TelnetDevice

class DeviceManager():
    def __init__(self) -> None:
        self.devices = {}                        # 存储设备对象
        self.locks = {}                          # 存储设备的锁状态
        self.lock = threading.Lock()

    def register_device(self, device) -> bool:
        with self.lock:
            if device.name in self.devices:
                raise ValueError(f"Device with name {device.name} already exists")
            self.devices[device.name] = device
            self.locks[device.name] = False      # 初始化锁状态为未锁定
        return True

    def acquire_device(self, device_name) -> None:
        with self.lock:
            if device_name in self.devices and not self.locks[device_name]:
                self.locks[device_name] = True  # 锁定设备
                self.devices[device_name].connect()
                self.devices[device_name].start_read_thread()
                self.devices[device_name].start_save_data_thread()
                return self.devices[device_name]
            else:
                raise Exception(f"Device {device_name} is not available or already locked")

    def release_device(self, device_name) -> None:
        with self.lock:
            if device_name in self.devices and self.locks[device_name]:
                self.devices[device_name].disconnect()
                self.locks[device_name] = False  # 解锁设备

    def update_case_name(self, case_name) -> None:
        with self.lock:
            for device_name in self.devices:
                self.devices[device_name].case_name = case_name


class Server():
    def __init__(self, max_workers=5, listen_client_num=5, rev_max_datalen=1024):
        self.server_handler = None
        self.server_thread_running = True
        self.max_workers = max_workers
        self.listen_client_num = listen_client_num
        self.rev_max_datalen = rev_max_datalen
        self.dev_name = 'uart'
        self.delimiter = 'mstar'
        self.host = 'localhost'
        self.port = int(net_connect_port)
        # 创建 Socket 对象
        self.thread_pool = ThreadPoolExecutor(self.max_workers)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.server_socket:
           self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.dm = DeviceManager()
        self.case_name = ''

    def device_init(self):
        uart_device = SerialDevice(self.dev_name, uart_port, log_path)
        self.dm.register_device(uart_device)
        self.dm.acquire_device(self.dev_name)

    def device_deinit(self):
        self.dm.release_device(self.dev_name)

    def send_msg_to_client(self, client, msg):
        """
        发送消息, 保证发送消息时统一格式

        Args:
            client: Class: socket 对象
            msg: dict: 发送的消息内容

        Returns:
            None
        """
        msg = json.dumps(msg)
        full_msg = f"{msg}{self.delimiter}"
        client.sendall(full_msg.encode('utf-8'))

    def response_msg_to_client(self, client, status, data=''):
        """
        回复消息, 保证回复消息时统一格式

        Args:
            client (Class): socket 对象
            status (bool): 状态，告诉cilent端发送的消息是否符合协议格式

        Returns:
            None
        """
        if status is True:
            response = {"status": "recv_ok", "data": data}
        else:
            response = {"status": "recv_fail", "data": ""}
        response = json.dumps(response)
        full_msg = f"{response}{self.delimiter}"
        client.sendall(full_msg.encode('utf-8'))

    def parasing_data(self, msg):
        """
        解析socket接收到的信息

        Args:
            msg (bytes): socket接收到数据

        Returns:
            list: 每个成员是以分隔符区分的字典
        """
        res_msg_list = []
        if isinstance(msg, bytes):
            tmprequest = re.split(self.delimiter, msg.decode('utf-8', errors='replace'))
            # logger.print_info(f"thread_callfun Received no strip: {tmprequest}")
            msg = msg.decode('utf-8', errors='replace').strip(self.delimiter)
            res_msg_list = re.split(self.delimiter, msg)
        return res_msg_list

    def write(self, client, msg):
        """
        写入命令到device

        Args:
            None

        Returns:
            None
        """
        # print("write")
        device_name = msg["device_name"]
        data_to_write = msg["data"]
        result = self.dm.devices[device_name].write(data_to_write)
        self.response_msg_to_client(client, result)

    def read(self, client, msg):
        """
        readline from device

        Args:
            None

        Returns:
            None
        """
        device_name = msg["device_name"]
        timeout = msg["timeout"]
        data = self.dm.devices[device_name].read(timeout)
        client.sendall(data)

    def get_borad_cur_state(self, client, msg):
        device_name = msg["device_name"]
        borad_cur_state = self.dm.devices[device_name].get_bootstage()
        self.response_msg_to_client(client, True, borad_cur_state)

    def clear_borad_cur_state(self, client, msg):
        device_name = msg["device_name"]
        result = self.dm.devices[device_name].clear_bootstage()
        self.response_msg_to_client(client, True)

    def regiser_device(self, client, msg) -> bool:
        """
        注册设备

        Args:
            device_type (str): 设备类型

        Returns:
            bool: result
        """
        # logger.print_warning("regiser_device")
        result = False
        device_type = msg["device_type"]
        device_name = msg["device_name"]
        if device_name not in self.dm.devices:
            if device_type == "telnet":
                logger.print_info(f"{device_type}: {device_name}: {board_ip}")
                port = 23
                telnet_log = './out/' + device_name + '.log'
                telnet_device = TelnetDevice(device_name, board_ip, port, telnet_log)
                self.dm.register_device(telnet_device)
                self.dm.acquire_device(device_name)
                self.dm.update_case_name(self.case_name)
                result = True
            elif device_type == "uart":
                logger.print_warning("Please user default handle.")
            else:
                logger.print_error(f"device type: {device_type} not exist.")
        else:
            logger.print_warning(f"device name: {device_name} existed.")
        self.response_msg_to_client(client, result)
        return result

    def prepare_msg(self, client, msg):
        result = True
        self.case_name = msg["case_name"]
        self.dm.update_case_name(self.case_name)                  # 所有设备更新case name
        self.response_msg_to_client(client, result)

    def client_close(self, client, msg):
        """
        cmd client_close对应动作,client退出

        Args:
            client (class): socket handle

        Returns:
            NA
        """
        # logger.print_info("client close!!!!")
        device_name = msg["device_name"]
        self.response_msg_to_client(client, True)
        client.close()
        if device_name != 'uart':
            self.dm.release_device(device_name)
        # 退出thread_callfun线程
        sys.exit()

    def server_exit(self, client):
        """
        cmd server_exit对应动作,退出server.py主进程

        Args:
            client (class): socket handle

        Returns:
            None
        """
        self.response_msg_to_client(client, True)
        client.close()
        self.server_socket.close()
        self.server_stop()

    def thread_callfun(self, client):
        """
        client端对应子线程，根据接收到的消息处理不同的业务

        Args:
            client (class): socket handle

        Returns:
            int: result
        """
        request_msg_list = []
        while True:
            request = client.recv(self.rev_max_datalen)
            request_msg_list = self.parasing_data(request)
            for item in request_msg_list:
                param = json.loads(item)
                cmd = param['cmd']
                if hasattr(server_handle, cmd):
                    cmd_callback = getattr(server_handle, cmd)
                    cmd_callback(client, param)
                if cmd == "client_close":
                    return 0
            request_msg_list = []
            time.sleep(0.01)

    def get_client_data(self):
        """
        等待client端连接，接收到连接信息后创建子线程处理

        Args:
            None

        Returns:
            None
        """
        while self.server_thread_running:
            # 阻塞等待client端连接
            client, addr = self.server_socket.accept()
            logger.print_info(f"[INFO] Accepted connection from {addr[0]}:{addr[1]}")
            # 每次client的第一条消息特殊处理，判断是否是退出server命令
            request = client.recv(self.rev_max_datalen)
            request_msg_list = self.parasing_data(request)
            for item in request_msg_list:
                param = json.loads(item)
                cmd = param['cmd']
                if cmd == 'server_exit':
                    self.server_exit(client)
                    return 0
                if hasattr(self, cmd):
                    cmd_callback = getattr(self, cmd)
                    cmd_callback(client, param)
            # 将每个client连接加入到线程池
            self.thread_pool.submit(self.thread_callfun, client)

    def server_start(self):
        logger.print_info("server_start")
        # 打开设备列表中的设备
        self.device_init()
        # 绑定 IP 和端口
        self.server_socket.bind((self.host, self.port))
        # 监听连接
        self.server_socket.listen(self.listen_client_num)
        self.server_thread_running = True
        self.server_handler = threading.Thread(target=self.get_client_data)
        self.server_handler.start()
        return 0

    def server_stop(self):
        self.server_thread_running = False
        # 关闭各设备
        self.device_deinit()

if __name__ == "__main__":
    server_handle = Server()
    server_handle.server_start()