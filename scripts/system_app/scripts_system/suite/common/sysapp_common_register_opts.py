#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""register operations interfaces"""

import re
from suite.common.sysapp_common_logger import logger

class SysappRebootOpts():
    """A class representing reboot options
    Attributes:
        device (Device): device handle
        board_cur_state (str): board current state.
        reboot_timeout (int): reboot timeout setting
        enter_uboot_try_cnt (int): the count of pressing enter to jump to uboot
        get_state_try_cnt (int): the count of pressing enter to get current state of device
    """

    @staticmethod
    def read_register(device:object, bank, offset, is_kernel=True):
        """run cmd on server
        Args:
            device (): device handle
            bank (str): register bank address
            offset (str): register offset
            is_kernel (bool): if executed at kernel phase
        Returns:
            result (int): execute success, return 0; else, return 255
        """
        result = 255
        str_reg_value = ""
        read_line_cnt = 0
        max_read_lines = 10
        is_register_value_ready = 0
        cmd_read_register = ""
        if is_kernel:
            cmd_read_register = f"/customer/riu_r {bank} {offset}"
        else:
            cmd_read_register = f"riu_r {bank} {offset}"
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
                        result = 0
                        logger.print_info(f"bank:{bank} offset:{offset} "
                                        f"register value is {str_reg_value}")
                        break
            else:
                logger.print_error(f"read line:{read_line_cnt} fail")
                break
        return result, str_reg_value

    @staticmethod
    def get_bit_value(str_hex, position):
        """run cmd on server
        Args:
            str_hex (str): register value
            position (int): bit offset
        Returns:
            result (int): bit value, 0 or 1
        """
        num = int(str_hex, 16)
        bit = (num >> position) & 1
        return bit
