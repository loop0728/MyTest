"""Client API Test."""

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
from sysapp_client import SysappClient
from python_scripts.logger import logger
import common.sysapp_common as sys_common
from common.sysapp_common_case_base import SysappCaseBase
from common.sysapp_common_error_codes import ErrorCodes as EC


class SysappUtClient(SysappCaseBase):
    """Client API Test."""

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
        self.write_cmd_lst = ["中文", "%", "123", "中^文", " ", "NULL"]

    def write_cmd_test(self, device) -> bool:
        """
        Client write API test.

        Returns:
            bool: result
        """
        result = True
        for write_cmd in self.write_cmd_lst:
            result = device.write(write_cmd)
            if result is False:
                logger.print_error(f"Write fail: {write_cmd}")
                continue
            time.sleep(1)
        return result

    def read_cmd_test(self, device, case_num, log_path, resource_log) -> bool:
        """
        Client read API test.

        Returns:
            bool: result
        """
        test_cmd = ""
        test_cmd1 = "cat /mnt/scripts_system/Suite/UT/resource/test1.log"
        test_cmd2 = "cat /mnt/scripts_system/Suite/UT/resource/test2.log"
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
            result, data = device.read()
            if result is True:
                if data.strip() == "/ #":
                    logger.print_info("Read end.")
                    break
                else:
                    with open(log_path, "a+", encoding="utf-8") as file:
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
        """
        Run case entry.

        Returns:
            int: Error code
        """
        err_code = EC.SUCCESS
        test_cmd1_log = "out/read_test1.log"
        resource_test1_log = "suite/ut/resource/test1.log"
        test_cmd2_log = "out/read_test2.log"
        resource_test2_log = "suite/ut/resource/test2.log"

        uart = SysappClient(self.case_name, "uart", "uart")
        sys_common.goto_kernel(uart)
        sys_common.set_board_kernel_ip(uart)
        sys_common.mount_to_server(uart)

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
