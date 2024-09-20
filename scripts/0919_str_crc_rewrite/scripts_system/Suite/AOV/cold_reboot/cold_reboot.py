#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""cold reboot test case for AOV scenarios"""

from PythonScripts.logger import logger
from Common.case_base import CaseBase
import Common.system_common as sys_common
from client import Client

class ColdReboot(CaseBase):
    """A class representing cold reboot test flow
    Attributes:
        uart (Device): device handle
    """

    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    @logger.print_line_info
    def runcase(self):
        """test function body
        Args:
            None
        Returns:
            result (int): result of test
        """
        sys_common.cold_reboot()
        return 0

    @logger.print_line_info
    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.print_warning("dev power off, then power on")
