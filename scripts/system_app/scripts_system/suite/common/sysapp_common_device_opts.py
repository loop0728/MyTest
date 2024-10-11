#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""device operations interfaces"""

import re
from suite.common.sysapp_common_types import SysappPackageType, SysappBootstrapType
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_register_opts import SysappRegisterOpts
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts

class SysappDeviceOpts():
    """
    A class representing device options
    Attributes:
        None:
    """

    @staticmethod
    def get_package_type(device: object):
        """
        Get the package type of chip.
        Args:
            device (): device handle
        Returns:
            (SysappPackageType): return the package type of chip
        """
        result = False
        package_type = SysappPackageType.PACKAGE_TYPE_MAX
        result, str_reg_value = SysappRegisterOpts.read_register(device, "101e", "48")
        if result:
            bit4 = SysappRegisterOpts.get_bit_value(str_reg_value, 4)
            bit5 = SysappRegisterOpts.get_bit_value(str_reg_value, 5)
            if bit4 == 0 and bit5 == 0:
                package_type = SysappPackageType.PACKAGE_TYPE_QFN128
            elif bit4 == 0 and bit5 == 1:
                package_type = SysappPackageType.PACKAGE_TYPE_BGA12
            else:
                package_type = SysappPackageType.PACKAGE_TYPE_BGA11

        #logger.warning(f"The package type is {package_type.name}")
        return package_type

    @staticmethod
    def get_bootstrap_type(device: object):
        """
        Get the bootstrap type of device.
        Args:
            device (): device handle
        Returns:
            bootstrap_type (SysappBootstrapType): return the bootstrap type of device
        """
        result = False
        bootstrap_type = SysappBootstrapType.BOOTSTRAP_TYPE_MAX
        result, str_reg_value = SysappRegisterOpts.read_register(device, "38", "70")
        if result:
            nor_flag = (SysappRegisterOpts.get_bit_value(str_reg_value, 1) |
                        SysappRegisterOpts.get_bit_value(str_reg_value, 5))
            nand_flag = (SysappRegisterOpts.get_bit_value(str_reg_value, 2) |
                        SysappRegisterOpts.get_bit_value(str_reg_value, 4))
            emmc_flag = SysappRegisterOpts.get_bit_value(str_reg_value, 3)

            if nor_flag == 1:
                bootstrap_type = SysappBootstrapType.BOOTSTRAP_TYPE_NOR
            elif nand_flag == 1:
                bootstrap_type = SysappBootstrapType.BOOTSTRAP_TYPE_NAND
            elif emmc_flag == 1:
                bootstrap_type = SysappBootstrapType.BOOTSTRAP_TYPE_EMMC

        #logger.warning(f"The bootstrap type is {bootstrap_type.name}")
        return bootstrap_type

    @staticmethod
    def _uboot_get_mtdparts(device: object):
        """
        Get the partitions of device in uboot phase.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get mtdparts success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                index (str): index of partition;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []
        read_line_cnt = 0
        cmd_get_mtdparts = "mtdparts"

        device.write(cmd_get_mtdparts)

        while True:
            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "active partition:" in line:
                    result = True
                    break

                pattern = re.compile(r'\d+:\s*')
                match = pattern.search(line)
                if match:
                    parts = re.split(r'\s*:\s*|\s+', line)
                    if len(parts) >= 5:
                        index = parts[0]
                        name = parts[1]
                        size = parts[2]
                        partition_list.append((index, name, size))
                        #print(f"{line}, {parts[0]}, {parts[1]}, {parts[2]}, {parts[3]}, "
                        #      f"{parts[4]}, {len(parts)}")
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                break
        return result, partition_list

    @staticmethod
    def _kernel_get_mtdparts(device: object):
        """
        Get the partitions of device in kernel phase.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get mtdparts success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                index (str): index of partition;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []
        read_line_cnt = 0
        cmd_get_mtdparts = "cat /proc/mtd;echo $?"

        device.write(cmd_get_mtdparts)

        while True:
            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if line == "0":
                    result = True
                    break

                pattern = re.compile(r'\d+:\s*')
                match = pattern.search(line)
                if match:
                    parts = re.split(r'\s*:\s*|\s+', line)
                    if len(parts) >= 4:
                        index = parts[0].replace("mtd", "")
                        name = parts[3].replace('"', '')
                        size = parts[1]
                        partition_list.append((index, name, size))
                        #print(f"{line}, {parts[0]}, {parts[1]}, {parts[2]}, {parts[3]}, "
                        #      f"{len(parts)}")
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                break
        return result, partition_list

    @staticmethod
    def get_mtdparts(device: object):
        """
        Get the partitions of device.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get mtdparts success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                index (str): index of partition;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []

        if SysappRebootOpts.check_uboot_phase():
            result, partition_list = SysappDeviceOpts._uboot_get_mtdparts(device)
        elif SysappRebootOpts.check_kernel_phase():
            result, partition_list = SysappDeviceOpts._kernel_get_mtdparts(device)
        else:
            logger.error("the device is not at kernel or at uboot, read register fail")
        return result, partition_list
