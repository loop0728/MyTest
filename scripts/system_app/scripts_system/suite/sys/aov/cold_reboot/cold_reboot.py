#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""cold reboot test case for AOV scenarios"""

from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_error_codes import ErrorCodes
from sysapp_client import SysappClient as Client

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
            error_code (ErrorCodes): result of test
        """
        error_code = ErrorCodes.FAIL
        result = False
        result = SysappRebootOpts.cold_reboot_to_uboot(self.uart)
        result &= SysappRebootOpts.cold_reboot_to_kernel(self.uart)

        if result:
            error_code =  ErrorCodes.SUCCESS
        return error_code

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
