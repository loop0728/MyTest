"""Relay Device"""

#!usr/bin/python
# -*- coding: utf-8 -*-

# __all__ = ['_SysAppDevRelay']

import platform
import serial
from python_scripts.logger import logger


class SysappDevRelay:
    """
    Relay for control board.
    """

    def __init__(self, relay, port="/dev/relay_uart", baudrate=9600):
        """
        Relay is a serial device.

        Args:
            relay: the link N.O. of the Relays.
            port: port
            baudrate: baudrate
            timeout: timeout
        """
        self.relay = relay
        self.port = port
        self.baudrate = baudrate
        self.timeout = 0.05

        self._connection = None

    def connect(self):
        """
        Connect to relay.

        Returns:
            bool: result
        """
        result = False
        os_info = platform.system()
        if os_info == "Windows":
            self.port = "COM" + self.port

        try:
            self._connection = serial.Serial(
                self.port, self.baudrate, timeout=self.timeout
            )
            if self._connection.is_open:
                logger.print_info(f"Connected to {self.port} baudrate {self.baudrate}")
                result = True
            else:
                logger.print_error(f"Failed to connect to {self.port}")
                result = False
        except serial.SerialException as e:
            logger.print_error(f"Failed to connect to {self.port}: {e}")
            result = False
        return result

    def disconnect(self):
        """Disconnect relay."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.print_info(f"Disconnected from {self.port}")
        return True

    def power_off(self):
        """Board power off."""
        power_off_arr = [0x33, 0x01, 0x11, 0x00, 0x00, 0x00, 0x00, 0x45]
        power_off_arr[6] = power_off_arr[6] + self.relay
        power_off_arr[7] = power_off_arr[7] + self.relay
        if self._connection.is_open:
            logger.print_info(f"Power off relay:{self.relay}")
            self._connection.write(power_off_arr)
        else:
            logger.print_error("power_off open failed")

    def power_on(self):
        """Board power on."""
        power_on_arr = [0x33, 0x01, 0x12, 0x00, 0x00, 0x00, 0x00, 0x46]
        power_on_arr[7] = power_on_arr[7] + self.relay
        power_on_arr[6] = power_on_arr[6] + self.relay
        if self._connection.is_open:
            logger.print_info(f"Power on relay:{self.relay}")
            self._connection.write(power_on_arr)
        else:
            logger.print_error("power_on open failed")
