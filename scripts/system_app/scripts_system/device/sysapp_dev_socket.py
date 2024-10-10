"""Socket device."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
from suite.common.sysapp_common_logger import logger
from device.sysapp_dev_base import SysappDevBase


class SysappDevSocket(SysappDevBase):
    """
    Socket Device.
    """

    def __init__(self, name, host, port, log_path=""):
        """
        Init Socket.

        Args:
            name: device name
            host: Telnet server host name or IP
            port: Telnet server port
            timeout: timeout (s)
        """
        super().__init__(name, log_path)
        self.host = host
        self.port = port
        self.timeout = 10
        self.rev_max_datalen = 1024

    def connect(self) -> bool:
        """
        Connect to socket.

        Returns:
            bool: result
        """
        try:
            self._dev_info['conn'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._dev_info['conn'].connect((self.host, self.port))
            logger.info(f"Socket {self.name} Connect")
            self._dev_info['running'] = True
            return True
        except Exception as e:
            logger.info(
                f"Failed to connect to {self.host}:{self.port}. Error: {e}"
            )
            return False

    def disconnect(self) -> bool:
        """
        Disconnect.

        Returns:
            bool: result
        """
        self._dev_info['running'] = False
        if self._dev_info['conn']:
            self._dev_info['conn'].close()
            logger.info(f"Socket {self.name} disconnect")
        return True

    def write(self, data) -> bool:
        """
        Write data to device.

        Args:
            data (str): write data

        Returns:
            bool: result
        """
        self.queue_clear(self._dev_info['tmp_data_queue'])
        if self._dev_info['conn']:
            self._dev_info['conn'].sendall(data.encode("utf-8") + b"\n")
            return True
        else:
            logger.info("Socket not connect, cant't send.")
            return False

    def read_from_device(self):
        """Start read device data."""
        logger.info("start read socket data.")
        while self._dev_info['conn']:
            data = self._dev_info['conn'].recv(self.rev_max_datalen)
            if data:
                self._dev_info['data_queue'].put(data)
                self._dev_info['tmp_data_queue'].put(data)
