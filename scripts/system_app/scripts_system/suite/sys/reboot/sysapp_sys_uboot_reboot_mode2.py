#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""uboot reboot mode2 test scenarios"""

import time
import os
import sysapp_platform as platform
from sysapp_sys_reboot import SysappSysRebootCase as RebootCase,SysappCheckResultWay
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_net_opts import SysappNetOpts
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from sysapp_client import SysappClient as Client

class SysappSysUbootRebootMode2(RebootCase):
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
        self.check_result_way = SysappCheckResultWay.E_CHECK_PING
        self.try_max_cnt = 20
        self.goto_uboot_way = "kernel_goto_uboot" # cold_reboot_goto_uboot kernel_goto_uboot

    def check_board_ping(self)-> int:
        """check board ping(check net status).
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """

        logger.warning("go to check_board_log_keyword\n")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            logger.error("goto uboot is fail")
            return result
        SysappNetOpts.setup_network(self.uart)
        time.sleep(2)
        ping_cmd = "ping " + platform.PLATFORM_BOARD_IP + " -c 5 \n"
        os.system(ping_cmd)
        telnet = Client(self.case_name, "telnet", "telnet0")
        telnet.write("\n\n")
        result,line = telnet.read()
        try_cnt = 0
        while '/ #' not in line and try_cnt < self.try_max_cnt:
            telnet.write("cd /\n")
            result,line = telnet.read()
            if result:
                logger.warning(f"telnet line str is:{line} !\n")
            try_cnt += 1
            time.sleep(0.1)
        if '/ #' not in line:
            logger.warning("telnet is fail !\n")
            telnet.close()
            return 255
        telnet.close()
        return 0


    @staticmethod
    def runcase_help():
        """ go to runcase help
        Args:
            None:
        Returns:
            None
        """
        logger.warning("support kernel_reboot_mode0\1\2: 0[check result\
                        by uart send cmd is ok],1[]\n")
        logger.warning("general case runcmd:  python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_uboot_reboot_mode2.py uboot_reboot_mode2 1\n")
        logger.warning("support stress! eg cmd:uboot_reboot_mode2_stress_5\n")
        logger.warning("stress  case runcmd: python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_uboot_reboot_mode2.py \
                       uboot_reboot_mode2_stress_5 1\n")
