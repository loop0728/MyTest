"""Serial Device"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import serial
from python_scripts.logger import logger
from device.sysapp_dev_base import SysappDevBase


class SysappDevSerial(SysappDevBase):
    """
    Serial Device.
    """

    def __init__(self, name, port, log_file="", baudrate=115200):
        """
        Init serial.

        Args:
            name: device name
            port: serial name, ex: '/dev/ttyUSB0'(Linux) or 'COM3'(Windows)
            baudrate: baudrate
            timeout: timeout
        """
        super().__init__(name, log_file)
        self.port = port
        self.baudrate = baudrate
        self.timeout = 1

    def connect(self) -> bool:
        """
        Connect to serial.

        Returns:
            bool: result
        """
        result = False
        try:
            self._dev_info['conn'] = serial.Serial(
                self.port, self.baudrate, timeout=self.timeout
            )
            if self._dev_info['conn'].is_open:
                logger.print_info(f"Connected to {self.port} baudrate {self.baudrate}")
                self._dev_info['running'] = True
                result = True
            else:
                logger.print_warning(f"Failed to connect to {self.port}")
                result = False
        except serial.SerialException as e:
            logger.print_warning(f"Failed to connect to {self.port}: {e}")
            result = False
        return result

    def disconnect(self) -> bool:
        """
        Disconnect.

        Returns:
            bool: result
        """
        time.sleep(2)
        self._dev_info['running'] = False
        conn = self._dev_info['conn']
        if conn and conn.is_open:
            conn.close()
            logger.print_info(f"Disconnected from {self.port}")
            if self._dev_info["read_thread"] and self._dev_info["read_thread"].is_alive():
                self._dev_info["read_thread"].join()
            if self._dev_info["save_data_thread"] and self._dev_info["save_data_thread"].is_alive():
                self._dev_info["save_data_thread"].join()
        return True
