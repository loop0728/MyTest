#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""reboot interfaces"""

import time
from suite.common.sysapp_common_logger import logger
import sysapp_platform as platform
from device.sysapp_dev_relay import SysappDevRelay

class SysappRebootOpts():
    """
    A class representing reboot options
    Attributes:
        __uboot_prompt (str): the prompt of uboot phase
        __kernel_prompt (str): the prompt of kernel phase
        __reboot_timeout (int): reboot timeout setting
        __enter_uboot_try_cnt (int): the count of pressing enter to jump to uboot
        __get_state_try_cnt (int): the count of pressing enter to get current state of device
    """
    __uboot_prompt  = 'SigmaStar #'
    __kernel_prompt = '/ #'
    __reboot_timeout = 30
    __enter_uboot_try_cnt = 30
    __get_state_try_cnt = 20

    @classmethod
    def _get_cur_boot_state(cls, device: object):
        """
        Get current status of the device.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device is at kernel or at uboot, return True; Else, return False;
        """
        result = False
        device.write('')
        if device.check_uboot_phase() or device.check_kernel_phase():
            result = True
        else:
            i = 1
            while i < cls.__get_state_try_cnt:
                device.write('')
                if device.check_uboot_phase() or device.check_kernel_phase():
                    result = True
                    break
                time.sleep(1)

        if not result:
            logger.error("dev is not at kernel or at uboot")
        return result

    @classmethod
    def _enter_to_uboot(cls, device: object):
        """
        Enter to uboot.
        Args:
            device (object): Client handle.
        Returns:
            result (bool): If run success, return True; Else, return False.
        """
        result = False
        try_time = 0
        # enter to uboot
        while True:
            if try_time >= cls.__enter_uboot_try_cnt:
                logger.error("enter to uboot timeout")
                result = False
                break
            device.write('')
            if device.check_uboot_phase():
                logger.info("enter to uboot success")
                result = True
                break
            if device.check_kernel_phase():
                logger.error("enter to uboot fail, run in kernel phase now")
                result = False
                break
            try_time += 1
            time.sleep(0.1)

        return result

    @classmethod
    def _enter_to_kernel(cls, device: object):
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
                logger.error("enter to kernel timeout")
                result = False
                break
            if device.check_kernel_phase():
                logger.info("enter to kernel success")
                result = True
                break
            try_time += 1
            time.sleep(1)
        return result

    @classmethod
    def _kernel_to_uboot(cls, device: object):
        """
        Reboot the device from kernel to uboot.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to uboot success, return True; Else, return False.
        """
        result = False
        logger.info('begin to run _kernel_to_uboot')
        device.write('reboot -f')
        #time.sleep(2)
        device.clear_board_cur_state()

        result = cls._enter_to_uboot(device)
        return result

    @classmethod
    def _uboot_to_kernel(cls, device: object):
        """
        Reboot the device from uboot to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to kernel success, return True; Else, return False.
        """
        result = False
        try_cnt = 0
        logger.info('begin to run _uboot_to_kernel')
        while try_cnt < 5:
            result = device.write('reset')
            if result:
                break
            try_cnt += 1
            time.sleep(1)

        if not result:
            logger.error("send reset cmd timeout")
            return result

        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        return result

    @classmethod
    def _kernel_to_kernel(cls, device: object):
        """
        Reboot the device from kernel to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to kernel success, return True; Else, return False.
        """
        result = False
        logger.info('begin to run _kernel_to_kernel')
        device.write('reboot -f')
        #time.sleep(2)
        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        return result

    @classmethod
    def _uboot_to_uboot(cls, device: object):
        """
        Reboot the device from uboot to uboot.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device go to uboot success, return True; Else, return False.
        """
        result = False
        try_cnt = 0
        logger.info('begin to run _uboot_to_uboot')
        while try_cnt < 5:
            logger.warning(f"[try_cnt:{try_cnt+1}/5] send reset cmd")
            result = device.write('reset')
            if result:
                break
            try_cnt += 1
            time.sleep(1)

        if not result:
            logger.error("send reset cmd timeout")
            return result

        device.clear_board_cur_state()

        result = cls._enter_to_uboot(device)
        return result

    @classmethod
    def _run_uboot_cmd_to_kernel(cls, device: object, cmd):
        """
        Execute uboot command and enter to kernel from uboot.
        Args:
            device (object): Client instance.
            cmd (str): uboot command
        Returns:
            result (bool): If the device go to kernel success, return True; Else, return False.
        """
        result = False
        try_cnt = 0
        logger.info('begin to run _run_uboot_cmd_to_kernel')
        while try_cnt < 5:
            result = device.write(cmd)
            if result:
                break
            try_cnt += 1
            time.sleep(1)

        if not result:
            logger.error(f"send {cmd} timeout")
            return result

        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        return result

    @staticmethod
    def cold_reboot():
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
        logger.info(f"init rs232_contrl_handle {relay_name}:{relay_no}")
        rs232_contrl_handle.connect()
        rs232_contrl_handle.power_off()
        time.sleep(2)
        rs232_contrl_handle.power_on()
        rs232_contrl_handle.disconnect()
        logger.info("closed rs232_contrl_handle.")

    @classmethod
    def _get_key_value(cls, device: object, key):
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
                if cls.__uboot_prompt == line.strip() or cls.__kernel_prompt == line.strip():
                    if val:
                        result = True
                    break
                val += line
            else:
                logger.error(f"read line fail, {line}")
                result = False
                break

        if result:
            index = val.find('=')
            val = val[index+1:]
            logger.info(f"the value of {key} is: {val}")

        return result, val

    @classmethod
    def _uboot_get_bootenv(cls, device: object, key):
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
    def _uboot_set_bootenv(cls, device: object, key, val):
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
        logger.warning(f"set {key} to {val}")
        cmd_setenv = f"setenv {key} '{val}';saveenv"
        result = device.write(cmd_setenv)
        return result

    @classmethod
    def _is_fw_tool_exist(cls, device: object, tool_name) -> bool:
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
                if line == "0":
                    break
            else:
                logger.error(f"read line fail, {line}")
                result = False
                break
        if result:
            logger.info(f"{tool_path} is exist")
        return result, tool_path

    @classmethod
    def _kernel_get_bootenv(cls, device: object, key):
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
    def _kernel_set_bootenv(cls, device: object, key, val):
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
            logger.info(f"update the value of {key}: {val}")
            cmd_setenv = f"{fw_tool_path} {key} '{val}';echo $?"
            result = device.write(cmd_setenv)
        return result

    @classmethod
    def init_kernel_env(cls, device: object):
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
        if result and device.check_uboot_phase():
            result = cls._uboot_to_kernel(device)

        return result

    @classmethod
    def init_uboot_env(cls, device: object):
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
        if result and device.check_kernel_phase():
            result = cls._kernel_to_uboot(device)

        return result

    @classmethod
    def reboot_to_kernel(cls, device: object):
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
            if device.check_uboot_phase():
                result = cls._uboot_to_kernel(device)
            elif device.check_kernel_phase():
                result = cls._kernel_to_kernel(device)

        return result

    @classmethod
    def reboot_to_uboot(cls, device: object):
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
            if device.check_uboot_phase():
                result = cls._uboot_to_uboot(device)
            elif device.check_kernel_phase():
                result = cls._kernel_to_uboot(device)

        return result

    @classmethod
    def run_bootcmd(cls, device: object):
        """
        Run bootcmd in uboot phase to enter to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If enter to kernel success, return True; Else, return False
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if device.check_uboot_phase():
                result = cls._run_uboot_cmd_to_kernel(device, "run bootcmd")

        return result

    @classmethod
    def estar_script(cls, device: object, scritp_name):
        """
        Do estar in uboot phase to enter to kernel.
        Args:
            device (object): Client instance.
            scritp_name (str): script name
        Returns:
            result (bool): If enter to kernel success, return True; Else, return False
        """
        result = False
        result = cls._get_cur_boot_state(device)
        if result:
            if device.check_uboot_phase():
                result = cls._run_uboot_cmd_to_kernel(device, f"estar {scritp_name}")

        return result

    @classmethod
    def cold_reboot_to_kernel(cls, device: object) -> bool:
        """
        Cold reboot the device to kernel.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device boots to kernel success, return True; Else, return False.
        """
        result = False
        cls.cold_reboot()
        device.clear_board_cur_state()

        result = cls._enter_to_kernel(device)
        if result:
            logger.warning("cold reboot to kernel success!")
        else:
            logger.error("cold reboot to kernel fail!")
        return result

    @classmethod
    def cold_reboot_to_uboot(cls, device: object) -> bool:
        """
        Cold reboot the device to uboot.
        Args:
            device (object): Client instance.
        Returns:
            result (bool): If the device boots to uboot success, return True; Else, return False.
        """
        result = False
        cls.cold_reboot()
        device.clear_board_cur_state()

        result = cls._enter_to_uboot(device)
        if result:
            logger.warning("cold reboot to uboot success!")
        else:
            logger.error("cold reboot to uboot fail!")
        return result

    @classmethod
    def get_bootenv(cls, device: object, key):
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
            if device.check_uboot_phase():
                result, val = cls._uboot_get_bootenv(device, key)
            elif device.check_kernel_phase():
                result, val = cls._kernel_get_bootenv(device, key)

        return result, val

    @classmethod
    def set_bootenv(cls, device: object, key, val):
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
            if device.check_uboot_phase():
                result = cls._uboot_set_bootenv(device, key, val)
            elif device.check_kernel_phase():
                result = cls._kernel_set_bootenv(device, key, val)

        return result

    @classmethod
    def check_bootenv(cls, device: object, key, check_value):
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
