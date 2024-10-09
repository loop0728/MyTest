#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""str_crc test case for AOV scenarios"""

import re
from cases.platform.sys.aov.str_crc_var import (STR_CRC_OK, STR_CRC_FAIL,
                                                SUSPEND_CRC_START_ADDR,
                                                SUSPEND_CRC_END_ADDR)
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_error_codes import ErrorCodes
from sysapp_client import SysappClient as Client


class SysappAovStrCrc(CaseBase):
    """
    A class representing str_crc test flow.
    Attributes:
        self.uart (object): device handle
        suspend_crc_param (str): str_crc env parameters
        default_bootargs (str): default bootargs_linux_only
        str_crc_bootargs (str): str_crc bootargs_linux_only
        cmd_str (str): str test command
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """
        Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.suspend_crc_param = (f"suspend_crc={hex(SUSPEND_CRC_START_ADDR)},"
                                  f"{hex(SUSPEND_CRC_END_ADDR)}")
        self.default_bootargs = ""
        self.str_crc_bootargs = ""
        self.cmd_str = ("echo 10 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer;"
                        "echo mem > /sys/power/state")

    @logger.print_line_info
    def str_crc_test(self):
        """
        do str crc test and parse log.
        Args:
            None:
        Returns:
            result (bool): If parse log success, return True; Else, return False.
        """
        result = False
        logger.print_warning("do str crc check ...")
        result = self.uart.write(self.cmd_str)

        while True:
            status, line = self.uart.read(1, 15)
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if str(STR_CRC_OK).strip() in line:
                    logger.print_warning("str crc check success")
                    result = True
                    break
                if str(STR_CRC_FAIL).strip() in line:
                    logger.print_error("str crc check fail")
                    result = False
                    break
            else:
                logger.print_error(f"read line fail after cmd:{self.cmd_str}")
                result = False
                break
        return result

    def set_crc_test_env(self):
        """
        Set str_crc param in bootargs for test.
        Args:
            None:
        Returns:
            result (bool): If set str_crc env success, return True; Else, return False.
        """
        result = False
        bootargs = ""
        pattern = r"suspend_crc=[^ ]* "
        logger.print_warning("set crc test env ...")
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if not result:
            logger.print_error("the device is not at kernel or at uboot")
            return result
        result, bootargs = SysappRebootOpts.get_bootenv(self.uart, "bootargs_linux_only")

        # if fw tool is not exsit, reboot to uboot to get bootenv
        if not result and bootargs is None:
            result = SysappRebootOpts.reboot_to_uboot(self.uart)
            if result:
                result, bootargs = SysappRebootOpts.get_bootenv(self.uart, "bootargs_linux_only")

        if result:
            self.default_bootargs = re.sub(pattern, "", bootargs.strip())
            if self.suspend_crc_param in bootargs:
                self.str_crc_bootargs = bootargs.strip()
                logger.print_info("suspend_crc_param has been set, test directly!")
            else:
                # change bootargs and check if change success
                self.str_crc_bootargs = self.default_bootargs + " " + self.suspend_crc_param
                result = SysappRebootOpts.set_bootenv(self.uart, "bootargs_linux_only",
                                                      self.str_crc_bootargs)
                # if fw_printenv is exist, but fw_setenv is not exist
                if not result:
                    result = SysappRebootOpts.reboot_to_uboot(self.uart)
                    if result:
                        SysappRebootOpts.set_bootenv(self.uart, "bootargs_linux_only",
                                                     self.str_crc_bootargs)
                logger.print_info(f"set bootargs: {self.str_crc_bootargs}")
                # reboot to uboot to check if change bootargs success
                result = SysappRebootOpts.reboot_to_uboot(self.uart)
                if result:
                    result, bootargs = SysappRebootOpts.get_bootenv(self.uart,
                                                                    "bootargs_linux_only")
                    if result and self.suspend_crc_param in bootargs:
                        logger.print_info("set str_crc bootargs success")
                        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result:
            logger.print_warning("set crc test env success")
        else:
            logger.print_error("set crc test env fail")

        return result

    def recovery_default_env(self):
        """
        Recovery bootargs.
        Args:
            None:
        Returns:
            result (bool): If recovery bootargs success, return True; Else, return False.
        """
        result = False
        bootargs = ""
        pattern = r"suspend_crc=[^ ]*"
        logger.print_warning("recovery default env ...")
        result, bootargs = SysappRebootOpts.get_bootenv(self.uart, "bootargs_linux_only")

        # if fw tool is not exsit, reboot to uboot to get bootenv
        if not result and bootargs is None:
            result = SysappRebootOpts.reboot_to_uboot(self.uart)
            if result:
                result, bootargs = SysappRebootOpts.get_bootenv(self.uart, "bootargs_linux_only")

        if result:
            self.default_bootargs = re.sub(pattern, "", bootargs.strip())
            if "suspend_crc" not in bootargs:
                logger.print_info("suspend_crc_param has not been set, no need to remove!")
            else:
                # change bootargs and check if change success
                result = SysappRebootOpts.set_bootenv(self.uart, "bootargs_linux_only",
                                                      self.default_bootargs)
                # if fw_printenv is exist, but fw_setenv is not exist
                if not result:
                    result = SysappRebootOpts.reboot_to_uboot(self.uart)
                    if result:
                        SysappRebootOpts.set_bootenv(self.uart, "bootargs_linux_only",
                                                     self.default_bootargs)
                logger.print_info(f"set bootargs: {self.default_bootargs}")
                # reboot to uboot to check if change bootargs success
                result = SysappRebootOpts.reboot_to_uboot(self.uart)
                if result:
                    result, bootargs = SysappRebootOpts.get_bootenv(self.uart,
                                                                    "bootargs_linux_only")
                    if result and "suspend_crc" in bootargs:
                        logger.print_error("recovery bootargs fail")
                        result = False
        result &= SysappRebootOpts.reboot_to_kernel(self.uart)

        if result:
            logger.print_warning("recovery default env success")
        else:
            logger.print_error("recovery default env fail")

        return result

    def runcase(self):
        """
        Test function body.
        Args:
            None:
        Returns:
            error_code (Errorcodes): Result of test.
        """
        error_code = ErrorCodes.FAIL
        result = False
        result = self.set_crc_test_env()

        if result:
            result = self.str_crc_test()

        # need to judge if it needs to burn image refer to the return value.
        result &= self.recovery_default_env()

        if result:
            error_code = ErrorCodes.SUCCESS
        else:
            error_code = ErrorCodes.FAIL

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
        logger.print_warning("stat str crc test")
        logger.print_warning("cmd : echo 3 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
        logger.print_warning("cmd : echo mem > /sys/power/state")
        logger.print_warning("if the result return 'CRC check success', test pass; "
                             "if the result return 'CRC check fail', test fail.")
