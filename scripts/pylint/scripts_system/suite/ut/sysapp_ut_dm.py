"""Device manager Test."""

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import threading
from python_scripts.logger import logger
from common.sysapp_common_case_base import SysappCaseBase
from common.sysapp_common_error_codes import ErrorCodes as EC
import common.sysapp_common as sys_common
from sysapp_client import SysappClient


class SysappUtDm(SysappCaseBase):
    """Device manager Test."""

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

    def device_manager_test(self, device, log_path, resource_log):
        """
        device_manager API test.

        Returns:
            bool: result
        """
        if os.path.exists(log_path):
            os.remove(log_path)
            logger.print_info(f"{log_path} removed.")
        sys_common.ensure_file_exists(log_path)
        test_cmd = "cat /mnt/scripts_system/Suite/UT/resource/test1.log"
        device.write(test_cmd)
        while True:
            try:
                result, data = device.read()
                if result is True:
                    if data.strip() == "/ #":
                        break
                    else:
                        with open(log_path, "a+", encoding='utf-8') as file:
                            file.write(f"{data}")
                else:
                    break
            except Exception as e:
                logger.print_info(f"read fail {e}")
                break
        result = sys_common.are_files_equal_line_by_line(log_path, resource_log)
        if result == 255:
            logger.print_error(f"{test_cmd} fail.")
        else:
            logger.print_info(f"{test_cmd} pass.")
        return result

    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """
        result = EC.SUCCESS

        log_path = "out/read_serial.log"
        log_path1 = "./out/read_telnet1.log"
        log_path2 = "./out/read_telnet2.log"
        log_path3 = "./out/read_telnet3.log"
        resource_log = "suite/ut/resource/test1.log"

        uart = SysappClient(self.case_name, "uart", "uart")

        sys_common.goto_kernel(uart)
        sys_common.set_board_kernel_ip(uart)
        sys_common.mount_to_server(uart)

        telnet1 = SysappClient(self.case_name, "telnet", "telnet1")
        telnet2 = SysappClient(self.case_name, "telnet", "telnet2")
        telnet3 = SysappClient(self.case_name, "telnet", "telnet3")

        t1 = threading.Thread(
            target=self.device_manager_test,
            kwargs={
                "device": telnet1,
                "log_path": log_path1,
                "resource_log": resource_log,
            },
        )
        t2 = threading.Thread(
            target=self.device_manager_test,
            kwargs={
                "device": telnet2,
                "log_path": log_path2,
                "resource_log": resource_log,
            },
        )
        t3 = threading.Thread(
            target=self.device_manager_test,
            kwargs={
                "device": telnet3,
                "log_path": log_path3,
                "resource_log": resource_log,
            },
        )
        t4 = threading.Thread(
            target=self.device_manager_test,
            kwargs={
                "device": uart,
                "log_path": log_path,
                "resource_log": resource_log
            },
        )

        # 启动线程
        t4.start()
        t1.start()
        t2.start()
        t3.start()

        # 等待所有线程完成
        t4.join()
        t1.join()
        t2.join()
        t3.join()

        return result
