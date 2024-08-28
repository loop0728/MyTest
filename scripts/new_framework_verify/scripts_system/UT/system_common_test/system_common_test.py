#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/01 15:06:50
# @file        : system_common_test.py
# @description : test system_common

from PythonScripts.logger import logger
from Common.case_base import CaseBase
from Common.error_codes import ErrorCodes as EC
import Common.system_common as sys_common
from client import Client


class system_common_test(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def goto_uboot_test(self):
        result = sys_common.goto_uboot(self.uart)
        if result is True:
            logger.print_info("Please see the ./out/uart.log")
        else:
            logger.print_info("Go to uboot fail.Please check env.")
        return result

    def goto_kernel_test(self):
        result = sys_common.goto_kernel(self.uart)
        if result is True:
            logger.print_info("Please see the ./out/uart.log")
        else:
            logger.print_info("Go to kernel fail.Please check env.")
        return result

    def ensure_file_exists_test(self):
        test_file1 = "test_file1.txt"
        test_file2 = "test/test_file2.txt"
        test_file3 = "./test/test_file3.txt"
        sys_common.ensure_file_exists(test_file1)
        sys_common.ensure_file_exists(test_file2)
        sys_common.ensure_file_exists(test_file3)
        logger.print_info("Please check 'test_file1.txt' 'test/test_file2.txt' and './test/test_file3.txt'.")

    def runcase(self):
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