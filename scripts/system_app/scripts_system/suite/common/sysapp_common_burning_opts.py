#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""burning interfaces"""

from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from sysapp_client import SysappClient as Client
import sysapp_platform as platform

class SysappBurningOpts():
    """ Burning image """
    __uboot_prompt  = 'SigmaStar #'
    __kernel_prompt = '/ #'

    @classmethod
    def check_uboot_env(cls, device: object):
        """
        Check uboot env for burning image.

        Args:
            bool: result
        """
        pri = "pri"
        pri_data = ""
        device.write(pri)
        while True:
            ret, data = device.read()
            if ret is True and cls.__uboot_prompt in data:
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
            device.write(ping_server_cmd)
            while True:
                ret, data = device.read(wait_timeout=30)
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

    @classmethod
    def setenv_in_uboot(cls, device: object):
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
        device.write(set_ethaddr)
        device.write(set_gw)
        device.write(set_ip)
        device.write(set_serverip)
        device.write(saveenv)
        result = cls.check_uboot_env(device)
        return result

    @classmethod
    def burning_image_for_tftp(cls, device=''):
        """
        Burning image.

        Return:
            int: result
        """
        result = False
        if device == '':
            device = Client("Burning_image", "uart", "uart")
        # step1 go uboot
        ret = SysappRebootOpts.cold_reboot_to_uboot(device)
        if ret is False:
            logger.error("Reboot to uboot fail.")
            return result
        # step2 set uboot net
        ret = cls.setenv_in_uboot(device)
        if ret is False:
            logger.error("Failed in uboot setenv.")
            return result
        # step3 get image path
        image_path = platform.PLATFORM_IMAGE_PATH
        # step4 estar
        estar_cmd = f"estar {image_path}"
        device.write(estar_cmd)
        # step5 result judgment
        while True:
            ret, data = device.read(wait_timeout=10)
            if ret is True and cls.__kernel_prompt in data:
                logger.info("Estar success.")
                result = True
                break
            if ret is False:
                logger.error("Estar failed.")
                result = False
                break

        return result

    @staticmethod
    def burning_uboot_for_isp_tool():
        """Burning uboot."""
        pass
