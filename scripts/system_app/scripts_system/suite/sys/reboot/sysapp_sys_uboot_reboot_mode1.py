#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""uboot reboot mode1 test scenarios"""

import time
from sysapp_sys_reboot import SysappSysRebootCase as RebootCase,SysappCheckResultWay
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts


class SysappSysUbootRebootMode1(RebootCase):
    """A class representing uboot reboot options
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
        self.reboot_way = "uboot_reboot"
        self.check_result_way = SysappCheckResultWay.E_CHECK_KEY_WORD
        self.goto_kernel_max_time = 20
        self.kernel_reboot_cmd = "reboot -f"
        self.goto_uboot_way = "kernel_goto_uboot" # cold_reboot_goto_uboot kernel_goto_uboot
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
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            logger.error("goto uboot is fail")
            return result
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
        logger.warning("support kernel_reboot_mode0\1\2: 0 \
                       [check result by uart send cmd is ok],1[]\n")
        logger.warning("general case runcmd:  python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_uboot_reboot_mode1.py uboot_reboot_mode1 1\n")
        logger.warning("support stress! eg cmd:uboot_reboot_mode1_stress_5\n")
        logger.warning("stress  case runcmd: python sysapp_run_user_case.py \
                    suite/sys/reboot/sysapp_sys_uboot_reboot_mode1.py\
                    uboot_reboot_mode1_stress_5 1\n")
