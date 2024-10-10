"""Device Base Class"""

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from enum import Enum
import queue
from datetime import datetime
import threading
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common import ensure_file_exists


# pylint: disable=C0103
class BootStage(Enum):
    """
    Boot Stage Enum.
    """

    E_BOOTSTAGE_UBOOT = 1
    E_BOOTSTAGE_KERNEL = 2
    E_BOOTSTAGE_UNKNOWN = 3


class SysappDevBase(ABC):
    """
    Base calss fo devices communicating with the board.
    """

    def __init__(self, name, log_file):
        """
        Init device param.

        Args:
            name: device name
            log_file: device log path
        """
        self.name = name
        self.case_name = ""
        self.uboot_prompt = "SigmaStar #"
        self.kernel_prompt = "/ #"
        self.bootstage = BootStage.E_BOOTSTAGE_UNKNOWN

        self._dev_info = {
            'running': False,
            'conn': None,
            'data_queue': queue.Queue(),
            'tmp_data_queue': queue.Queue(),
            'read_thread': None,
            'save_data_thread': None,
            'log_file': log_file,
        }

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect device.
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect device.
        """
        pass

    def write(self, data) -> bool:
        """
        Write data to device.

        Args:
            data (str): write data

        Returns:
            bool: result
        """
        result = False
        curr_line = 0
        self.queue_clear(self._dev_info["tmp_data_queue"])
        if self._dev_info["conn"]:
            if self.name != "uart" or self.name == "uart" and self._dev_info["conn"].is_open:
                self._dev_info["conn"].write(data.encode("utf-8") + b"\n")
                data = data.strip()
                curr_data = ""
                while curr_line < 10:  # wait 10 lines
                    data_new = (
                        self.read().decode("utf-8", errors="replace").strip(" \r\n")
                    )
                    curr_data += data_new
                    if data in curr_data or "?" in curr_data:
                        result = True
                        break
                    curr_line += 1
        else:
            logger.warning(f"{self.__class__.__name__} port is not open")
        return result

    def read(self, wait_timeout=2) -> bytes:
        """
        Read device data.

        Args:
            wait_timeout (int): timeout

        Returns:
            bytes: data
        """
        terminator = b""
        # logger.warning(f"self.__class__.__name__ read.")
        try:
            data = self._dev_info["tmp_data_queue"].get(timeout=wait_timeout - 0.5)
            data += terminator
            return data
        except queue.Empty:
            logger.warning(
                f"{self.__class__.__name__} _tmp_data_queue is empty."
            )
            return b""

    @staticmethod
    def queue_clear(data_queue):
        """
        Clean read data queue.

        Args:
            data_queue (queue): queue name
        """
        while not data_queue.empty():
            data_queue.get_nowait()

    def set_case_name(self, case_name):
        """
        Set case name.

        Args:
            case_name (str): case name
        """
        self.case_name = case_name

    def get_case_name(self):
        """
        Get case name.

        Returns:
            str: case name
        """
        return self.case_name

    def start_read_thread(self):
        """Start read."""
        self.queue_clear(self._dev_info["data_queue"])
        self.queue_clear(self._dev_info["tmp_data_queue"])
        read_thread = threading.Thread(target=self.read_from_device)
        read_thread.start()

    def start_save_data_thread(self):
        """Start save data to file."""
        save_data_thread = threading.Thread(target=self.save_data_to_file)
        save_data_thread.start()

    def read_from_device(self):
        """Start read device data."""
        logger.info("start read uart data.")
        conn = self._dev_info['conn']
        while self._dev_info['running']:
            if conn and conn.is_open and conn.in_waiting > 0:
                # data = self._dev_info['conn'].read(self._dev_info['conn'].in_waiting)
                data = conn.readline()
                if data:
                    self._dev_info["data_queue"].put(data)
                    self._dev_info["tmp_data_queue"].put(data)

    def save_data_to_file(self):
        """Start save device data."""
        logger.info(f"start save data to {self._dev_info['log_file']}.")
        ensure_file_exists(self._dev_info["log_file"])  # ensure file exists
        while self._dev_info['running']:
            try:
                item = (
                    self._dev_info["data_queue"]
                    .get(timeout=1)
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                if self.uboot_prompt in item:
                    self.bootstage = BootStage.E_BOOTSTAGE_UBOOT
                if self.kernel_prompt in item:
                    self.bootstage = BootStage.E_BOOTSTAGE_KERNEL
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(self._dev_info["log_file"], "a+", encoding="utf-8") as file:
                    file.write(f"[{formatted_time} {self.case_name}] {item}\n")
                self._dev_info["data_queue"].task_done()
            except queue.Empty:
                continue

    def get_bootstage(self):
        """
        Get bootstage.

        Returns:
            str: status
        """
        status = self.bootstage.name
        return status

    def clear_bootstage(self):
        """
        Clear bootstage.
        """
        self.bootstage = BootStage.E_BOOTSTAGE_UNKNOWN
