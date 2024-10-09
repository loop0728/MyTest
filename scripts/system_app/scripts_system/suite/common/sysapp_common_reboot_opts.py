#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""reboot interfaces"""

import time
from suite.common.sysapp_common_logger import logger
import sysapp_platform as platform
from device.sysapp_dev_base import BootStage
from device.sysapp_dev_relay import SysappDevRelay

class SysappRebootOpts():
    """
    A class representing reboot options
    Attributes:
        __uboot_prompt (str): the prompt of uboot phase
        __kernel_prompt (str): the prompt of kernel phase
        __board_cur_state (str): board current state.
        __reboot_timeout (int): reboot timeout setting
        __enter_uboot_try_cnt (int): the count of pressing enter to jump to uboot
        __get_state_try_cnt (int): the count of pressing enter to get current state of device
    """
    __uboot_prompt  = 'SigmaStar #'
    __kernel_prompt = '/ #'
    __reboot_timeout = 30
    __enter_uboot_try_cnt = 30
    __get_state_try_cnt = 20
    __board_cur_state = BootStage.E_BOOTSTAGE_UNKNOWN.name

    @classmethod
    def _get_cur_boot_state(cls, device:object):
        """
        Get current status of the device.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device is at kernel or at uboot, return True; Else, return False;
        """
        result = False
        device.write('')
        cls.__board_cur_state = device.get_board_cur_state()[1]
        if cls.__board_cur_state != BootStage.E_BOOTSTAGE_UNKNOWN.name:
            result = True
        else:
            i = 1
            while i < cls.__get_state_try_cnt:
                device.write('')
                cls.__board_cur_state = device.get_board_cur_state()[1]
                if cls.__board_cur_state != BootStage.E_BOOTSTAGE_UNKNOWN.name:
                    result = True
                    break
                time.sleep(1)

        if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UNKNOWN.name:
            logger.print_error("dev is not at kernel or at uboot")
        return result

    @classmethod
    def _enter_to_uboot(cls, device:object):
        """
        Enter to uboot.
        Args:
            device (object): Client handle.
        Returns:
            result (bool): If run success, return True; Else, return False.
        """
        result = False
        try_time = 0
        # wait uboot keyword
        while True:
            status, line = device.read()
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                result = False
                return result

        # enter to uboot
        while True:
            if try_time >= cls.__enter_uboot_try_cnt:
                logger.print_error("enter to uboot timeout")
                result = False
                break
            device.write('')
            cls.__board_cur_state = device.get_board_cur_state()[1]
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                logger.print_info("enter to uboot success")
                result = True
                break
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                logger.print_error(f"enter to uboot fail, current state:{cls.__board_cur_state}")
                result = False
                break
            try_time += 1
            time.sleep(0.1)
        return result

    @classmethod
    def _enter_to_kernel(cls, device:object):
        """
        Enter to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If run success, return True; Else, return False.
        """
        result = False
        try_time = 0
        # enter to kernel
        while True:
            if try_time >= cls.__reboot_timeout:
                logger.print_error("enter to kernel timeout")
                result = False
                break
            cls.__board_cur_state = device.get_board_cur_state()[1]
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                logger.print_info("enter to kernel success")
                result = True
                break
            try_time += 1
            time.sleep(1)
        return result

    @classmethod
    def _kernel_to_uboot(cls, device:object):
        """
        Reboot the device from kernel to uboot.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to uboot success, return True; Else, return False.
        """
        result = False
        logger.print_info('begin to run _kernel_to_uboot')
        device.write('reboot -f')
        #time.sleep(2)
        device.clear_board_cur_state()

        result = cls._enter_to_uboot(device)
        return result

    @classmethod
    def _uboot_to_kernel(cls, device:object):
        """
        Reboot the device from uboot to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to kernel success, return True; Else, return False.
        """
        result = False
        logger.print_info('begin to run _uboot_to_kernel')
        device.write('reset')
        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        return result

    @classmethod
    def _kernel_to_kernel(cls, device:object):
        """
        Reboot the device from kernel to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to kernel success, return True; Else, return False.
        """
        result = False
        logger.print_info('begin to run _kernel_to_kernel')
        device.write('reboot -f')
        #time.sleep(2)
        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        return result

    @classmethod
    def _uboot_to_uboot(cls, device:object):
        """
        Reboot the device from uboot to uboot.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to uboot success, return True; Else, return False.
        """
        result = False
        logger.print_info('begin to run _uboot_to_uboot')
        device.write('reset')
        device.clear_board_cur_state()

        result = cls._enter_to_uboot(device)
        return result

    @staticmethod
    def _cold_reboot():
        """
        Power off the device and then power on.
        Args:
            None:
        Returns:
            None:
        """
        relay_name = platform.PLATFORM_RELAY
        relay_no = platform.PLATFORM_RELAY_PORT
        rs232_contrl_handle = SysappDevRelay(relay=relay_no, port=relay_name)
        logger.print_info(f"init rs232_contrl_handle {relay_name}:{relay_no}")
        rs232_contrl_handle.connect()
        rs232_contrl_handle.power_off()
        time.sleep(2)
        rs232_contrl_handle.power_on()
        rs232_contrl_handle.disconnect()
        logger.print_info("closed rs232_contrl_handle.")

    @classmethod
    def _get_key_value(cls, device:object, key):
        """
        Get the value of key.
        Args:
            device (object): Client instance.
            key (str): key's name.
        Returns:
            tuple:
            - result (bool): If the key exists, return True; Else, return False.
            - val (str): If the key is unset, return ""; Else, return the actual value.
        """
        result = False
        val = ''
        while True:
            status, line = device.read()
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "not defined" in line:
                    result = False
                    break
                #if self.__uboot_prompt in line or self.__kernel_prompt in line:
                if cls.__uboot_prompt == line.strip() or cls.__kernel_prompt == line.strip():
                    #if len(val) > 0:
                    if val:
                        result = True
                    break
                val += line
            else:
                logger.print_error(f"read line fail, {line}")
                result = False
                break

        if result:
            index = val.find('=')
            val = val[index+1:]
            logger.print_info(f"the value of {key} is: {val}")

        return result, val

    @classmethod
    def _uboot_get_bootenv(cls, device:object, key):
        """
        Get bootenv at uboot phase.
        Args:
            device (object): Client instance.
            key (str): key's name.
        Returns:
            tuple:
            - result (bool): If get env success, return True; Else, return False.
            - val (str): If get env success, return the actual value; Else, return "".
        """
        result = False
        val = ""
        cmd_setenv = f"printenv {key}"
        device.write(cmd_setenv)
        result, val = cls._get_key_value(device, key)
        return (result, val)

    @classmethod
    def _uboot_set_bootenv(cls, device:object, key, val):
        """
        Set bootenv at uboot phase.
        Args:
            device (objecet): Client instance.
            key (str): key's name.
            val (str): key's value.
        Returns:
            result (bool): If set env success, return True; Else, return False.
        """
        result = False
        logger.print_warning(f"set {key} to {val}")
        cmd_setenv = f"setenv {key} '{val}';saveenv"
        result = device.write(cmd_setenv)
        return result

    @classmethod
    def _is_fw_tool_exist(cls, device:object, tool_name) -> bool:
        """
        Check if fw_tools exist.
        Args:
            device (object): Client instance.
            tool_name (str): tool's name.
        Returns:
            result (bool): If the tool exists, return True; Else, return False.
        """
        result = False
        tool_path = ""
        cmd_find_fw_tool = f"find / -name {tool_name};echo $?"
        device.write(cmd_find_fw_tool)

        while True:
            status, line = device.read()
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if tool_name in line:
                    result = True
                    tool_path = line.strip()
                if "0" == line:
                    break
            else:
                logger.print_error(f"read line fail, {line}")
                result = False
                break
        if result:
            logger.print_info(f"{tool_path} is exist")
        return result, tool_path

    @classmethod
    def _kernel_get_bootenv(cls, device:object, key):
        """
        Get bootenv at kernel phase.
        Args:
            device (object): Client instance.
            key (str): key's name.
        Returns:
            tuple:
            - result (bool): If get env success, return True; Else, return False.
            - val (str): If get env success, return return the actual value; Else if fw tool
            exists, return ""; Else, return None.
        """
        result = False
        val = ""
        fw_tool_path = ""
        ret, fw_tool_path = cls._is_fw_tool_exist(device, "fw_printenv")
        if ret:
            cmd_setenv = f"{fw_tool_path} {key}"
            device.write(cmd_setenv)
            result, val = cls._get_key_value(device, key)
        else:
            val = None
        return result, val

    @classmethod
    def _kernel_set_bootenv(cls, device:object, key, val):
        """
        Set bootenv at kernel phase.
        Args:
            device (object): Client instance.
            key (str): key's name.
            val (str): key's value.
        Returns:
            result (bool): If set env success, return True; Else, return False.
        """
        result = False
        fw_tool_path = ""
        ret, fw_tool_path = cls._is_fw_tool_exist(device, "fw_setenv")
        if ret:
            logger.print_info(f"update the value of {key}: {val}")
            cmd_setenv = f"{fw_tool_path} {key} '{val}';echo $?"
            result = device.write(cmd_setenv)
        return result

    @classmethod
    def check_kernel_phase(cls):
        """
        Check if the device is running in the kernel phase.
        Args:
            None:
        Returns:
           result (bool): If the device is at kernel, return True; Else, return False.
        """
        result = False
        if cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
            result = True
        return result

    @classmethod
    def check_uboot_phase(cls):
        """
        Check if the device is running in the uboot phase.
        Args:
            None:
        Returns:
           result (bool): If the device is at uboot, return True; Else, return False.
        """
        result = False
        if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
            result = True
        return result

    @classmethod
    def init_kernel_env(cls, device:object):
        """
        Check current status of the device. If the device is not at kernel, then reboot to
        kernel if possible.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If device go to kernel success, return True; Else, return False.
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                result = cls._uboot_to_kernel(device)

        return result

    @classmethod
    def init_uboot_env(cls, device:object):
        """
        Check current status of the device. If the device is not at uboot, then reboot to
        uboot if possible.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to kernel success, return True; Else, return False.
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                result = cls._kernel_to_uboot(device)

        return result

    @classmethod
    def reboot_to_kernel(cls, device:object):
        """
        Reboot the device from current booting state to kernel
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If reboot to kernel success, return True; Else, return False
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                result = cls._uboot_to_kernel(device)
            elif cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                result = cls._kernel_to_kernel(device)

        return result

    @classmethod
    def reboot_to_uboot(cls, device:object):
        """
        Reboot the device from current booting state to uboot
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If reboot to uboot success, return True; Else, return False
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                result = cls._uboot_to_uboot(device)
            elif cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                result = cls._kernel_to_uboot(device)

        return result

    @classmethod
    def cold_reboot_to_kernel(cls, device:object) -> bool:
        """
        Cold reboot the device to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device boots to kernel success, return True; Else, return False.
        """
        result = False
        cls._cold_reboot()
        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        if result:
            logger.print_warning("cold reboot to kernel success!")
        else:
            logger.print_error("cold reboot to kernel fail!")
        return result

    @classmethod
    def cold_reboot_to_uboot(cls, device:object) -> bool:
        """
        Cold reboot the device to uboot.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device boots to uboot success, return True; Else, return False.
        """
        result = False
        cls._cold_reboot()
        device.clear_board_cur_state()

        result = cls._enter_to_uboot(device)
        if result:
            logger.print_warning("cold reboot to uboot success!")
        else:
            logger.print_error("cold reboot to uboot fail!")
        return result

    @classmethod
    def get_bootenv(cls, device:object, key):
        """
        Get bootenv.
        Args:
            device (object): Client instance.
            key (str): key's name.
        Returns:
            tuple:
            - result (bool): If get env success, return True; Else, return False.
            - val (str): If get env success, return the actual value; Else if fw tool
            exists, return ""; Else, return None.
        """
        result = False
        val = ""
        result = cls._get_cur_boot_state(device)
        if result:
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                result, val = cls._uboot_get_bootenv(device, key)
            elif cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                result, val = cls._kernel_get_bootenv(device, key)

        return result, val

    @classmethod
    def set_bootenv(cls, device:object, key, val):
        """
        Set bootenv.
        Args:
            device (object): Client instance.
            key (str): key's name
            val (str): key's value
        Returns:
            result (int): If set env success, return True; Else, return False.
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if cls.__board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                result = cls._uboot_set_bootenv(device, key, val)
            elif cls.__board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                result = cls._kernel_set_bootenv(device, key, val)

        return result

    @classmethod
    def check_bootenv(cls, device:object, key, check_value):
        """
        Check if the actual value of env key is equal to the target value.
        Args:
            device (object): device handle.
            key (str): env key.
            check_value (str): env target value.
        Returns:
            result (bool): If the actual value of env key is equal to the target value,
            return True; Else, return False.
        """
        result, get_value = cls.get_bootenv(device, key)
        if result and get_value != check_value:
            result = False
        return result
