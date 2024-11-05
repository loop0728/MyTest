#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""device operations interfaces"""

import re
from suite.common.sysapp_common_types import SysappPackageType, SysappBootstrapType
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_register_opts import SysappRegisterOpts

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
                dev_name (str): name of device node;
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
                        dev_name = "mtd"+parts[0]
                        name = parts[1]
                        size = parts[2]
                        partition_list.append((dev_name, name, size))
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
                dev_name (str): name of device node;
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
                        dev_name = parts[0]
                        name = parts[3].replace('"', '')
                        size = "0x" + parts[1]
                        partition_list.append((dev_name, name, size))
                        #print(f"{line}, {parts[0]}, {parts[1]}, {parts[2]}, {parts[3]}, "
                        #      f"{len(parts)}")
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                break
        return result, partition_list

    @classmethod
    def _get_mtd_partitions(cls, device: object):
        """
        Get the partitions of mtd device.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get partitons success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                dev_name (str): name of device node;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []

        if device.check_uboot_phase():
            result, partition_list = cls._uboot_get_mtdparts(device)
        elif device.check_kernel_phase():
            result, partition_list = cls._kernel_get_mtdparts(device)
        else:
            logger.error("the device is not at kernel or at uboot, get mtd partitions fail")
        return result, partition_list

    @staticmethod
    def _uboot_get_emmc_boot_area_size(device: object):
        """
        Get the size of emmc boot area in uboot phase.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If find uboot area success, return True; Else, return False.
            - size (str): size of emmc boot area.
        """
        result = False
        size = 0
        read_line_cnt = 0
        cmd_emmc_info = "mmc info"

        result = device.write(cmd_emmc_info)
        if not result:
            logger.error("uboot get emmc boot area size fail")
            return result, size

        while True:
            if read_line_cnt > 20:
                logger.error("read lines exceed max_read_lines:20")
                break

            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "Boot Capacity:" in line:
                    match = re.search(r'(\d+) (\w+)', line)
                    if match:
                        val = int(match.group(1))
                        unit = match.group(2)
                        if unit == "KiB":
                            size = val * 1024
                        elif unit == "MiB":
                            size = val * 1024 * 1024
                        else:
                            size = 0
                        result = True
                        break
        return result, size

    @classmethod
    def _uboot_get_emmc_parts(cls, device: object):
        """
        Get the partitions of emmc device in uboot phase.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get partitions success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                dev_name (str): name of device node;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []
        read_line_cnt = 0
        uboot_prompt  = 'SigmaStar #'
        cmd_emmc_user_part = "mmc part"

        result, size = cls._uboot_get_emmc_boot_area_size(device)
        if result:
            partition_list.append("mmcblk0boot0", "boot0", hex(size))
            partition_list.append("mmcblk0boot1", "boot1", hex(size))
        else:
            return result, partition_list

        result = device.write(cmd_emmc_user_part)
        if not result:
            logger.error("uboot get emmc user part fail")
            return result, partition_list

        while True:
            if read_line_cnt > 25:
                logger.error("read lines exceed max_read_lines:25")
                break

            status, line = device.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if uboot_prompt in line:
                    result = True
                    break

                if "U-Boot" in line:
                    fields = line.split()
                    if len(fields) > 4:
                        dev_name = "mmcblk0p" + fields[2]
                        name = fields[1]
                        size = int(fields[3]) * 512
                        partition_list.append((dev_name, name, hex(size)))
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                break
        return result, partition_list

    @staticmethod
    def _kernel_get_dev_num(device: object, dev_type):
        """
        Get the number of devices in kernel phase.
        Args:
            device (object): device handle
            dev_type: device type
        Returns:
            dev_cnt (int): the number of devices
        """
        dev_cnt = 0
        cmd_get_dev_cnt = f"ls /dev/{dev_type} | wc -l"
        result = device.write(cmd_get_dev_cnt)
        if not result:
            logger.error(f"execute cmd:{cmd_get_dev_cnt} fail")
            return dev_cnt

        result, data = device.read()
        if result:
            dev_cnt = int(data)
        return dev_cnt

    @staticmethod
    def _kernel_get_emmc_part_size(device: object, dev_name):
        """
        Get the number of devices in kernel phase.
        Args:
            device (object): device handle
            dev_name: device node
        Returns:
            tuple:
            - result (bool): If find uboot area success, return True; Else, return False.
            - size (str): size of emmc boot area.
        """
        result = False
        size = 0
        cmd_get_part_size = f"cat /sys/block/{dev_name}/size"
        result = device.write(cmd_get_part_size)
        if result:
            result, line = device.read()
            if result:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "No such file or directory" in line:
                    result = False
                else:
                    size = int(line) * 512
        return result, size

    @staticmethod
    def _kernel_get_emmc_part_name(device: object, dev_name):
        """
        Get the number of devices in kernel phase.
        Args:
            device (object): device handle
            dev_name: device node
        Returns:
            tuple:
            - result (bool): If find uboot area success, return True; Else, return False.
            - size (str): size of emmc boot area.
        """
        result = False
        part_name = ""
        part_offset = 0
        read_line_cnt = 2
        emmc_part_into = {
            "index": 0,
            "section_offset": 512,
            "name_offset": 16,
            "name_size": 32
        }

        if dev_name == "mmcblk0boot0":
            part_name = "boot0"
            result = True
        elif dev_name == "mmcblk0boot1":
            part_name = "boot1"
            result = True
        elif "mmcblk0p" in dev_name:
            index = int(dev_name.replace("mmcblk0p", ""))
            part_offset = emmc_part_into['section_offset'] * index + emmc_part_into['name_offset']
            cmd_get_emmc_user_part_name = (f"hexdump -C -s {part_offset}"
                                           f" -n {emmc_part_into['name_size']} "
                                           "/dev/mmcblk0")
            result = device.write(cmd_get_emmc_user_part_name)
            if result:
                while read_line_cnt > 0:
                    result, data = device.read()
                    if result:
                        fields = data.split('|')
                        part_name += fields[1].strip('.')
                    read_line_cnt -= 1
        else:
            logger.error(f"invaild dev name:{dev_name}")

        return result, part_name


    @classmethod
    def _kernel_get_emmc_parts(cls, device: object):
        """
        Get the partitions of emmc device in kernel phase.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get partitions success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                dev_name (str): name of device node;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = True
        partition_list = []
        boot_area_cnt = cls._kernel_get_dev_num(device, "mmcblk0boot*")
        for i in range(boot_area_cnt):
            dev_name = "mmcblk0boot" + str(i)
            ret_get_name, name = cls._kernel_get_emmc_part_name(device, dev_name)
            ret_get_size, size = cls._kernel_get_emmc_part_size(device, dev_name)
            if ret_get_name and ret_get_size:
                partition_list.append((dev_name, name, hex(size)))
            else:
                logger.error("kernel get emmc boot partiton fail")
                result = False
                break

        user_area_cnt = cls._kernel_get_dev_num(device, "mmcblk0p*")
        for i in range(user_area_cnt):
            dev_name = "mmcblk0p" + str(i+1)
            ret_get_name, name = cls._kernel_get_emmc_part_name(device, dev_name)
            ret_get_size, size = cls._kernel_get_emmc_part_size(device, f"mmcblk0/{dev_name}")
            if ret_get_name and ret_get_size:
                partition_list.append((dev_name, name, hex(size)))
            else:
                logger.error("kernel get emmc user partiton fail")
                result = False
                break

        return result, partition_list

    @classmethod
    def _get_emmc_partitions(cls, device: object):
        """
        Get the partitions of emmc device.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get partitions success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                dev_name (str): name of device node;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []

        if device.check_uboot_phase():
            result, partition_list = cls._uboot_get_emmc_parts(device)
        elif device.check_kernel_phase():
            result, partition_list = cls._kernel_get_emmc_parts(device)
        else:
            logger.error("the device is not at kernel or at uboot, get emmc partitons fail")
        return result, partition_list

    @classmethod
    def get_partition_list(cls, device: object):
        """
        Get the partitions of device.
        Args:
            device (): device handle
        Returns:
            tuple:
            - result (bool): If get mtdparts success, return True; Else, return False.
            - partition_list (list of tuple): return the partition list of device.
                dev_name (str): name of device node;
                name (str): name of partition;
                size (str): size of partition.
        """
        result = False
        partition_list = []
        bootstrap_type = cls.get_bootstrap_type(device)

        if (bootstrap_type == SysappBootstrapType.BOOTSTRAP_TYPE_NOR
            or bootstrap_type == SysappBootstrapType.BOOTSTRAP_TYPE_NAND):
            result, partition_list = cls._get_mtd_partitions(device)
        elif bootstrap_type == SysappBootstrapType.BOOTSTRAP_TYPE_EMMC:
            result, partition_list = cls._get_emmc_partitions(device)
        else:
            logger.error("the device is not at kernel or at uboot, read register fail")
        return result, partition_list

    @staticmethod
    def is_trimed_ic(device: object):
        """
        Check if the chip has been trimed.
        Args:
            device (): device handle
        Returns:
            result (bool): If the chip has been trimed, return True; Else, return False.
        """
        result = False

        result, str_reg_value = SysappRegisterOpts.read_register(device, "e", "64")
        if result:
            reg_value = int(str_reg_value, 16)
            if (reg_value & 0x7E) != 0:
                result = True

        return result
