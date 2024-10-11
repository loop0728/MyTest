"""System common API Test."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.common.sysapp_common_error_codes import SysappErrorCodes as EC
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from sysapp_client import SysappClient


class SysappUtCommon(SysappCaseBase):
    """
    System common API Test.
    """

    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """
        API test Case.

        Args:
            case_name: case name
            case_run_cnt: case run cnt
            script_path: script_path
            case_stage: case stage
        """
        super().__init__(case_name, case_run_cnt, script_path)
        self.uart = SysappClient(self.case_name, "uart", "uart")

    def goto_uboot_test(self):
        """
        goto_uboot API test.

        Returns:
            bool: result
        """
        result = SysappRebootOpts.reboot_to_uboot(self.uart)
        if result:
            logger.info("Please see the ./out/uart.log")
        else:
            logger.info("Go to uboot fail.Please check env.")
        return result

    def goto_kernel_test(self):
        """
        goto_kernel API test.

        Returns:
            bool: result
        """
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result:
            logger.info("Please see the ./out/uart.log")
        else:
            logger.info("Go to kernel fail.Please check env.")
        return result

    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """
        err_code = EC.SUCCESS
        ret = SysappRebootOpts.init_kernel_env(self.uart)
        if not ret:
            logger.error("Go to kernel test fail.")
            err_code = EC.FAIL
        ret = self.goto_uboot_test()
        if not ret:
            logger.error("Go to Uboot test fail.")
            err_code = EC.FAIL
        ret = self.goto_kernel_test()
        if not ret:
            logger.error("Go to kernel test fail.")
            err_code = EC.FAIL
        return err_code
