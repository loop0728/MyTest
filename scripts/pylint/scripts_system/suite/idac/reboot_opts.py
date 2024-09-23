#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""reboot interfaces"""

import time
from python_scripts.logger import logger

class RebootOpts():
    """A class representing reboot options
    Attributes:
        device (Device): device handle
        borad_cur_state (str): board current state.
        reboot_timeout (int): reboot timeout setting
    """
    def __init__(self, device, timeout=30):
        """Class constructor.
        Args:
            device (Device): device handle
            timeout (int): reboot timeout
        Returns:
            None
        """
        self.device = device
        self.borad_cur_state = ''
        self.reboot_timeout = timeout

    def get_cur_boot_state(self):
        """get current status of the device
        Args:
            None
        Returns:
            result (int): if the device is at kernel or at uboot, return 0; else return 255
        """
        result = 255
        self.device.write('')
        self.borad_cur_state = self.device.get_borad_cur_state()[1]
        if self.borad_cur_state != 'Unknow':
            result = 0
        else:
            i = 1
            while i < 20:
                self.device.write('')
                self.borad_cur_state = self.device.get_borad_cur_state()[1]
                if self.borad_cur_state != 'Unknow':
                    result = 0
                    break
                time.sleep(1)

        if self.borad_cur_state == 'Unknow':
            logger.print_error("dev is not at kernel or at uboot")
        return result

    def check_kernel_env(self):
        """check current status of the dev, if the dev is not at kernel, then reboot the dev
        Args:
            None
        Returns:
            result (int): if device go to kernel success, return 0; else, return 255
        """
        trywait_time = 0
        result = 255
        self.device.write('')
        self.borad_cur_state = self.device.get_borad_cur_state()[1]
        if self.borad_cur_state == 'Unknow':
            i = 1
            while i < 20:
                self.device.write('')
                self.borad_cur_state = self.device.get_borad_cur_state()[1]
                if self.borad_cur_state != 'Unknow':
                    break
                time.sleep(1)

        if self.borad_cur_state == 'Unknow':
            logger.print_error("dev enter to kernel fail")
            return result

        if self.borad_cur_state == 'at uboot':
            self.device.clear_borad_cur_state()
            self.device.write('reset')
            logger.print_info(f"borad_cur_state:{self.borad_cur_state}, do reset")

        while True:
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                result = 0
                logger.print_info(f"borad_cur_state:{self.borad_cur_state}")
                break
            else:
                time.sleep(1)
                trywait_time = trywait_time + 1
                if trywait_time > self.reboot_timeout:
                    logger.print_error("dev reset to kernel timeout")
                    break
        return result

    def kernel_to_uboot(self):
        """reboot device from kernel to uboot
        Args:
            None
        Returns:
            result (int): if device go to uboot success, return 0; else, return 255
        """
        result = 255
        try_time = 0
        logger.print_info('begin to run kernel_to_uboot')
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        logger.print_info(f'cur_state: {self.borad_cur_state}')
        if self.borad_cur_state != 'at kernel':
            logger.print_error(f"dev is not at kernel now, cur_state:{self.borad_cur_state}")
            result = 255
            return result

        self.device.write('reboot -f')
        time.sleep(2)
        self.device.clear_borad_cur_state()

        #logger.print_info("begin to read keyword")
        # wait uboot keyword
        while True:
            status, line = self.device.read(1, 10)
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                result = 255
                return result

        # enter to uboot
        while True:
            if try_time >= self.reboot_timeout:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at uboot':
                logger.print_info("enter to uboot success")
                result = 0
                break
            elif self.borad_cur_state == 'at kernel':
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result

    def uboot_to_kernel(self):
        """reboot device from uboot to kernel
        Args:
            None
        Returns:
            result (int): if device go to kernel success, return 0; else, return 255
        """
        result = 255
        try_time = 0
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        if self.borad_cur_state != 'at uboot':
            logger.print_error("dev is not at uboot now")
            result = 255
            return result

        self.device.write('reset')
        self.device.clear_borad_cur_state()

        while True:
            if try_time >= self.reboot_timeout:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                logger.print_info("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def kernel_to_kernel(self):
        """reboot device from kernel to kernel
        Args:
            None
        Returns:
            result (int): if device go to kernel success, return 0; else, return 255
        """
        result = 255
        try_time = 0
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        if self.borad_cur_state != 'at kernel':
            logger.print_error("dev is not at kernel now")
            result = 255
            return result

        self.device.write('reboot -f')
        time.sleep(2)
        self.device.clear_borad_cur_state()

        while True:
            if try_time >= self.reboot_timeout:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                logger.print_info("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def uboot_to_uboot(self):
        """reboot device from uboot to uboot
        Args:
            None
        Returns:
            result (int): if device go to uboot success, return 0; else, return 255
        """
        result = 255
        try_time = 0
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        if self.borad_cur_state != 'at uboot':
            logger.print_error("dev is not at uboot now")
            result = 255
            return result

        self.device.write('reset')
        self.device.clear_borad_cur_state()

        # wait uboot keyword
        while True:
            status, line = self.device.read()
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                result = 255
                return result

        # enter to uboot
        while True:
            if try_time >= self.reboot_timeout:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at uboot':
                logger.print_info("enter to uboot success")
                result = 0
                break
            elif self.borad_cur_state == 'at kernel':
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result
