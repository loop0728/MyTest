#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""cold reboot mode0 test scenarios"""

from sysapp_sys_reboot import SysappSysRebootCase as RebootCase,SysappCheckResultWay
from suite.common.sysapp_common_logger import logger

class SysappSysColdRebootMode0(RebootCase):
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
        self.reboot_way = "cold_reboot"
        self.check_result_way = SysappCheckResultWay.E_CHECK_UART
        self.goto_kernel_max_time = 200

    def check_board_uart_status(self) ->int:
        """
        check board uart status.

        Args:
            None

        Returns:
            int: result
        """
        logger.warning("go to check_board_uart_status !\n")
        result, data = self.write_return_ret(self.uart, 'pwd' , 1, 3)
        if result and int(data) == 0:
            logger.info("=======uart is ok========\n")
            return 0
        else:
            logger.error("=======uart is abnormal========\n")
        return 255

    @staticmethod
    def runcase_help():
        """ go to runcase help
        Args:
            None:
        Returns:
            None
        """
        logger.warning("support cold_reboot_mode0\1\2: 0[check result \
                       by uart send cmd is ok],1[]\n")
        logger.warning("general case runcmd:python sysapp_run_user_case.py\
                        suite/sys/reboot/sysapp_sys_cold_reboot_mode0.py cold_reboot_mode0 1\n")
        logger.warning("support stress! eg cmd:cold_reboot_mode0_stress_5\n")
        logger.warning("stress case runcmd:python sysapp_run_user_case.py \
                       suite/sys/reboot/sysapp_sys_cold_reboot_mode0.py\
                       cold_reboot_mode0_stress_5 1\n")
