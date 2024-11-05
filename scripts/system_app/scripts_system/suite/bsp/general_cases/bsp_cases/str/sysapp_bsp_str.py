#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" BSP General Case: suspend to ram test"""
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.bsp.general_cases.common.sysapp_bsp_general_case_base import SysappBspGeneralCaseBase
from suite.common.sysapp_common_error_codes import SysappErrorCodes
from sysapp_client import SysappClient as Client

class SysappBspStr(SysappCaseBase, SysappBspGeneralCaseBase):
    """A class representing  suspend to ram test flow
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
        args = {"test":1}
        self.run_mid_func("str", args)
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
        logger.warning("Test the BSP module before and after suspend to RAM")
