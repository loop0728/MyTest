#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""register operations interfaces"""

import re
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts

class SysappRegisterOpts():
    """
    A class representing reboot options
    Attributes:
        None:
    """

    @staticmethod
    def read_register(device:object, bank, offset):
        """
        Get the value of the specified register.
        Args:
            device (): device handle
            bank (str): register bank address
            offset (str): register offset
        Returns:
            tuple:
            - result (bool): If get value success, return True; Else, return False.
            - str_reg_value (str): If get value success, return the actual value; Else if fw tool
            exists, return ""; Else, return None.
        """
        result = False
        str_reg_value = ""
        read_line_cnt = 0
        max_read_lines = 10
        is_register_value_ready = 0
        cmd_read_register = ""

        if SysappRebootOpts.check_uboot_phase():
            cmd_read_register = f"riu_r {bank} {offset}"
        elif SysappRebootOpts.check_kernel_phase():
            cmd_read_register = f"/customer/riu_r {bank} {offset}"
        else:
            logger.print_error("the device is not at kernel or at uboot, read register fail")
            return False

        device.write(cmd_read_register)

        while True:
            if read_line_cnt > max_read_lines:
                logger.print_error(f"read lines exceed max_read_lines:{max_read_lines}")
                break

            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "BANK" in line:
                    is_register_value_ready = 1
                    continue

                if is_register_value_ready == 1 :
                    pattern = re.compile(r'0x([A-Fa-f0-9]{4})')
                    match = pattern.search(line)
                    if match:
                        str_reg_value = match.group(0)
                        result = True
                        logger.print_info(f"bank:{bank} offset:{offset} "
                                        f"register value is {str_reg_value}")
                        break
            else:
                logger.print_error(f"read line:{read_line_cnt} fail")
                break
        return result, str_reg_value

    @staticmethod
    def write_register(device:object, bank, offset, value):
        """
        Set the value to the specified register.
        Args:
            device (): device handle
            bank (str): register bank address
            offset (str): register offset
            value (str): register value
        Returns:
            result (bool): If execute success, return True; else, return False
        """
        result = False
        str_reg_value = ""
        cmd_write_register = ""

        if SysappRebootOpts.check_uboot_phase():
            cmd_write_register = f"riu_w {bank} {offset} {value}"
        elif SysappRebootOpts.check_kernel_phase():
            cmd_write_register = f"/customer/riu_w {bank} {offset} {value}"
        else:
            logger.print_error("the device is not at kernel or uboot, read register fail")
            return False

        device.write(cmd_write_register)

        result, str_reg_value = SysappRegisterOpts.read_register(device, bank, offset)

        if result:
            if not value.startswith("0x"):
                value = "0x" + value
            if int(value, 16) != int(str_reg_value, 16):
                result = False

        return result

    @staticmethod
    def get_bit_value(str_hex, position):
        """
        Get the value of the specified bit.
        Args:
            str_hex (str): register value
            position (int): bit offset
        Returns:
            bit (int): Return the value of the specified bit, 0 or 1.
        """
        num = int(str_hex, 16)
        bit = (num >> position) & 1
        return bit
