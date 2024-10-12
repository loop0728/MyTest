#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""burning image ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_burning_opts import SysappBurning
from suite.common.sysapp_common_types import SysappErrorCodes

class SysappUtBurningOpts(CaseBase):
    """
    A class representing burning image test flow.
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

    def runcase(self):
        """
        Test function body.
        Args:
            None:
        Returns:
            error_code (SysappErrorCodes): Result of test.
        """
        error_code = SysappErrorCodes.FAIL
        logger.warning("Run burning image.")
        burning_test = SysappBurning(self.uart)
        result = burning_test.burning_image_for_tftp()
        if result:
            error_code = SysappErrorCodes.SUCCESS

        return error_code

    @staticmethod
    def system_help():
        """
        Help info.
        Args:
            None:
        Returns:
            None:
        """
        logger.warning("test burning image")
