"""Server is used to communicate with the client. Send data to client."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import socket
import threading
import json
import re
from concurrent.futures import ThreadPoolExecutor

from sysapp_platform import (
    PLATFORM_NET_CONNECT_PORT,
    LOG_PATH,
    PLATFORM_UART,
    PLATFORM_BOARD_IP,
)
from suite.common.sysapp_common_logger import logger

from device.sysapp_dev_serial import SysappDevSerial
from device.sysapp_dev_telnet import SysappDevTelnet


class SysappDeviceManager:
    """
    Device Manager.
    """

    def __init__(self):
        """Device manager."""
        self.devices = {}
        self.locks = {}
        self.lock = threading.Lock()

    def register_device(self, device) -> bool:
        """
        Add device to DM.

        Args:
            device (object) : device
        """
        with self.lock:
            if device.name in self.devices:
                raise ValueError(f"Device with name {device.name} already exists")
            self.devices[device.name] = device
            self.locks[device.name] = False
        return True

    def acquire_device(self, device_name) -> None:
        """
        Acquire device.

        Args:
            device_name (str) : device name
        """
        with self.lock:
            if device_name in self.devices and not self.locks[device_name]:
                self.locks[device_name] = True      # lock device
            else:
                raise Exception(
                    f"Device {device_name} is not available or already locked"
                    )
        self.devices[device_name].connect()
        self.devices[device_name].start_read_thread()
        self.devices[device_name].start_save_data_thread()
        return self.devices[device_name]

    def release_device(self, device_name) -> None:
        """
        Release device from DM.

        Args:
            device_name (str): device name
        """
        with self.lock:
            if device_name in self.devices and self.locks[device_name]:
                self.devices[device_name].disconnect()
                self.devices.pop(device_name)
                self.locks[device_name] = False  # unlock device

    def update_case_name(self, case_name) -> None:
        """
        Update case name to all device.

        Args:
            case_name (str): case name
        """
        with self.lock:
            for _, device_value in self.devices.items():
                device_value.case_name = case_name


class SysappServer:
    """
    Server for get device data and send to client.
    """

    def __init__(self):
        """Init Server."""
        self.server_param = {
            "max_workers" : 5,
            "listen_client_num" : 5,
            "rev_max_datalen" : 1024
        }

        self._server_socket = None
        self._delimiter = "mstar"
        self._case_name = ""
        self._dm = SysappDeviceManager()

    def device_init(self):
        """Open uart."""
        dev_name = "uart"
        uart_device = SysappDevSerial(dev_name, PLATFORM_UART, LOG_PATH)
        self._dm.register_device(uart_device)
        self._dm.acquire_device(dev_name)

    def device_deinit(self):
        """Close uart."""
        dev_name = "uart"
        self._dm.release_device(dev_name)

    def send_msg_to_client(self, client, msg):
        """
        Send msg to client.

        Args:
            client (object): client object
            msg: dict: data
        """
        msg = json.dumps(msg)
        full_msg = f"{msg}{self._delimiter}"
        client.sendall(full_msg.encode("utf-8"))

    def response_msg_to_client(self, client, status, data=""):
        """
        Response msg to client.

        Args:
            client (object): client object
            status (bool): response status
            data (str): response data
        """
        if status is True:
            response = {"status": "recv_ok", "data": data}
        else:
            response = {"status": "recv_fail", "data": ""}
        response = json.dumps(response)
        full_msg = f"{response}{self._delimiter}"
        client.sendall(full_msg.encode("utf-8"))

    def parasing_data(self, msg):
        """
        parasing client data

        Args:
            msg (bytes): client data

        Returns:
            list: data from client
        """
        res_msg_list = []
        if isinstance(msg, bytes):
            # tmprequest = re.split(self._delimiter, msg.decode("utf-8", errors="replace"))
            # logger.info(f"thread_callfun Received no strip: {tmprequest}")
            msg = msg.decode("utf-8", errors="replace").strip(self._delimiter)
            res_msg_list = re.split(self._delimiter, msg)
        return res_msg_list

    def write(self, client, msg):
        """Write to device."""
        device_name = msg["device_name"]
        data_to_write = msg["data"]
        result = self._dm.devices[device_name].write(data_to_write)
        self.response_msg_to_client(client, result)

    def read(self, client, msg):
        """Readline from device."""
        device_name = msg["device_name"]
        timeout = msg["timeout"]
        data = self._dm.devices[device_name].read(timeout)
        # if no '\n', add it
        if data:
            if not data.endswith(b'\n'):
                data += b'\n'
            client.sendall(data)

    def get_board_cur_state(self, client, msg):
        """Get board curr state"""
        device_name = msg["device_name"]
        board_cur_state = self._dm.devices[device_name].get_bootstage()
        self.response_msg_to_client(client, True, board_cur_state)

    def clear_board_cur_state(self, client, msg):
        """Clear board curr state"""
        result = 255
        device_name = msg["device_name"]
        result = self._dm.devices[device_name].clear_bootstage()
        self.response_msg_to_client(client, True)
        return result

    def clear(self, client, msg):
        """Clear device buffer."""
        device_name = msg["device_name"]
        result = self._dm.devices[device_name].queue_clear("tmp_data_queue")
        self.response_msg_to_client(client, result)

    def regiser_device(self, client, msg) -> bool:
        """
        Regiser device to Device Manager.

        Args:
            client (object): client
            msg (dict): data from client

        Returns:
            bool: result
        """
        # logger.warning("regiser_device")
        result = False
        device_type = msg["device_type"]
        device_name = msg["device_name"]
        if device_name not in self._dm.devices:
            if device_type == "telnet":
                logger.info(f"{device_type}: {device_name}: {PLATFORM_BOARD_IP}")
                port = 23
                telnet_log = "./out/" + device_name + ".log"
                telnet_device = SysappDevTelnet(device_name, PLATFORM_BOARD_IP, port, telnet_log)
                self._dm.register_device(telnet_device)
                self._dm.acquire_device(device_name)
                self._dm.update_case_name(self._case_name)
                result = True
            elif device_type == "uart":
                logger.warning("Please user default handle.")
            else:
                logger.error(f"device type: {device_type} not exist.")
        else:
            logger.warning(f"device name: {device_name} existed.")
        self.response_msg_to_client(client, result)
        return result

    def prepare_msg(self, client, msg):
        """The first cmd. update case name."""
        result = True
        self._case_name = msg["case_name"]
        self._dm.update_case_name(self._case_name)
        self.response_msg_to_client(client, result)

    def client_close(self, client, msg):
        """
        Close client.

        Args:
            client (class): socket handle
        """
        # logger.info("client close!!!!")
        device_name = msg["device_name"]
        self.response_msg_to_client(client, True)
        client.close()
        if device_name != "uart":
            self._dm.release_device(device_name)
        # exit thread_callfun
        sys.exit()

    def server_exit(self, client):
        """
        exit server.

        Args:
            client (class): socket handle
        """
        self.response_msg_to_client(client, True)
        client.close()
        self.server_stop()

    def thread_callfun(self, client):
        """
        Handling cmd.

        Args:
            client (class): socket handle

        Returns:
            int: result
        """
        request_msg_list = []
        while True:
            request = client.recv(self.server_param['rev_max_datalen'])
            request_msg_list = self.parasing_data(request)
            for item in request_msg_list:
                param = json.loads(item)
                cmd = param["cmd"]
                if hasattr(self, cmd):
                    cmd_callback = getattr(self, cmd)
                    cmd_callback(client, param)
                if cmd == "client_close":
                    return 0
            request_msg_list = []
            time.sleep(0.01)

    def get_client_data(self):
        """Wait client connect."""
        thread_pool = ThreadPoolExecutor(self.server_param['max_workers'])
        while self._server_socket:
            try:
                # Accepted connection
                client, addr = self._server_socket.accept()
                logger.info(f"[INFO] Accepted connection from {addr[0]}:{addr[1]}")
                # Determine whether the first message is a server exit.
                request = client.recv(self.server_param['rev_max_datalen'])
                request_msg_list = self.parasing_data(request)
                for item in request_msg_list:
                    param = json.loads(item)
                    cmd = param["cmd"]
                    if cmd == "server_exit":
                        self.server_exit(client)
                        return 0
                    if hasattr(self, cmd):
                        cmd_callback = getattr(self, cmd)
                        cmd_callback(client, param)
                # add cilent to thread pool
                thread_pool.submit(self.thread_callfun, client)
            except socket.error as e:
                logger.error(f"Socket error: {e}")
                continue
        return 0

    @staticmethod
    def check_env():
        """Check env"""
        result = True
        if LOG_PATH == "":
            logger.error("Please check sysapp_platform.py LOG_PATH")
            result = False
        if PLATFORM_UART == "":
            logger.error("Please check sysapp_platform.py PLATFORM_UART")
            result = False
        return result

    def server_start(self):
        """Start server."""
        ss_host = "localhost"
        ss_port = PLATFORM_NET_CONNECT_PORT

        logger.info("Server start.")
        result = self.check_env()
        if result is False:
            return
        # open uart
        self.device_init()
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._server_socket:
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((ss_host, ss_port))
        self._server_socket.listen(self.server_param['listen_client_num'])
        server_thread = threading.Thread(target=self.get_client_data)
        server_thread.start()

    def server_stop(self):
        """Stop server."""
        logger.info("Server stop.")
        # close server socket
        self._server_socket.close()
        # close uart
        self.device_deinit()


def main():
    """Entry"""
    server_handle = SysappServer()
    server_handle.server_start()

if __name__ == "__main__":
    main()
