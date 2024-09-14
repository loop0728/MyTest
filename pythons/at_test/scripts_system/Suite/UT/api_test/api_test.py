#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/01 11:47:27
# @file        : api_test.py
# @description :

import os
import time
from datetime import datetime
from PythonScripts.logger import logger
import Common.system_common as sys_common
from Common.case_base import CaseBase
from client import Client
from Common.error_codes import ErrorCodes as EC

class api_test(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.write_cmd_lst = ["中文", "%", "123", "中^文", " ", "NULL"]

    def write_cmd_test(self, device) -> bool:
        result = True
        for write_cmd in self.write_cmd_lst:
            result = device.write(write_cmd)
            if result is False:
                logger.print_error(f"Write fail: {write_cmd}")
                break
            time.sleep(1)
        return result

    def read_cmd_test(self, device, case_num, log_path, resource_log) -> bool:
        test_cmd1 = 'cat /mnt/scripts_system/Suite/UT/resource/test1.log'
        test_cmd2 = 'cat /mnt/scripts_system/Suite/UT/resource/test2.log'
        if case_num == 1:
            test_cmd = test_cmd1
        elif case_num == 2:
            test_cmd = test_cmd2
        if os.path.exists(log_path):
            os.remove(log_path)
            logger.print_info(f"{log_path} removed.")
        sys_common.ensure_file_exists(log_path)
        device.write(test_cmd)
        while True:
            result,data = device.read()
            if result is True:
                if data.strip() == '/ #':
                    logger.print_info("Read end.")
                    break
                else:
                    with open(log_path, 'a+') as file:
                        # now = datetime.now()
                        # formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        # file.write(f"[{formatted_time}]{data}")
                        file.write(f"{data}")
            else:
                logger.print_warning("Read time out.")
                break
        result = sys_common.are_files_equal_line_by_line(log_path, resource_log)
        if result == 255:
            logger.print_error(f"{test_cmd} fail.")
            return result
        else:
            logger.print_info(f"{test_cmd} pass.")
        return True

    def runcase(self) -> int:
        err_code = EC.SUCCESS
        test_cmd1_log = "out/read_test1.log"
        resource_test1_log = "Suite/UT/resource/test1.log"
        test_cmd2_log = "out/read_test2.log"
        resource_test2_log = "Suite/UT/resource/test2.log"

        uart = Client(self.case_name, "uart", "uart")
        ret = self.write_cmd_test(uart)
        if ret is False:
            logger.print_error("Write test fail.")
            err_code = EC.FAIL
        ret = self.read_cmd_test(uart, 1, test_cmd1_log, resource_test1_log)
        if ret is False:
            logger.print_error("Read test1 fail.")
            err_code = EC.FAIL
        ret = self.read_cmd_test(uart, 2, test_cmd2_log, resource_test2_log)
        if ret is False:
            logger.print_error("Read test fail.")
            err_code = EC.FAIL

        return err_code