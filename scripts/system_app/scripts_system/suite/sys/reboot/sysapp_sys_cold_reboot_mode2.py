#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""cold reboot mode2 test scenarios"""

import time
import os
import sysapp_platform as platform
from sysapp_sys_reboot import SysappSysRebootCase as RebootCase,SysappCheckResultWay
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_net_opts import SysappNetOpts
from sysapp_client import SysappClient as Client


class SysappSysColdRebootMode2(RebootCase):
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
        self.check_result_way = SysappCheckResultWay.E_CHECK_PING
        self.try_max_cnt = 20
        self.reboot_way = "cold_reboot"

    def check_board_ping(self)-> int:
        """
        check board net status

        Args:
            None

        Returns:
            int: result
        """
        logger.warning("go to check board ping\n")
        SysappNetOpts.setup_network(self.uart)
        time.sleep(2)
        ping_cmd = "ping " + platform.PLATFORM_BOARD_IP + " -c 5 \n"
        os.system(ping_cmd)
        telnet = Client(self.case_name, "telnet", "telnet0")
        if not telnet.is_open:
            logger.error("telnet open fail! \n")
            return 255
        logger.warning("telnet open is ok! \n")
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
        logger.warning("support cold_reboot_mode0\1\2: 0[check result by \
                       uart send cmd is ok],1[]\n")
        logger.warning("general case runcmd:  python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_cold_reboot_mode2.py cold_reboot_mode2 1\n")
        logger.warning("support stress! eg cmd:cold_reboot_mode2_stress_5\n")
        logger.warning("stress  case runcmd:  python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_cold_reboot_mode2.py \
                       cold_reboot_mode2_stress_5 1\n")
