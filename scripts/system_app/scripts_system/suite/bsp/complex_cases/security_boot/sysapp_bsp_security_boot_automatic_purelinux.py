#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""test for security boot with automatic(purelinux)"""

from suite.common.sysapp_common_utils import write_and_match_keyword
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_burning_opts import SysappBurningOpts
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_types import SysappErrorCodes as EC
from sysapp_client import SysappClient


class SysappBspSecurityBootAutomaticPurelinux(CaseBase):
    """Sysapp BSP security boot automatic purelinux class

    Attributes:
        case_name: case name
        case_run_cnt: case run cnt
        script_path: script path
        uart: uart
    """

    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """case init function

        Args:
            case_name (str): case name
            case_run_cnt (int): case run cnt
            script_path (str): script path
        """

        super().__init__(case_name, case_run_cnt, script_path)
        self.case_name = case_name
        self.case_run_cnt = case_run_cnt
        self.script_path = script_path
        self.uart = SysappClient(self.case_name, "uart", "uart")

        logger.info(f"{self.case_name} init successful")

    @sysapp_print.print_line_info
    def case_deinit(self):
        """case deinit function

        Returns:
            bool: True
        """
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result is False:
            logger.error("case_deinit Fail")

        logger.info("run case_deinit succeed")
        return True

    def runcase(self):
        """Run case entry.

        Args:
            Na

        Returns:
            enum: ErrorCodes code
        """
        err_code = EC.FAIL

        # 1. burning image form tftp
        result = SysappBurningOpts.burning_image_for_tftp()
        if result:
            err_code = EC.SUCCESS
            logger.info("burning_image_for_tftp succeed")
            return err_code
        else:
            err_code = EC.FAIL
            logger.error("burning_image_for_tftp failed")

        # 2. check if the current system is Linux
        result = write_and_match_keyword(self.uart, cmd="ls", keyword="/ #")
        if result:
            err_code = EC.SUCCESS
            logger.info("check board's stage succeed")
            return err_code
        else:
            err_code = EC.FAIL
            logger.error("check board's stage failed")

        return err_code
