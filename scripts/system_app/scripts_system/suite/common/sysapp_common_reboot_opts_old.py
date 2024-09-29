#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""reboot interfaces"""

import time
from suite.common.sysapp_common_logger import logger
import sysapp_platform as platform
from device.sysapp_dev_base import BootStage
from device.sysapp_dev_relay import SysappDevRelay

class SysappRebootOptsOld():
    """A class representing reboot options
    Attributes:
        device (Device): device handle
        board_cur_state (str): board current state.
        reboot_timeout (int): reboot timeout setting
        enter_uboot_try_cnt (int): the count of pressing enter to jump to uboot
        get_state_try_cnt (int): the count of pressing enter to get current state of device
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
        self.uboot_prompt = 'SigmaStar #'
        self.kernel_prompt = '/ #'
        self.board_cur_state = BootStage.E_BOOTSTAGE_UNKNOWN.name
        self.reboot_timeout = timeout
        self.enter_uboot_try_cnt = 30
        self.get_state_try_cnt = 20

    def _get_cur_boot_state(self):
        """get current status of the device
        Args:
            None
        Returns:
            result (int): if the device is at kernel or at uboot, return 0; else return 255
        """
        result = 255
        self.device.write('')
        self.board_cur_state = self.device.get_board_cur_state()[1]
        if self.board_cur_state != BootStage.E_BOOTSTAGE_UNKNOWN.name:
            result = 0
        else:
            i = 1
            while i < self.get_state_try_cnt:
                self.device.write('')
                self.board_cur_state = self.device.get_board_cur_state()[1]
                if self.board_cur_state != BootStage.E_BOOTSTAGE_UNKNOWN.name:
                    result = 0
                    break
                time.sleep(1)

        if self.board_cur_state == BootStage.E_BOOTSTAGE_UNKNOWN.name:
            logger.print_error("dev is not at kernel or at uboot")
        return result

    def check_uboot_phase(self):
        """check if current state of device is at uboot
        Args:
            None
        Returns:
            result (int): if the state is at uboot, return 0; else, return 255
        """
        result = 255
        result = self._get_cur_boot_state()
        if result != 0:
            return result
        logger.print_info(f'cur_state: {self.board_cur_state}')
        if self.board_cur_state != BootStage.E_BOOTSTAGE_UBOOT.name:
            logger.print_warning(f"dev is not at uboot now, cur_state:{self.board_cur_state}")
            result = 255
        return result

    def check_kernel_phase(self):
        """check if current state of device is at kernel
        Args:
            None
        Returns:
            result (int): if the state is at kernel, return 0; else, return 255
        """
        result = 255
        result = self._get_cur_boot_state()
        if result != 0:
            return result
        if self.board_cur_state != BootStage.E_BOOTSTAGE_KERNEL.name:
            logger.print_warning(f"dev is not at kernel now, cur_state:{self.board_cur_state}")
            result = 255
        return result

    def _enter_to_uboot(self):
        """enter to uboot
        Args:
            None
        Returns:
            result (int): if run success, return 0; else, return 255
        """
        result = 255
        try_time = 0
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
            if try_time >= self.enter_uboot_try_cnt:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.board_cur_state = self.device.get_board_cur_state()[1]
            if self.board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                logger.print_info("enter to uboot success")
                result = 0
                break
            if self.board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result

    def _enter_to_kernel(self):
        """enter to kernel
        Args:
            None
        Returns:
            result (int): if run success, return 0; else, return 255
        """
        result = 255
        try_time = 0
        # enter to kernel
        while True:
            if try_time >= self.reboot_timeout:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.board_cur_state = self.device.get_board_cur_state()[1]
            if self.board_cur_state == BootStage.E_BOOTSTAGE_KERNEL.name:
                logger.print_info("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def kernel_to_uboot(self):
        """reboot device from kernel to uboot
        Args:
            None
        Returns:
            result (int): if device go to uboot success, return 0; else, return 255
        """
        result = 255
        logger.print_info('begin to run kernel_to_uboot')
        result = self.check_kernel_phase()
        if result != 0:
            return result

        self.device.write('reboot -f')
        #time.sleep(2)
        self.device.clear_board_cur_state()

        result = self._enter_to_uboot()
        return result

    def uboot_to_kernel(self):
        """reboot device from uboot to kernel
        Args:
            None
        Returns:
            result (int): if device go to kernel success, return 0; else, return 255
        """
        result = 255
        logger.print_info('begin to run uboot_to_kernel')
        result = self.check_uboot_phase()
        if result != 0:
            return result

        self.device.write('reset')
        self.device.clear_board_cur_state()

        result = self._enter_to_kernel()
        return result

    def kernel_to_kernel(self):
        """reboot device from kernel to kernel
        Args:
            None
        Returns:
            result (int): if device go to kernel success, return 0; else, return 255
        """
        result = 255
        logger.print_info('begin to run kernel_to_kernel')
        result = self.check_kernel_phase()
        if result != 0:
            return result

        self.device.write('reboot -f')
        time.sleep(2)
        self.device.clear_board_cur_state()

        result = self._enter_to_kernel()
        return result

    def uboot_to_uboot(self):
        """reboot device from uboot to uboot
        Args:
            None
        Returns:
            result (int): if device go to uboot success, return 0; else, return 255
        """
        result = 255
        logger.print_info('begin to run uboot_to_uboot')
        result = self.check_uboot_phase()
        if result != 0:
            return result

        self.device.write('reset')
        self.device.clear_board_cur_state()

        result = self._enter_to_uboot()
        return result

    @staticmethod
    def _cold_reboot():
        """ the device is powered off and then powered on.
        Args:
            None
        Returns:
            None
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

    def cold_reboot_to_uboot(self) -> bool:
        """ cold reboot device to uboot
        Args:
            None
        Returns:
            result (int): if the device boots to uboot success, return 0; else, return 255
        """
        result = 255
        self._cold_reboot()
        self.device.clear_board_cur_state()

        result = self._enter_to_uboot()
        if result == 0:
            logger.print_warning("cold reboot to uboot success!")
        else:
            logger.print_error("cold reboot to uboot fail!")
        return result

    def cold_reboot_to_kernel(self) -> bool:
        """ cold reboot device to kernel
        Args:
            None
        Returns:
            result (int): if the device boots to kernel success, return 0; else, return 255
        """
        result = 255
        self._cold_reboot()
        self.device.clear_board_cur_state()

        result = self._enter_to_kernel()
        if result == 0:
            logger.print_warning("cold reboot to kernel success!")
        else:
            logger.print_error("cold reboot to kernel fail!")
        return result

    def check_kernel_env(self):
        """check current status of the dev, if the dev is not at kernel, then reboot to
           kernel if possible
        Args:
            None
        Returns:
            result (int): if device go to kernel success, return 0; else, return 255
        """
        result = 255
        result = self._get_cur_boot_state()
        if result == 0:
            if self.board_cur_state == BootStage.E_BOOTSTAGE_UBOOT.name:
                result = self.uboot_to_kernel()

        return result

    def _get_key_value(self, key):
        """get the value of key
        Args:
            key (str): key's name
        Returns:
            result (int): if the key exists, return 0; else, return 255
            val (str): if the key is unset, return ""; else, return actual value
        """
        result = 255
        val = ''
        while True:
            status, line = self.device.read()
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "not defined" in line:
                    result = 255
                    break
                #if self.uboot_prompt in line or self.kernel_prompt in line:
                if self.uboot_prompt == line.strip() or self.kernel_prompt == line.strip():
                    #if len(val) > 0:
                    if val:
                        result = 0
                    break
                val += line
            else:
                logger.print_error(f"read line fail, {line}")
                result = 255
                break
        #print("+++++++++++++++++++++++++++++++++++++")
        #print(f"val: {val}")
        #print("-------------------------------------")

        if result == 0:
            index = val.find('=')
            val = val[index+1:]
            logger.print_info(f"the value of {key} is: {val}")

        return result, val

    def uboot_get_bootenv(self, key):
        """get bootenv at uboot phase
        Args:
            None
        Returns:
            result (int): if get env success, return 0; else, return 255
            val (str): if get env success, return ""; else, return actual value
        """
        result = 255
        val = ""
        result = self.check_uboot_phase()
        if result != 0:
            return result

        cmd_setenv = f"printenv {key}"
        self.device.write(cmd_setenv)
        result, val = self._get_key_value(key)
        return result, val

    def uboot_set_bootenv(self, key, val):
        """set bootenv at uboot phase
        Args:
            None
        Returns:
            result (int): if set env success, return 0; else, return 255
        """
        result = 255
        result = self.check_uboot_phase()
        if result != 0:
            return result

        logger.print_warning(f"set {key} to {val}")
        cmd_setenv = f"setenv {key} '{val}';saveenv"
        self.device.write(cmd_setenv)
        return result

    def _is_fw_tool_exist(self, tool_name) -> bool:
        """check if tool exists
        Args:
            tool_name (str): tool name
        Returns:
            result (int): if tool exists, return True; else, return False
        """
        result = False
        tool_path = ""
        cmd_find_fw_tool = f"find / -name {tool_name};echo $?"
        self.device.write(cmd_find_fw_tool)

        while True:
            status, line = self.device.read()
            if status:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if tool_name in line:
                    result = True
                    tool_path = line.strip()
                if "0" in line:
                    break
            else:
                logger.print_error(f"read line fail, {line}")
                result = False
                break
        if result:
            logger.print_info(f"{tool_path} is exist")
        return result, tool_path

    def kernel_get_bootenv(self, key):
        """get bootenv at kernel phase
        Args:
            None
        Returns:
            result (int): if get env success, return 0; else, return 255
            val (str): if get env success, return ""; else, return actual value
        """
        result = 255
        val = ""
        fw_tool_path = ""
        result = self.check_kernel_phase()
        if result != 0:
            return result

        ret, fw_tool_path = self._is_fw_tool_exist("fw_printenv")
        if ret:
            cmd_setenv = f"{fw_tool_path} {key}"
            self.device.write(cmd_setenv)
            result, val = self._get_key_value(key)
        return result, val

    def kernel_set_bootenv(self, key, val):
        """set bootenv at kernel phase
        Args:
            None
        Returns:
            result (int): if set env success, return 0; else, return 255
        """
        result = 255
        fw_tool_path = ""
        result = self.check_kernel_phase()
        if result != 0:
            return result

        ret, fw_tool_path = self._is_fw_tool_exist("fw_setenv")
        if ret:
            logger.print_info(f"update the value of {key}: {val}")
            cmd_setenv = f"{fw_tool_path} {key} '{val}';echo $?"
            self.device.write(cmd_setenv)
            result = 0
        return result
