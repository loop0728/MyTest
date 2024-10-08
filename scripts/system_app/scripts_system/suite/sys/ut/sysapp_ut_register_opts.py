#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Register ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_register_opts import SysappRegisterOpts
from suite.common.sysapp_common_error_codes import ErrorCodes

class SysappUtRegisterTest(CaseBase):
    """
    A class representing regiseter test flow.
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

    def register_test(self):
        """
        Register test.
        Args:
            None:
        Returns:
            error_code (ErrorCodes): Test success, return ErrorCodes.SUCCESS;
            Else, return ErrorCodes.FAIL.
        """
        error_code = ErrorCodes.FAIL
        result = False
        str_reg_value = ""
        bank = "3f"
        offset = "1"
        set_value = "78"
        result = SysappRebootOpts.init_uboot_env(self.uart)
        if not result:
            return result

        logger.print_info("test read register at uboot phase ...")
        result, str_reg_value = SysappRegisterOpts.read_register(self.uart, bank, offset)
        if result:
            logger.print_warning("test read register success at uboot phase, the value of "
                                 f"{bank}:{offset} is {str_reg_value}")
        else:
            logger.print_error("test read register fail at uboot phase")

        logger.print_info("test write register at uboot phase ...")
        result = SysappRegisterOpts.write_register(self.uart, bank, offset, set_value)
        if result:
            logger.print_warning("test write register success at uboot phase, set the value of "
                                 f"{bank}:{offset} to {set_value}")
        else:
            logger.print_error("test write register fail at uboot phase")

        logger.print_info("test read register at kernel phase ...")
        logger.print_info("reboot to kernel")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            error_code = ErrorCodes.FAIL
            return error_code

        result, str_reg_value = SysappRegisterOpts.read_register(self.uart, bank, offset)
        if result:
            logger.print_warning("test read register success at kernel phase, the value of "
                                 f"{bank}:{offset} is {str_reg_value}")
        else:
            logger.print_error("test read register fail at kernel phase")

        logger.print_info("test write register at kernel phase ...")
        result = SysappRegisterOpts.write_register(self.uart, bank, offset, set_value)
        if result:
            logger.print_warning("test write register success at kernel phase, set the value of "
                                 f"{bank}:{offset} to {set_value}")
        else:
            logger.print_error("test write register fail at kernel phase")

        if result:
            error_code = ErrorCodes.SUCCESS

        return error_code

    @logger.print_line_info
    def runcase(self):
        """
        Test function body.
        Args:
            None:
        Returns:
            error_code (ErrorCodes): Result of test.
        """
        error_code = ErrorCodes.FAIL
        result = self.register_test()
        if result:
            error_code = ErrorCodes.SUCCESS

        return error_code

    @logger.print_line_info
    @staticmethod
    def system_help():
        """
        Help info.
        Args:
            None:
        Returns:
            None:
        """
        logger.print_warning("test register")
        logger.print_warning("cmd: RegisterTest")
