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
    def _check_emac_ko_insmod_status(device: object):
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
                line = line.decode('utf-8', errors='replace')
            line = line.strip()
            if net_interface in line:
                logger.info("ko has insmoded already")
                result = True
        else:
            logger.error(f"read line fail, {line}")
            result = False
        return result

    @classmethod
    def _insmod_emac_ko(cls, device: object, koname):
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
        result = cls._check_emac_ko_insmod_status(device)
        if not result:
            logger.error(f"insmod {koname} fail")
        return result

    @classmethod
    def _rmmod_emac_ko(cls, device: object, koname):
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
        result = cls._check_emac_ko_insmod_status(device)
        if not result:
            logger.error(f"rmmod {koname} success")
        result = not result
        return result

    @staticmethod
    def _check_kernel_ifconfig_setting(device: object, check_ifconfig_setting):
        """
        Check board mac, ip, netmask setting.
        Args:
            device (object): device handle
            check_ifconfig_setting (dict): target mac, board ip, netmask
        Returns:
            result (bool): If the actual ifconfig setting is equal to target ifconfig setting,
            return True; Else, return False.
        """
        result = False
        net_interface = "eth0"
        read_line_cnt = 0
        check_result = {
            'check_mac': False,
            'check_board_ip': False,
            'check_netmask': False
        }

        # check mac, board_ip, mask
        device.write(f"ifconfig {net_interface};echo $?")
        while True:
            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "0" == line:
                    result = True
                    break
                for key in check_ifconfig_setting.keys():
                    if check_ifconfig_setting[key] in line:
                        check_result[key] = True
                        logger.info(f"{check_ifconfig_setting[key]}")
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                break

        result = all(check_result.values())
        return result

    @staticmethod
    def _check_kernel_route_setting(device: object, check_gateway_ip):
        """
        Check board gateway setting.
        Args:
            device (object): device handle
            check_gateway_ip (str): target gateway ip
        Returns:
            result (bool): If the actual gateway ip is equal to target gateway ip,
            return True; Else, return False.
        """
        result = False
        net_interface = "eth0"
        read_line_cnt = 0
        get_gw_str = ""

        device.write("route -n;echo $?")
        while True:
            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "0" == line:
                    result = True
                    break
                if net_interface in line and "UG" in line:
                    get_gw_str =  line.split()[1]
                    if get_gw_str == check_gateway_ip:
                        result = True
                        logger.info(f"{line}")
                    break
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                break

        return result

    @classmethod
    def _check_kenrel_network_setting(cls, device: object):
        """
        Check board kernel network setting.
        Args:
            device (object): device handle
        Returns:
            result (bool): If check ok, return True; Else, return False.
        """
        result = False
        check_str = {
            'check_mac': f"HWaddr {platform.PLATFORM_BOARD_MAC}",
            'check_board_ip': f"inet addr:{platform.PLATFORM_BOARD_IP}",
            'check_netmask': f"Mask:{platform.PLATFORM_MOUNT_NETMASK}"
        }

        # check mac, board_ip, mask
        result = cls._check_kernel_ifconfig_setting(device, check_str)

        # check gatewayip
        result |= cls._check_kernel_route_setting(device, platform.PLATFORM_MOUNT_GW)

        return result

    @classmethod
    def _setup_kernel_network(cls, device: object):
        """
        Set board kernel ip.
        Args:
            device (object): device handle
        Returns:
            result (bool): If set board ip success, return True; Else, return False.
        """
        result = False
        net_koname = "sstar_emac"
        if platform.PLATFORM_BOARD_MAC_TYPE == "gmac":
            net_koname = "sstar_gmac"
        # check if net ko has insmoded
        result = cls._check_emac_ko_insmod_status(device)
        if not result:
            # insmod net ko
            result = cls._insmod_emac_ko(device, net_koname)
            if not result:
                return result

        # set board ip
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

        # check set ok
        result = cls._check_kenrel_network_setting(device)

        return result

    @staticmethod
    def _setup_uboot_network(device: object):
        """
        Set board uboot ip.
        Args:
            device (object): device handle.
        Returns:
            result (bool): If set board ip success, return True; Else, return False.
        """
        result = False
        # set board ip
        set_ethaddr = f"set -f ethaddr  {platform.PLATFORM_BOARD_MAC};"
        set_gw = f"set -f gatewayip {platform.PLATFORM_MOUNT_GW};"
        set_ip = f"set -f ipaddr {platform.PLATFORM_BOARD_IP};"
        set_serverip = f"set -f serverip {platform.PLATFORM_SERVER_IP};"
        saveenv = "saveenv"
        pri = "pri"
        if platform.PLATFORM_BOARD_MAC_TYPE == "gmac":
            device.write("setenv ethact gmac0")
        device.write(set_ethaddr)
        device.write(set_gw)
        device.write(set_ip)
        device.write(set_serverip)
        device.write(saveenv)
        device.write(pri)

        # check set ok
        result = SysappRebootOpts.reboot_to_uboot(device)
        if result:
            result = (SysappRebootOpts.check_bootenv(device, "ethaddr",
                                                         platform.PLATFORM_BOARD_MAC)
                        and SysappRebootOpts.check_bootenv(device, "gatewayip",
                                                               platform.PLATFORM_MOUNT_GW)
                        and SysappRebootOpts.check_bootenv(device, "ipaddr",
                                                               platform.PLATFORM_BOARD_IP)
                        and SysappRebootOpts.check_bootenv(device, "serverip",
                                                               platform.PLATFORM_SERVER_IP))

        return result

    @classmethod
    def setup_network(cls, device: object):
        """
        Set board ip.
        Args:
            device (object): device handle.
        Returns:
            result (bool): If set board ip success, return True; Else, return False.
        """
        result = False
        if SysappRebootOpts.check_uboot_phase():
            result = cls._setup_uboot_network(device)
        elif SysappRebootOpts.check_kernel_phase():
            result = cls._setup_kernel_network(device)
        else:
            logger.error("the device is not at kernel or at uboot, read register fail")
        return result



    @staticmethod
    def mount_to_server(device: object, sub_path="") -> bool:
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
                logger.info(f"{data} cause {exce}")
                returncode = -1
            if result is True and returncode == 0:
                return True
            loopcnt += 1
        return False
