#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" BSP General Case: module loading"""
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.bsp.general_cases.common.sysapp_bsp_general_case_base import SysappBspGeneralCaseBase
from suite.common.sysapp_common_error_codes import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from sysapp_client import SysappClient as Client

class SysappBspModuleLoading(SysappCaseBase, SysappBspGeneralCaseBase):
    """A class representing  module loading test flow
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

        SysappCaseBase.__init__(self, case_name, case_run_cnt, module_path_name)
        SysappBspGeneralCaseBase.__init__(self,case_name)
        self.uart = Client(self.case_name, "uart", "uart")

    @sysapp_print.print_line_info
    def runcase(self):
        """test function body
        Args:
            None
        Returns:
            result (int): result of test
        """

        ret_test = 0

        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result is False:
            logger.info("BSP case module loading reboot to kernel fail !")
            return SysappErrorCodes.FAIL

        args = {'insmod and rmmod cnt':2}

        ret_test =  self.run_mid_func("module_loading", args)

        if ret_test != 0:

            return SysappErrorCodes.FAIL

        return SysappErrorCodes.SUCCESS

    @staticmethod
    @sysapp_print.print_line_info
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("Test insmod and rmmod of bsp module")
