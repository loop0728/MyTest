#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""str_crc test case for AOV scenarios"""

import re
from str_crc_var import STR_CRC_OK, STR_CRC_FAIL, SUSPEND_CRC_START_ADDR, SUSPEND_CRC_END_ADDR
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from Common.reboot_opts import RebootOpts
from client import Client

class StrCrc(CaseBase):
    """A class representing str_crc test flow
    Attributes:
        case_env_param (dict): env parameters
        case_cmd_param (dict): test commands
        case_test_param (dict): internal parameters for test
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.reboot_opt = RebootOpts(self.uart)
        self.suspend_crc_param = (f"suspend_crc={hex(SUSPEND_CRC_START_ADDR)},"
                                  f"{hex(SUSPEND_CRC_END_ADDR)}")
        self.default_bootargs = ""
        self.str_crc_bootargs = ""
        self.cmd_str = ("echo 10 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer;"
                        "echo mem > /sys/power/state")

    def _uboot_set_suspend_crc(self):
        result = 255
        bootargs = ""
        pattern = r"suspend_crc=[^ ]* "
        result, bootargs = self.reboot_opt.uboot_get_bootenv("bootargs_linux_only")
        if result == 0:
            if self.suspend_crc_param in bootargs:
                self.str_crc_bootargs = bootargs.strip()
                self.default_bootargs = re.sub(pattern, "", bootargs.strip())
                logger.print_info("suspend_crc_param has been set, test directly!")
            else:
                self.default_bootargs = re.sub(pattern, "", bootargs.strip())
                self.str_crc_bootargs = self.default_bootargs + " " + self.suspend_crc_param
                self.reboot_opt.uboot_set_bootenv("bootargs_linux_only", self.str_crc_bootargs)
                logger.print_info(f"uboot set bootargs: {self.str_crc_bootargs}")
                result = self.reboot_opt.uboot_to_uboot()
                if result == 0:
                    # check if changing bootargs ok
                    result, bootargs = self.reboot_opt.uboot_get_bootenv("bootargs_linux_only")
                    if result == 0:
                        if self.suspend_crc_param in bootargs:
                            result = self.reboot_opt.uboot_to_kernel()
                        else:
                            # set suspend_crc_param fail
                            result = 255
                    # else, uboot get bootargs fail
                # else, boot to uboot fail
        # else, uboot get bootargs fail
        return result

    def _kernel_set_suspend_crc(self):
        result = 255
        bootargs = ""
        pattern = r"suspend_crc=[^ ]* "
        result, bootargs = self.reboot_opt.kernel_get_bootenv("bootargs_linux_only")
        if result == 0:
            if self.suspend_crc_param in bootargs:
                self.str_crc_bootargs = bootargs.strip()
                self.default_bootargs = re.sub(pattern, "", bootargs.strip())
                logger.print_info("suspend_crc_param has been set, test directly!")
            else:
                self.default_bootargs = re.sub(pattern, "", bootargs.strip())
                self.str_crc_bootargs = self.default_bootargs + " " + self.suspend_crc_param
                result = self.reboot_opt.kernel_set_bootenv("bootargs_linux_only",
                                                            self.str_crc_bootargs)
                if result == 0:
                    #logger.print_info(f"kernel set bootargs: {self.str_crc_bootargs}")
                    result = self.reboot_opt.kernel_to_uboot()
                    if result == 0:
                        # check if changing bootargs ok
                        result, bootargs = self.reboot_opt.uboot_get_bootenv("bootargs_linux_only")
                        if result == 0 and self.suspend_crc_param in bootargs:
                            result = self.reboot_opt.uboot_to_kernel()
                        else:
                            # uboot get bootargs fail or set suspend_crc_param fail
                            result = 255
                    # else, boot to uboot fail
                # else, kernel set bootargs fail
        else:
            # kernel get bootargs fail, run to uboot
            result = self._uboot_set_suspend_crc()
        return result

    def set_crc_test_env(self):
        """set str_crc param in bootargs for test
        Args:
            None
        Returns:
            result (int): if set success, return 0; else, return 255
        """
        result = 255
        logger.print_warning("set str_crc param in bootargs for test ...")
        result = self.reboot_opt.check_uboot_phase()
        if result == 0:
            result = self._uboot_set_suspend_crc()
            if result != 0:
                logger.print_error("uboot set str_crc env fail")
        else:
            result = self.reboot_opt.check_kernel_phase()
            if result == 0:
                result = self._kernel_set_suspend_crc()
                if result != 0:
                    logger.print_error("kernel set str_crc env fail")
            else:
                logger.print_error("the device is not at kernel or at uboot")
                result = 255
        return result

    @logger.print_line_info
    def str_crc_test(self):
        """do str crc test.
        Args:
            None
        Returns:
            result (int): test success or fail
        """
        result = 255
        logger.print_warning("do str crc test ...")
        result = self.uart.write(self.cmd_str)

        while True:
            status, line = self.uart.read(1, 15)
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if str(STR_CRC_OK).strip() in line:
                    logger.print_warning("str crc check success")
                    result = 0
                    break
                if str(STR_CRC_FAIL).strip() in line:
                    logger.print_error("str crc check fail")
                    result = 255
                    break
            else:
                logger.print_error(f"read line fail after cmd:{self.cmd_str}")
                result = 255
                break
        return result

    def _uboot_remove_suspend_crc(self):
        result = 255
        bootargs = ""
        pattern = r"suspend_crc=[^ ]*"
        result, bootargs = self.reboot_opt.uboot_get_bootenv("bootargs_linux_only")
        if result == 0:
            if "suspend_crc" not in bootargs:
                logger.print_info("suspend_crc_param has not been set, no need to remove!")
            else:
                self.default_bootargs = re.sub(pattern, "", bootargs.strip())
                self.reboot_opt.uboot_set_bootenv("bootargs_linux_only", self.default_bootargs)
                logger.print_info(f"uboot set bootargs: {self.default_bootargs}")
                result = self.reboot_opt.uboot_to_uboot()
                if result == 0:
                    # check if changing bootargs ok
                    result, bootargs = self.reboot_opt.uboot_get_bootenv("bootargs_linux_only")
                    if result == 0:
                        if "suspend_crc" in bootargs:
                            result = 255

        result |= self.reboot_opt.uboot_to_kernel()
        return result

    def _kernel_remove_suspend_crc(self):
        result = 255
        bootargs = ""
        pattern = r"suspend_crc=[^ ]*"
        result, bootargs = self.reboot_opt.kernel_get_bootenv("bootargs_linux_only")
        if result == 0:
            if "suspend_crc" not in bootargs:
                logger.print_info("suspend_crc_param has not been set, no need to remove!")
            else:
                self.default_bootargs = re.sub(pattern, "", bootargs.strip())
                result = self.reboot_opt.kernel_set_bootenv("bootargs_linux_only",
                                                            self.default_bootargs)
                if result == 0:
                    logger.print_info(f"kernel set bootargs: {self.default_bootargs}")
                    result = self.reboot_opt.kernel_to_uboot()
                    if result == 0:
                        # check if changing bootargs ok
                        result, bootargs = self.reboot_opt.uboot_get_bootenv("bootargs_linux_only")
                        if result != 0 or "suspend_crc" in bootargs:
                            result = 255
            result |= self.reboot_opt.uboot_to_kernel()
        else:
            # kernel get bootargs fail, run to uboot
            result = self._uboot_remove_suspend_crc()
        return result

    def recovery_default_env(self):
        """recovery bootargs
        Args:
            None
        Returns:
            result (int): if recovery bootargs success, return 0; else, return 255
        """
        result = 255
        logger.print_warning("remove str_crc param in bootargs ...")
        result = self.reboot_opt.check_uboot_phase()
        if result == 0:
            result = self._uboot_remove_suspend_crc()
            if result != 0:
                logger.print_error("uboot remove str_crc env fail")
        else:
            result = self.reboot_opt.check_kernel_phase()
            if result == 0:
                result = self._kernel_remove_suspend_crc()
                if result != 0:
                    logger.print_error("kernel remove str_crc env fail")
            else:
                logger.print_error("the device is not at kernel or at uboot")
                result = 255
        return result

    def runcase(self):
        """test function body
        Args:
            None
        Returns:
            result (int): result of test
        """
        result = 255
        result = self.set_crc_test_env()

        self.uart.write("echo ==================================")
        if result == 0:
            result = self.str_crc_test()
        else:
            logger.print_error("str crc test fail")

        self.uart.write("echo ++++++++++++++++++++++++++++++++++")
        self.recovery_default_env()

        return result

    @logger.print_line_info
    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.print_warning("stat str crc test")
        logger.print_warning("cmd : echo 3 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
        logger.print_warning("cmd : echo mem > /sys/power/state")
        logger.print_warning("if the result return 'CRC check success', test pass; "
                             "if the result return 'CRC check fail', test fail.")
