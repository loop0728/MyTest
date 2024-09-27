"""Stat timecost Test."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import timeit
from sysapp_client import SysappClient
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.common.sysapp_common_error_codes import ErrorCodes as EC


class SysappUtStatTimecost(SysappCaseBase):
    """Stat timecost test."""

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

    def stat_cmd_excute_time(self) -> bool:
        """
        stat cmd excute time test.

        Returns:
            bool: result
        """
        result = False
        cmd = ("echo 12345678901234567890123456789012345678901234567890123456789"
               "0123456789012345678901234567890123456789012345678901234567890")
        result = self.uart.write(cmd)
        if result is False:
            logger.print_error(f"Write fail: {cmd}")
            return result
        status, line = self.uart.read()
        if status is True:
            if isinstance(line, bytes):
                line = line.decode("utf-8", errors="replace").strip()
                if len(line) == len(cmd) - 5:
                    result = True

        return result

    def runcase(self) -> int:
        """
        Run case entry.

        Returns:
            int: Error code
        """
        err_code = EC.SUCCESS
        cnt = 100
        execution_time = timeit.timeit(self.stat_cmd_excute_time, number=cnt)
        print(f"single cmd run {cnt} times, cost time: {execution_time} s")

        return err_code
