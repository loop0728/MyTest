#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""net operations interfaces"""

import time
import sysapp_platform as platform
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts

class SysappNetOpts():
    """
    A class representing network options
    Attributes:
        device (Device): device handle
        board_cur_state (str): board current state.
        reboot_timeout (int): reboot timeout setting
        enter_uboot_try_cnt (int): the count of pressing enter to jump to uboot
        get_state_try_cnt (int): the count of pressing enter to get current state of device
    """

    @staticmethod
    def check_emac_ko_insmod_status(device:object):
        """
        Check if net ko insmod
        Args:
            device (): device handle
        Returns:
            result (bool): if net ko has insmoded, return True; else, return False.
        """
        result = False
        net_interface = "eth0"
        cmd_check_insmod_status = f"ifconfig -a | grep {net_interface};echo $?"
        device.write(cmd_check_insmod_status)
        status, line = device.read(1, 30)
        if status:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if net_interface in line:
                logger.print_info("ko has insmoded already")
                result = True
        else:
            logger.print_error(f"read line fail, {line}")
            result = False
        return result

    @staticmethod
    def insmod_emac_ko(device:object, koname):
        """
        Insmod net ko.
        Args:
            device (): device handle
            koname (str): the name of net ko
        Returns:
            result (bool): if net ko insmods success, return True; else, return False
        """
        result = False
        cmd_insmod_emac_ko = f"insmod /config/modules/5.10/{koname}.ko"
        device.write(cmd_insmod_emac_ko)
        result = SysappNetOpts.check_emac_ko_insmod_status(device)
        if not result:
            logger.print_error(f"insmod {koname} fail")
        return result

    @staticmethod
    def rmmod_emac_ko(device:object, koname):
        """
        Remove net ko.
        Args:
            device (): device handle
            koname (str): the name of net ko
        Returns:
            result (bool): if net ko removes success, return True; else, return False
        """
        result = False
        cmd_rmmod_emac_ko = f"rmmod {koname}"
        device.write(cmd_rmmod_emac_ko)
        result = SysappNetOpts.check_emac_ko_insmod_status(device)
        if not result:
            logger.print_error(f"rmmod {koname} success")
        result = not result
        return result

    @staticmethod
    def set_board_kernel_ip(device:object) -> None:
        """
        Set board kernel ip.

        Args:
            uart (class): only support uart.

        Returns:
            bool: result
        """
        set_mac = f"ifconfig eth0 hw ether {platform.PLATFORM_BOARD_MAC};"
        eth0_up = "ifconfig eth0 up;"
        set_lo = "ifconfig lo 127.0.0.1;"
        set_ip = (f"ifconfig eth0 {platform.PLATFORM_BOARD_IP} "
                f"netmask {platform.PLATFORM_MOUNT_NETMASK};")
        set_gw = f"route add default gw {platform.PLATFORM_MOUNT_GW};"
        device.write(set_mac)
        device.write(eth0_up)
        device.write(set_lo)
        device.write(set_ip)
        device.write(set_gw)

    @staticmethod
    def set_board_uboot_ip(device:object) -> None:
        """
        Set board uboot ip.

        Args:
            uart (class): only support uart.

        Returns:
            bool: result
        """
        set_ethaddr = f"set -f ethaddr  {platform.PLATFORM_BOARD_MAC};"
        set_gw = f"set -f gatewayip {platform.PLATFORM_MOUNT_GW};"
        set_ip = f"set -f ipaddr {platform.PLATFORM_BOARD_IP};"
        set_serverip = f"set -f serverip {platform.PLATFORM_SERVER_IP};"
        saveenv = "saveenv"
        pri = "pri"
        device.write(set_ethaddr)
        device.write(set_gw)
        device.write(set_ip)
        device.write(set_serverip)
        device.write(saveenv)
        device.write(pri)

    @staticmethod
    def mount_to_server(device:object, sub_path="") -> bool:
        """
        mount to server path

        Args:
            device_handle (class): device

        Returns:
            bool: result
        """
        umount_cmd = "umount /mnt/"
        mount_cmd = (f"mount -t nfs -o nolock {platform.PLATFORM_MOUNT_IP}:"
                    f"{platform.PLATFORM_MOUNT_PATH}/{sub_path} /mnt/")
        check_cmd = "echo $?"
        returnvalue = 255
        returncode = 0
        loopcnt = 0
        device.write(umount_cmd)
        time.sleep(1)
        while returnvalue == 255 and loopcnt <= 4:
            if returncode != -1:
                device.write(mount_cmd)
            time.sleep(5)
            device.write(check_cmd)
            result, data = device.read()
            try:
                returncode = int(data)
            except Exception as exce:
                logger.print_info(f"{data} cause {exce}")
                returncode = -1
            if result is True and returncode == 0:
                return True
            loopcnt += 1
        return False
