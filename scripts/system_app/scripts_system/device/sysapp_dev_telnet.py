"""Telnet device."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telnetlib
from suite.common.sysapp_common_logger import logger
from device.sysapp_dev_base import SysappDevBase


class SysappDevTelnet(SysappDevBase):
    """
    Telnet Device.
    """

    def __init__(self, name, host, port, log_path=""):
        """
        Init Telnet.

        Args:
            name: device name
            host: Telnet server host name or IP
            port: Telnet server port
            timeout: timeout (s)
        """
        super().__init__(name, log_path)
        self.host = host
        self.port = port
        self.timeout = 10               # timeout (S)

    def connect(self) -> bool:
        """
        Connect to telnet.

        Returns:
            bool: result
        """
        username = "root"
        password = ""
        try:
            # logger.info(f"telnet connect:{self.host}:{self.port}")
            self._dev_info['conn'] = telnetlib.Telnet(self.host, self.port, self.timeout)
            timeout = 2            # login timeout
            try:
                # login
                self._dev_info['conn'].read_until(b"login:", timeout)
                self._dev_info['conn'].write(username.encode("utf-8") + b"\n")
                # Password
                self._dev_info['conn'].read_until(b"Password:", timeout)
                self._dev_info['conn'].write(password.encode("utf-8") + b"\n")
            except Exception:
                logger.info("Telnet no need login.")
            logger.info(f"Telnet connected to {self.host}:{self.port}")
            self._dev_info['running'] = True
            return True
        except Exception as e:
            logger.error(
                f"Telnet failed to connect to {self.host}:{self.port}. Error: {e}"
            )
            return False

    def disconnect(self) -> bool:
        """
        Disconnect telnet.

        Returns:
            bool: result
        """
        self._dev_info['running'] = False
        self.queue_clear(self._dev_info['data_queue'])
        self.queue_clear(self._dev_info['tmp_data_queue'])
        if self._dev_info['conn']:
            self._dev_info['conn'].close()
            logger.info(f"Connection to {self.host}:{self.port} closed.")
        return True

    def read_from_device(self):
        """Read data from telnet device."""
        timeout = 0.5
        while self._dev_info['conn']:
            try:
                data = self._dev_info['conn'].read_until(b"\n", timeout)
                if data:
                    self._dev_info['data_queue'].put(data)
                    self._dev_info['tmp_data_queue'].put(data)
            except EOFError:
                break
            except Exception:
                break
