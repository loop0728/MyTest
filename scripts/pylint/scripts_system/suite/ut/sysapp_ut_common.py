"""System common API Test."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from python_scripts.logger import logger
from common.sysapp_common_case_base import SysappCaseBase
from common.sysapp_common_error_codes import ErrorCodes as EC
import common.sysapp_common as sys_common
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
        result = sys_common.goto_uboot(self.uart)
        if result is True:
            logger.print_info("Please see the ./out/uart.log")
        else:
            logger.print_info("Go to uboot fail.Please check env.")
        return result

    def goto_kernel_test(self):
        """
        goto_kernel API test.

        Returns:
            bool: result
        """
        result = sys_common.goto_kernel(self.uart)
        if result is True:
            logger.print_info("Please see the ./out/uart.log")
        else:
            logger.print_info("Go to kernel fail.Please check env.")
        return result

    def ensure_file_exists_test(self):
        """ensure_file_exists API test."""
        test_file1 = "test_file1.txt"
        test_file2 = "test/test_file2.txt"
        test_file3 = "./test/test_file3.txt"
        sys_common.ensure_file_exists(test_file1)
        sys_common.ensure_file_exists(test_file2)
        sys_common.ensure_file_exists(test_file3)
        logger.print_info(
            "Please check 'test_file1.txt' 'test/test_file2.txt' and './test/test_file3.txt'."
        )
        return True

    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """
        err_code = EC.SUCCESS
        ret = self.goto_kernel_test()
        if ret is False:
            logger.print_error("Go to kernel test fail.")
            err_code = EC.FAIL
        ret = self.goto_uboot_test()
        if ret is False:
            logger.print_error("Go to Uboot test fail.")
            err_code = EC.FAIL
        ret = self.goto_kernel_test()
        if ret is False:
            logger.print_error("Go to kernel test fail.")
            err_code = EC.FAIL
        ret = self.ensure_file_exists_test()
        if ret is False:
            logger.print_error("Ensure file exist test fail.")
            err_code = EC.FAIL
        return err_code
