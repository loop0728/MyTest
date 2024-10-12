"""Device """
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json
import re
from sysapp_platform import PLATFORM_NET_CONNECT_PORT
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_types import SysappBootStage


class SysappClient:
    """Device for obtaining server information."""

    DEVICE_TYPE = ("uart", "telnet", "socket")

    def __init__(self, case_name="", device_type="uart", device_name="uart"):
        """
        Init param.

        Args:
            case_name: device name
            device_type: device log path
            device_name: device name
            rev_max_datalen: device log path
        """
        self.case_name = case_name
        self.device_type = device_type
        self.device_name = device_name
        self.rev_max_datalen = 1024
        self.delimiter = "mstar"
        self.is_open = False

        self._client_socket = None
        self._connect()

    def __del__(self):
        """Auto close connection When the client exits."""
        if self.is_open is True:
            self.close()

    def _connect(self):
        """Connect to device."""
        ss_host = "localhost"
        ss_port = PLATFORM_NET_CONNECT_PORT
        try:
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.connect((ss_host, ss_port))
            logger.info(f"client connect to server {ss_host}:{ss_port}")
            self.is_open = True
        except Exception as e:
            logger.error(f"maybe sever is offline:error[{e}]")
            raise
        result = self._prepare_msg()
        if result is False:
            logger.error("Prepare msg send fail.")
            raise ValueError("Prepare msg send fail.")
        if self.device_type != "uart":
            result = self._regiser_device(self.device_type, self.device_name)
            if result is False:
                logger.error("Regiser device fail.")
                raise ValueError("Regiser device fail.")

    def _send_msg_to_server(self, msg):
        """
        send msg to server

        Args:
            msg (dict): send msg

        Returns:
            bool: result
        """
        result = False
        msg = json.dumps(msg)
        full_msg = f"{msg}{self.delimiter}"
        try:
            self._client_socket.sendall(full_msg.encode("utf-8"))
            result = True
        except socket.error as e:
            print(f"An error occurred: {e}")
        return result

    def _parasing_data(self, msg):
        """
        Parasing server data.

        Args:
            msg (byte): recv server data

        Returns:
            list: Characters segmented by "mstar"
        """
        res_msg_list = []
        # tmprequest = re.split(self.delimiter, msg)
        # logger.info(f"thread_callfun Received no strip: {tmprequest}\n")
        msg = msg.strip(self.delimiter)
        res_msg_list = re.split(self.delimiter, msg)
        return res_msg_list

    def _send_to_server_and_check_response(self, msg, wait_timeout=5) -> bool:
        """
        Send msg to server and check response.

        Args:
            msg (byte): msg

        Returns:
            bool: result
        """
        result = False
        data = ""
        old_timeout = self._client_socket.gettimeout()
        self._client_socket.settimeout(wait_timeout)  # timeout (S)
        try:
            self._send_msg_to_server(msg)
            # print(f"_send_msg_to_server done, {msg}")
            response = self._client_socket.recv(self.rev_max_datalen)
            # print(f"response:{response}")
            if isinstance(response, bytes):
                response = response.decode("utf-8", errors="replace")
            response_msg_list = self._parasing_data(response)
            for item in response_msg_list:
                try:
                    param = json.loads(item)
                    # print(f'param: {param}')
                except json.JSONDecodeError as e:
                    logger.error(f"JSON Error Resolution: {e}")
                    return False, data
                result = bool(param["status"] == "recv_ok")
                if "data" in param.keys():
                    data = param["data"]
                else:
                    print("data is not in param")
            # print(f'data is {data}')
        except Exception as e:
            logger.warning(f"Exception e:{e}")
            self._client_socket.settimeout(old_timeout)
            return False, data
        self._client_socket.settimeout(old_timeout)
        return result, data

    def _prepare_msg(self) -> bool:
        """
        The first msg, update case name and to thread pool.

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
        Regiser device.

        Args:
            device_type (str): device type
            device_name (str): device name

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

    def write(self, data, wait_timeout=5) -> bool:
        """
        Write data to device.

        Args:
            data (str): write data

        Returns:
            bool: result
        """
        msg = {
            "case_name": self.case_name,
            "cmd": "write",
            "data": data,
            "device_name": self.device_name,
        }
        result, _ = self._send_to_server_and_check_response(msg, wait_timeout)
        return result

    def read(self, line=1, wait_timeout=5):
        """
        Read data from device.

        Args:
            line (int): lines
            wait_timeout (int): one line timeout

        Returns:
            bool,str: result, data
        """
        old_timeout = self._client_socket.gettimeout()
        self._client_socket.settimeout(wait_timeout)  # timeout (S)
        result = False
        all_data = ""
        while line > 0:
            msg = {
                "case_name": self.case_name,
                "cmd": "read",
                "device_name": self.device_name,
                "timeout": wait_timeout,
            }
            self._send_msg_to_server(msg)
            try:
                data = ""
                while True:
                    data += self._client_socket.recv(self.rev_max_datalen).decode(
                        "utf-8", errors="replace"
                    )
                    if '\n' in data:  # End of line symbol
                        break
                result = True
                all_data += data
                line -= 1  # line - 1
            except Exception as e:
                logger.warning(f"Exception e:{e}")
                result = False
                all_data += ""
                break
        # logger.info(f"Client: {all_data}")
        self._client_socket.settimeout(old_timeout)
        return result, all_data

    def close(self) -> bool:
        """
        Close device.

        Returns:
            bool: result
        """
        msg = {
            "case_name": self.case_name,
            "cmd": "client_close",
            "device_name": self.device_name,
        }
        result = self._send_msg_to_server(msg)
        if result is True:
            self._client_socket.close()
            self.is_open = False
        return result

    def get_board_cur_state(self):
        """Get board curr state"""
        msg = {
            "case_name": self.case_name,
            "cmd": "get_board_cur_state",
            "device_name": self.device_name,
        }
        result, status = self._send_to_server_and_check_response(msg)
        # print(f'status: {status}')
        return result, status

    def clear_board_cur_state(self):
        """Clear board curr state"""
        msg = {
            "case_name": self.case_name,
            "cmd": "clear_board_cur_state",
            "device_name": self.device_name,
        }
        result, _ = self._send_to_server_and_check_response(msg)
        return result

    def check_kernel_phase(self):
        """
        Check if the device is running in the kernel phase.
        Args:
            None:
        Returns:
           result (bool): If the device is at kernel, return True; Else, return False.
        """
        result, cur_state = self.get_board_cur_state()
        if result:
            if cur_state != SysappBootStage.E_BOOTSTAGE_KERNEL.name:
                result = False

        return result

    def check_uboot_phase(self):
        """
        Check if the device is running in the uboot phase.
        Args:
            None:
        Returns:
           result (bool): If the device is at uboot, return True; Else, return False.
        """
        result, cur_state = self.get_board_cur_state()
        if result:
            if cur_state != SysappBootStage.E_BOOTSTAGE_UBOOT.name:
                result = False

        return result
