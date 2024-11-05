#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""cold reboot mode1 test scenarios"""

import time

from sysapp_sys_reboot import SysappSysRebootCase as RebootCase,SysappCheckResultWay
from suite.common.sysapp_common_logger import logger


class SysappSysColdRebootMode1(RebootCase):
    """A class representing cold reboot options
    Attributes:
        None
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.check_result_way = SysappCheckResultWay.E_CHECK_KEY_WORD
        self.goto_kernel_max_time = 5
        self.reboot_way = "cold_reboot"
        self.check_log_type = "uart.log"

    def check_board_log_keyword(self)-> int:
        """
        check board log keyword num.

        Args:
            None

        Returns:
            int: result
        """
        logger.warning("go to check_board_log_keyword\n")
        wait_times = 0
        keyword_record_dict = {}
        last_line = ''
        while wait_times < self.goto_kernel_max_time:
            result,curline = self.uart.read()
            if not result and curline == '':
                if '/ #' in last_line:
                    logger.warning("read line end!")
                    break
                wait_times += 1
                time.sleep(0.1)
                continue
            if curline != '':
                last_line = curline
                wait_times = 0
                keyword_record_dict = self.sum_keyword(curline,self.check_log_type)
            else:
                wait_times += 1
        result = self.compare_keywords(keyword_record_dict)
        if result != 0:
            return 255
        return 0

    @staticmethod
    def runcase_help():
        """ go to runcase help
        Args:
            None:
        Returns:
            None
        """
        logger.warning("support cold_reboot_mode0\1\2: 0[check result by \
                       uart send cmd is ok],1[]\n")
        logger.warning("general case runcmd:  python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_cold_reboot_mode1.py cold_reboot_mode1 1\n")
        logger.warning("support stress! eg cmd:cold_reboot_mode1_stress_5\n")
        logger.warning("stress  case runcmd:  python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_cold_reboot_mode1.py \
                       cold_reboot_mode1_stress_5 1\n")
