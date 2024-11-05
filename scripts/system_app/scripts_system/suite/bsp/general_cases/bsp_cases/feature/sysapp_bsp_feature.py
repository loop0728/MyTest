#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" BSP General Case: feature test"""
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.bsp.general_cases.common.sysapp_bsp_general_case_base import SysappBspGeneralCaseBase
from suite.common.sysapp_common_error_codes import SysappErrorCodes
from sysapp_client import SysappClient as Client

class SysappBspFeature(SysappCaseBase, SysappBspGeneralCaseBase):
    """A class representing  feature test flow
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
        args=[]
        ret=SysappErrorCodes.SUCCESS

        args.append(self.uart)
        args.append(self.case_stage)
        cmd = ["run","check_result","exit"]
        for i in range(3):
            args.append(f"{cmd[i]}")
            result=self.run_mid_func("feature", args)
            if result:
                ret = SysappErrorCodes.FAIL
                break
            args.remove(cmd[i])

        return ret

    @staticmethod
    @sysapp_print.print_line_info
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("Test whether all peripheral modules function properly"
                        "when running at the same time")
