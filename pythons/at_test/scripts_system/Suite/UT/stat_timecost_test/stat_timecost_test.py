#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/01 11:47:27
# @file        : stat_timecost_test.py
# @description :

import os
import time
from datetime import datetime
from PythonScripts.logger import logger
import Common.system_common as sys_common
from Common.case_base import CaseBase
from client import Client
from Common.error_codes import ErrorCodes as EC
import timeit

class stat_timecost_test(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def stat_cmd_excute_time(self) -> bool:
        result = False
        cmd = "echo 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
        result = self.uart.write(cmd)
        if result is False:
            logger.print_error(f"Write fail: {cmd}")
            return result
        status, line = self.uart.read()
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
                if len(line) == len(cmd) - 5:
                    result = True

        return result

    def runcase(self) -> int:
        err_code = EC.SUCCESS
        #cnt = 100
        #execution_time = timeit.timeit(self.stat_cmd_excute_time, number=cnt)
        #print(f"single cmd run {cnt} times, cost time：{execution_time} s")
        self.uart.write(f'ls')
        self.uart.read(10)

        return err_code
