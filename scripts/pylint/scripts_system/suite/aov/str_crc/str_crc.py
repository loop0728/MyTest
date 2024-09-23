#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""str_crc test case for AOV scenarios"""

import time
from python_scripts.logger import logger
from common.sysapp_common_case_base import SysappCaseBase as CaseBase
from sysapp_client import SysappClient as Client
from str_crc_var import STR_CRC_OK, STR_CRC_FAIL, SUSPEND_CRC_START_ADDR, SUSPEND_CRC_END_ADDR

class StrCrc(CaseBase):
    """A class representing str_crc test flow
    Attributes:
        case_env_param (dict): env parameters
        case_cmd_param (dict): test commands
        case_test_param (dict): internal parameters for test
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uboot_stage = 0
        self.kernel_stage = 0
        self.is_suspend_crc_on = 0
        self.is_set_bootargs_fail = 0
        self.is_boot_up_fail = 0
        self.is_change_bootargs_fail = 0

        self.board_reset_timeout = 40
        self.bak_env = ''
        self.str_crc_rst = 0
        self.board_state_in_boot_str = 'SigmaStar #'
        self.board_state_in_kernel_str = '/ #'
        self.client_handle = client_handle
        self.client_running = False
        self.client_handle.add_case_name_to_uartlog()
        self.case_log_path = case_log_path.replace('uart.log', '') + case_name + '_uart.log'
        self.client_handle.open_case_uart_bak_file(self.case_log_path)
        self.client_handle.clear_borad_cur_state()
        self.client_handle.client_send_cmd_to_server('')
        self.borad_cur_state = self.client_handle.get_borad_cur_state()
        logger.print_info(f"str_crc_ok:{STR_CRC_OK}, str_crc_fail:{STR_CRC_FAIL}")
        logger.print_info(f"suspend_crc_start_addr:{SUSPEND_CRC_START_ADDR}, \
                            suspend_crc_end_addr:{SUSPEND_CRC_END_ADDR}")
        super().__init__()

    @logger.print_line_info
    def check_uboot_stage_with_enter(self, timeout):
        """check if the current status of the dev is at uboot
        Args:
            timeout (int): seconds of timeout
        Returns:
            result (int): result of reboot
        """
        enter_cnt = 0
        wait_keyword = 'no_check'
        check_keyword = self.board_state_in_boot_str
        while True:
            cmd_exc_sta, ret_buf, ret_match_buffer = \
                self.client_handle.client_send_cmd_to_server('', True, wait_keyword, \
                                                            check_keyword, 6)
            if cmd_exc_sta == 'run_ok':
                logger.print_info(f"ok: check_uboot_stage_with_enter cmd_exc_sta:{cmd_exc_sta}, \
                    ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}!\n")
                break
            enter_cnt += 1
            if enter_cnt > timeout * 10:
                break
            time.sleep(0.1)

    @logger.print_line_info
    def set_crc_env(self):
        """set bootargs for crc test
        Args:
            None
        Returns:
            result (int): set bootargs success or fail
        """
        logger.print_info("set_crc_env start !\n")
        suspend_crc_bootargs = "suspend_crc=" + str(SUSPEND_CRC_START_ADDR) + "," + \
                                str(SUSPEND_CRC_END_ADDR)
        cmd_crc_env = "setenv suspend_crc_env ${bootargs_linux_only} " + suspend_crc_bootargs
        cmd = []
        wait_keyword = []
        check_keyword = []
        cmd.append('printenv bootargs_linux_only;saveenv')
        cmd.append("setenv default_env 11;setenv default_env ${bootargs_linux_only};saveenv")
        cmd.append('printenv default_env;setenv suspend_crc_env 22;')
        cmd.append(cmd_crc_env)
        cmd.append('setenv bootargs_linux_only ${suspend_crc_env};saveenv')
        cmd.append('saveenv')
        cmd.append('reset')

        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)

        check_keyword.append('bootargs_linux_only=ubi.mtd')
        check_keyword.append(self.board_state_in_boot_str)
        check_keyword.append('default_env=ubi.mtd')
        check_keyword.append(suspend_crc_bootargs)
        check_keyword.append(self.board_state_in_boot_str)
        check_keyword.append(self.board_state_in_boot_str)
        check_keyword.append('')
        i = 0
        while i < len(cmd):
            cmd_exc_sta, ret_buf, ret_match_buffer = \
                self.client_handle.client_send_cmd_to_server(cmd[i], True, \
                                        wait_keyword[i], check_keyword[i], 10)
            if cmd_exc_sta == 'run_ok':
                pass
            else:
                logger.print_info(f"fail: set_crc_env cmd_exc_sta:{cmd_exc_sta}, \
                                    ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
                return 254
            time.sleep(1)
        time.sleep(self.board_reset_timeout)
        self.client_handle.client_send_cmd_to_server('')
        self.borad_cur_state = self.client_handle.get_borad_cur_state()
        try_wait_time = 0
        while self.borad_cur_state != 'at kernel':
            time.sleep(6)
            self.client_handle.client_send_cmd_to_server('')
            self.borad_cur_state = self.client_handle.get_borad_cur_state()
            if self.borad_cur_state == 'at kernel':
                break
            try_wait_time += 1
            if try_wait_time > 20:
                return 255
            continue
        self.kernel_stage = 1
        logger.print_info("set_crc_env end !\n")
        return 0

    @logger.print_line_info
    def recovery_default_env(self):
        """recovery default bootargs
        Args:
            None
        Returns:
            result (int): set bootargs success or fail
        """
        logger.print_info("recovery_default_env start !\n")
        cmd = []
        wait_keyword = []
        check_keyword = []
        cmd.append('printenv default_env;setenv bootargs_linux_only 11;')
        cmd.append('setenv bootargs_linux_only ${default_env};printenv bootargs_linux_only')
        cmd.append('setenv default_env')
        cmd.append('setenv suspend_crc_env')
        cmd.append('saveenv')
        cmd.append('reset')

        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)
        wait_keyword.append(self.board_state_in_boot_str)

        check_keyword.append('default_env=ubi.mtd')
        check_keyword.append('bootargs_linux_only=ubi.mtd')
        check_keyword.append(self.board_state_in_boot_str)
        check_keyword.append(self.board_state_in_boot_str)
        check_keyword.append(self.board_state_in_boot_str)
        check_keyword.append('')

        i = 0
        while i < len(cmd):
            cmd_exc_sta, ret_buf, ret_match_buffer = \
                self.client_handle.client_send_cmd_to_server(cmd[i], True, \
                                            wait_keyword[i], check_keyword[i], 10)
            if cmd_exc_sta == 'run_ok':
                if i == 0:
                    old_env = ret_match_buffer
            else:
                logger.print_info(f"fail: set_crc_env cmd_exc_sta:{cmd_exc_sta}, \
                                ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
                return 254
            time.sleep(1)
        time.sleep(self.board_reset_timeout)
        self.client_handle.client_send_cmd_to_server('')
        self.borad_cur_state = self.client_handle.get_borad_cur_state()
        try_wait_time = 0
        while self.borad_cur_state != 'at kernel':
            time.sleep(6)
            self.client_handle.client_send_cmd_to_server('')
            self.borad_cur_state = self.client_handle.get_borad_cur_state()
            if self.borad_cur_state == 'at kernel':
                break
            try_wait_time += 1
            if try_wait_time > 20:
                return 255
            continue
        self.kernel_stage = 1
        logger.print_info("set_crc_env end !")

    @logger.print_line_info
    def change_bootargs(self, suspend_crc_state):
        """switch bootargs between suspend_crc on and suspend_crc off.
        Args:
            suspend_crc_state (str): crc flag that add or remove crc bootargs
        Returns:
            result (int): set bootargs success or fail
        """
        self.is_set_bootargs_fail = 0
        self.uboot_stage = 0
        self.is_boot_up_fail = 1
        logger.print_info("reboot change_bootargs\n")
        cmd = 'reboot'
        wait_keyword = self.board_state_in_kernel_str
        check_keyword = 'E:CD'
        cmd_exc_sta, ret_buf, ret_match_buffer = \
            self.client_handle.client_send_cmd_to_server(cmd, True, \
                                        wait_keyword, check_keyword, 10)
        if cmd_exc_sta == 'run_ok':
            logger.print_info(f"===run_ok change_bootargs cmd:{cmd}, \
                ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
        else:
            logger.print_error(f"fail change_bootargs cmd_exc_sta:{cmd_exc_sta}, \
                ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
            self.is_set_bootargs_fail = 1
            return 255

        self.check_uboot_stage_with_enter(10)
        cmd = ''
        wait_keyword = self.board_state_in_boot_str
        check_keyword = ''
        logger.print_info("reboot change_bootargs check is at uboot\n")
        cmd_exc_sta, ret_buf, ret_match_buffer = \
            self.client_handle.client_send_cmd_to_server(cmd, True, \
                                        wait_keyword, check_keyword, 10)
        if cmd_exc_sta == 'run_ok':
            logger.print_info(f"run_ok change_bootargs cmd_exc_sta:{cmd_exc_sta}, \
                                ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
            self.uboot_stage = 1
        else:
            logger.print_info(f"fail change_bootargs cmd_exc_sta:{cmd_exc_sta}, \
                                ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
            return 255
        logger.print_info("uboot_stage is %s\n" %self.uboot_stage)
        if self.uboot_stage == 1:
            self.kernel_stage = 0
            logger.print_info("kernel_stage is %s\n" %(self.kernel_stage))
            if suspend_crc_state == 'add_crc':
                logger.print_info("set_crc_env\n")
                if self.set_crc_env() == 254:
                    logger.print_info("set_crc_env fail\n")
                    return 254
            elif suspend_crc_state == 'remove_crc':
                logger.print_info("recovery_default_env\n")
                if self.recovery_default_env() == 254:
                    logger.print_info("recovery_default_env fail\n")
                    return 254
            logger.print_info("check kernel stage\n")
            if self.kernel_stage != 1:
                logger.warning("boot up timeout\n")
                self.is_boot_up_fail = 1
                return 255
            cmd = 'lsmod'
            wait_keyword = self.board_state_in_kernel_str
            check_keyword = self.board_state_in_kernel_str
            cmd_exc_sta, ret_buf, ret_match_buffer = \
                self.client_handle.client_send_cmd_to_server(cmd, True, \
                                            wait_keyword, check_keyword, 100)
            if cmd_exc_sta == 'run_ok':
                logger.print_info(f"change_bootargs lsmod: cmd_exc_sta:{cmd_exc_sta}, \
                                    ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
            logger.print_info("kernel_stage is %s\n" %self.kernel_stage)
            if self.kernel_stage == 0:
                logger.warning("boot up timeout\n")
                self.is_boot_up_fail = 1
                return 255
        else:
            logger.warning("reboot timeout\n")
            self.is_set_bootargs_fail = 1
            return 255
        return 0

    @logger.print_line_info
    def check_cmdline_suspend_crc(self):
        """check whether the cmdline contains the setting of suspend_crc.
        Args:
            None
        Returns:
            result (int): cmd execute success or fail
        """
        result = 255
        suspend_crc_bootargs = "suspend_crc=" + str(SUSPEND_CRC_START_ADDR) + \
                                "," + str(SUSPEND_CRC_END_ADDR)
        cmd = 'cat /proc/cmdline'
        wait_keyword = self.board_state_in_kernel_str
        check_keyword = 'root='
        cmd_exc_sta, ret_buf, ret_match_buffer = \
            self.client_handle.client_send_cmd_to_server(cmd, True, \
                                        wait_keyword, check_keyword, 10)
        if cmd_exc_sta == 'run_ok':
            logger.print_info(f"check_cmdline_suspend_crc cmd_exc_sta:{cmd_exc_sta}, \
                                ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}, \
                                check_keyword:{check_keyword}\n")
            logger.print_info(f"suspend_crc_bootargs:{suspend_crc_bootargs}\n")
            if str(suspend_crc_bootargs) in ret_match_buffer:
                self.is_suspend_crc_on = 1
                result = 0
                logger.print_info(f"suspend_crc is enabled!\n")
            else:
                check_keyword = suspend_crc_bootargs
                cmd_exc_sta, ret_buf, ret_match_buffer = \
                    self.client_handle.client_send_cmd_to_server(cmd, True, \
                                        wait_keyword, check_keyword, 10)
                if cmd_exc_sta != 'run_ok':
                    self.is_suspend_crc_on = 0
                    result = 0
                    logger.print_info("suspend_crc is disabled\n")
                elif cmd_exc_sta == 'cmd_no_run':
                    self.is_suspend_crc_on = 0
                    result = 255
                else:
                    self.is_suspend_crc_on = 1
                    result = 0
                    logger.print_info("suspend_crc is enabled\n")
        else:
            self.is_suspend_crc_on = 0
            result = 0
            if cmd_exc_sta == 'cmd_no_run':
                result = 255
            logger.print_error(f"fail,wait_keyword:{wait_keyword}, \
                                exec cmd:{cmd}:suspend_crc is disabled\n")
        return result

    @logger.print_line_info
    def str_crc_test(self, alarm_time=10, wait_timeout=50):
        """do str crc test.
        Args:
            alarm_time (int): str wakeup time
            wait_timeout (int): cmd execute timeout
        Returns:
            result (int): test success or fail
        """
        self.str_crc_rst = 0
        result = 255
        str_crc_ok_str = STR_CRC_OK.strip('"')
        str_crc_fail_str = STR_CRC_FAIL.strip('"')
        cmd = 'echo {} > /sys/devices/virtual/sstar/rtcpwc/alarm_timer;\
                echo mem > /sys/power/state'.format(alarm_time)
        wait_keyword = self.board_state_in_kernel_str
        check_keyword = str_crc_ok_str
        cmd_exc_sta, ret_buf, ret_match_buffer = \
            self.client_handle.client_send_cmd_to_server(cmd, True, \
                                    wait_keyword, check_keyword, wait_timeout)
        logger.print_info(f"start str_crc_test cmd_exc_sta:{cmd_exc_sta}, cmd:{cmd}, \
                                    ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
        if cmd_exc_sta == 'run_ok':
            logger.print_info("send str cmd\n")
            logger.print_info(f"str_crc_test cmd:{cmd}, ret_buf:{ret_buf}, \
                                    ret_match_buffer:{ret_match_buffer}\n")
            self.str_crc_rst = 1
            result = 0
            logger.print_info("STR CRC test success\n")
        elif str(str_crc_fail_str) in ret_match_buffer:
            self.str_crc_rst = 2
            logger.print_info("send str cmd fail\n")
            result = 254

        logger.print_info("str_crc_test end !")
        return result

    @logger.print_line_info
    def uboot_add_crc_env_test_crc_func(self):
        """uboot add crc bootargs and test str crc
        Args:
            None
        Returns:
            result (int): test success or fail
        """
        logger.print_info("go uboot_add_crc_env_test_crc_func!\n")
        result = self.change_bootargs('add_crc')
        if result != 0:
            logger.print_error("test_add_uboot_crc_flow is fail !\n")
            return result
        if self.is_set_bootargs_fail == 0 and \
                self.is_boot_up_fail == 0 and \
                self.is_change_bootargs_fail == 0:
            result = self.str_crc_test()
            if result == 254:
                logger.print_error("str_crc_test is abnormal!\n")
            elif result != 0:
                logger.print_error("str_crc_test is error!\n")
        result = self.str_crc_test()
        if result != 0:
            logger.print_error("uboot_add_crc_env_test_crc_func str_crc_test is fail !\n")
        result = self.change_bootargs('remove_crc')
        if result != 0:
            logger.print_error("recovery_default_env remove_crc is error!\n")
        return result

    @logger.print_line_info
    def default_open_crc_test_crc_func(self):
        """test str crc
        Args:
            None
        Returns:
            result (int): test success or fail
        """
        logger.print_info("go default_open_crc_test_crc_func!\n")
        result = self.str_crc_test()
        if result != 0:
            logger.print_error("test_uboot_test_crc_flow is fail !\n")
        return result

    @logger.print_line_info
    def runcase(self):
        """test function body
        Args:
            None
        Returns:
            result (int): result of test
        """
        result = 0
        logger.print_info("case_name:", self.case_name)
        logger.print_info("suspend_crc_start_addr is %s, suspend_crc_end_addr is %s\n" \
                                %(SUSPEND_CRC_START_ADDR, SUSPEND_CRC_END_ADDR))

        logger.print_info("runcase get board stat,set board to kernel!\n")
        try_wait_time = 0
        self.borad_cur_state = self.client_handle.get_borad_cur_state()
        while self.borad_cur_state != 'at kernel':
            if self.borad_cur_state == 'at uboot':
                cmd = 'reset'
                wait_keyword = self.board_state_in_boot_str
                check_keyword = self.board_state_in_kernel_str
                cmd_exc_sta, ret_buf, ret_match_buffer = \
                    self.client_handle.client_send_cmd_to_server(cmd, True, \
                                            wait_keyword, check_keyword, 60)
                if cmd_exc_sta == 'run_ok':
                    self.borad_cur_state = self.client_handle.get_borad_cur_state()
                    logger.print_info(f"ok str_crc_test cmd_exc_sta:{cmd_exc_sta}, \
                                        ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
                    break
                else:
                    logger.print_error(f"fail str_crc_test cmd_exc_sta:{cmd_exc_sta}, \
                                        ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer}\n")
                    self.borad_cur_state = self.client_handle.get_borad_cur_state()
            else:
                self.client_handle.client_send_cmd_to_server('')
                self.borad_cur_state = self.client_handle.get_borad_cur_state()
                if self.borad_cur_state == 'at kernel':
                    break
                try_wait_time += 1
                time.sleep(0.01)
                if try_wait_time > 40:
                    return 255
                continue
        logger.print_info("check and set suspend_crc env\n")
        result = self.check_cmdline_suspend_crc()
        if result != 0:
            logger.print_error("check_cmdline_suspend_crc 0 is abnormal!\n")
            return result
        if self.is_suspend_crc_on == 0:
            result = self.uboot_add_crc_env_test_crc_func()
            if result != 0:
                return result
        elif self.is_suspend_crc_on == 1:
            result = self.default_open_crc_test_crc_func()
            if result != 0:
                return result
            logger.print_info("default_open_crc_test_crc_func\n")
        return result

    @logger.print_line_info
    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.print_warning("stat str crc test")
        logger.print_warning("cmd : echo 3 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
        logger.print_warning("cmd : echo mem > /sys/power/state")
        logger.print_warning("if the result return 'CRC check success', test pass; \
                            if the result return 'CRC check fail', test fail.")
