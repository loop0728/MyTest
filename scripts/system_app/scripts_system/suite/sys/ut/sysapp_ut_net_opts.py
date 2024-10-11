#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""newwork ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
from suite.common.sysapp_common_error_codes import SysappErrorCodes

class SysappUtNetworkTest(CaseBase):
    """
    A class representing network test flow.
    Attributes:
        uart (Client): Clinet instance.
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name.
            case_run_cnt (int): the number of times the test case runs.
            module_path_name (str): moudle path.
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def network_test(self):
        """
        Network test.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        fail_cnt = 0
        result = SysappRebootOpts.init_uboot_env(self.uart)
        if not result:
            return result

        logger.info("test set board ip at uboot phase ...")
        result = SysappNetOpts.setup_network(self.uart)
        if result:
            logger.warning("test set board ip success at uboot phase")
        else:
            logger.error("test set board ip fail at uboot phase")
            fail_cnt += 1

        logger.info("test set board ip at kernel phase ...")
        logger.info("reboot to kernel")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            return result

        result = SysappNetOpts.setup_network(self.uart)
        if result:
            logger.warning("test set board ip success at kernel phase")
        else:
            logger.error("test set board ip fail at kernel phase")
            fail_cnt += 1

        if fail_cnt > 0:
            result = False

        return result

    @sysapp_print.print_line_info
    def runcase(self):
        """
        Test function body.
        Args:
            None:
        Returns:
            error_code (SysappErrorCodes): Result of test.
        """
        error_code = SysappErrorCodes.FAIL
        result = self.network_test()
        if result:
            error_code = SysappErrorCodes.SUCCESS

        return error_code

    @sysapp_print.print_line_info
    @staticmethod
    def system_help():
        """
        Help info.
        Args:
            None:
        Returns:
            None:
        """
        logger.warning("test register")
        logger.warning("cmd: RegisterTest")
