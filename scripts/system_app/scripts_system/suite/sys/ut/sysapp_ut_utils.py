#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Utils ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
import suite.common.sysapp_common_utils as SysappUtils
from suite.common.sysapp_common_types import SysappErrorCodes

class SysappUtUtils(CaseBase):
    """
    A class representing utils api test.
    Attributes:
        uart (Client): Clinet instance.
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name.
            case_run_cnt (int): the number of times the test case runs.
            module_path_name (str): moudle path.
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def utils_api_test(self):
        """
        Register test.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        logger.warning("test cmd and return single line data ...")
        ret_read_single_line, data = SysappUtils.write_and_match_keyword(self.uart,
                                                                         "ifconfig -a",
                                                                         "TX bytes")
        if ret_read_single_line:
            logger.info(f"read data: {data}")
        else:
            logger.error("not match keyword!")

        logger.warning("test cmd and return all read data ...")
        ret_read_multi_line, data = SysappUtils.write_and_match_keyword(self.uart,
                                                                        "ifconfig -a",
                                                                        "TX bytes",
                                                                        True)
        if ret_read_multi_line:
            logger.info(f"read data: {data}")
        else:
            logger.error("not match keyword!")

        result = (ret_read_single_line and ret_read_multi_line)
        return result

    @sysapp_print.print_line_info
    def runcase(self):
        """
        Test function body.
        Args:
            None:
        Returns:
            error_code (SysappErrorCodes): Result of test.
        """
        error_code = SysappErrorCodes.FAIL
        result = self.utils_api_test()
        if result:
            error_code = SysappErrorCodes.SUCCESS

        return error_code

    @sysapp_print.print_line_info
    @staticmethod
    def system_help():
        """
        Help info.
        Args:
            None:
        Returns:
            None:
        """
        logger.warning("test utils api")
