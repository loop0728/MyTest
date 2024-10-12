#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""burning interfaces"""

from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
import sysapp_platform as platform

class SysappBurning():
    """ Burning image """
    def __init__(self, uart):
        """ Burning image.
        Args:
           uart: device uart handle
        """
        self.uart = uart
        self.reboot_opts = SysappRebootOpts()
        self.uboot_prompt = 'SigmaStar #'
        self.kernel_prompt = '/ #'

    def check_uboot_env(self):
        """
        Check uboot env for burning image.

        Args:
            bool: result
        """
        pri = "pri"
        pri_data = ""
        self.uart.write(pri)
        while True:
            ret, data = self.uart.read()
            if ret is True and self.uboot_prompt in data:
                break
            if ret is False:
                logger.error("Uboot prientenv failed.")
                break
            pri_data += data

        if platform.PLATFORM_BOARD_MAC not in pri_data:
            return False
        if platform.PLATFORM_MOUNT_GW not in pri_data:
            return False
        if platform.PLATFORM_BOARD_IP not in pri_data:
            return False
        if platform.PLATFORM_SERVER_IP not in pri_data:
            return False

        ping_server_cmd = f"ping {platform.PLATFORM_SERVER_IP}"
        host_is_alive = "is alive"
        host_is_not_alive = "is not alive"
        try_cnt = 3
        while try_cnt:
            self.uart.write(ping_server_cmd)
            while True:
                ret, data = self.uart.read(wait_timeout=30)
                if ret is True and host_is_alive in data:
                    logger.info("Setenv success in uboot.")
                    return True
                if ret is True and host_is_not_alive in data:
                    logger.warning(f"Uboot ping server {platform.PLATFORM_SERVER_IP} failed.")
                    try_cnt -= 1
                    break
                if ret is False:
                    logger.warning("Uboot ping read failed")
                    try_cnt -= 1
                    break
        return False

    def setenv_in_uboot(self):
        """
        Set env in uboot.

        Returns:
            bool: result
        """
        result = False
        set_ethaddr = f"set -f ethaddr {platform.PLATFORM_BOARD_MAC};"
        set_gw = f"set -f gatewayip {platform.PLATFORM_MOUNT_GW};"
        set_ip = f"set -f ipaddr {platform.PLATFORM_BOARD_IP};"
        set_serverip = f"set -f serverip {platform.PLATFORM_SERVER_IP};"
        saveenv = "saveenv"
        self.uart.write(set_ethaddr)
        self.uart.write(set_gw)
        self.uart.write(set_ip)
        self.uart.write(set_serverip)
        self.uart.write(saveenv)
        result = self.check_uboot_env()
        return result

    def burning_image_for_tftp(self):
        """
        Burning image.
        Args:

        Return:
            int: result
        """
        result = False
        # step1 go uboot
        ret = self.reboot_opts.cold_reboot_to_uboot(self.uart)
        if ret is False:
            logger.error("Reboot to uboot fail.")
            return result
        # step2 set uboot net
        ret = self.setenv_in_uboot()
        if ret is False:
            logger.error("Failed in uboot setenv.")
            return result
        # step3 get image path
        image_path = platform.PLATFORM_IMAGE_PATH
        # step4 estar
        estar_cmd = f"estar {image_path}"
        self.uart.write(estar_cmd)
        # step5 result judgment
        while True:
            ret, data = self.uart.read(wait_timeout=10)
            if ret is True and self.kernel_prompt in data:
                logger.info("Estar success.")
                result = True
                break
            if ret is False:
                logger.error("Estar failed.")
                result = False
                break

        return result

    def burning_uboot_for_isp_tool(self):
        """Burning uboot."""
        pass
