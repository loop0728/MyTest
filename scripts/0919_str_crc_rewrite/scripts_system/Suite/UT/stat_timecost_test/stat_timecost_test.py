#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""stat time cost for UT scenarios"""

import timeit
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from Common.error_codes import ErrorCodes as EC
from client import Client

class StatTimeCostTest(CaseBase):
    """A class representing stat time cost test flow
    Attributes:
        uart (Device): device handle
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def stat_cmd_execute_time(self) -> bool:
        """test function
        Args:
            None
        Returns:
            result (bool): if the command executes success, return True; else, return False
        """
        result = False
        cmd = ("echo 1234567890123456789012345678901234567890123456789012345678901234567890"
               "12345678901234567890123456789012345678901234567890")
        result = self.uart.write(cmd)
        if result is False:
            logger.print_error(f"Write fail: {cmd}")
            return result
        status, line = self.uart.read()
        if status:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
                if len(line) == len(cmd) - 5:
                    result = True

        return result

    def runcase(self) -> int:
        err_code = EC.SUCCESS
        cnt = 100
        execution_time = timeit.timeit(self.stat_cmd_execute_time, number=cnt)
        print(f"single cmd run {cnt} times, cost time：{execution_time} s")
        #self.uart.write(f'ls')
        #self.uart.read(10)

        return err_code
