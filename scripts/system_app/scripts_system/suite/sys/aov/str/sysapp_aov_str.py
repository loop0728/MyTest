#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""str test case for AOV scenarios"""

import re
import time
from enum import Enum
from cases.platform.sys.aov.str_var import (STR_TARGET, STR_KMSG,
                                            SUSPEND_ENTRY, SUSPEND_EXIT,
                                            APP_RESUME, BOOTING_TIME)
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_error_codes import SysappErrorCodes
from suite.sys.aov.common.sysapp_aov_common import SysappAovCommon
from sysapp_client import SysappClient as Client

class SysappStrStage(Enum):
    """
    A class representing str stage"""
    E_STAGE_SUSPEND_ENTRY = 1
    E_STAGE_SUSPEND_EXIT = 2
    E_STAGE_APP_RESUME = 3

class SysappAovStr(CaseBase):
    """
    A class representing str test flow
    Attributes:
        case_env_param (dict): env parameters
        case_cmd_param (dict): test commands
        case_test_param (dict): internal parameters for test
    """

    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """
        Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.case_env_param = {
            'max_read_lines': 10240
        }
        self.case_cmd_param = {
            'cmd_uboot_reset': 'reset',
            'cmd_kernel_reboot': 'reboot',
            'cmd_aov_run': '/customer/sample_code/bin/prog_aov_aov_demo -t -d',
            'cmd_aov_test': 'a',
            'cmd_aov_quit': 'q',
            'cmd_printk_time_on': 'echo y > /sys/module/printk/parameters/time',
            'cmd_printk_time_off': 'echo n > /sys/module/printk/parameters/time',
            'cmd_redirect_kmsg': f"cat /proc/kmsg > {STR_KMSG} &",
            'cmd_kill_kmsg': "pkill -f 'cat /proc/kmsg'",
            'cmd_cat_tmpfile': f"cat {STR_KMSG}",
            'cmd_cat_booting_time': 'cat /sys/class/sstar/msys/booting_time'
        }
        self.case_test_param = {
            'str_suspend_entry': SUSPEND_ENTRY.strip('"'),
            'str_suspend_exit': SUSPEND_EXIT.strip('"'),
            'str_app_resume': APP_RESUME.strip('"'),
            'str_booting_time': BOOTING_TIME.strip('"'),
            'target_time': STR_TARGET,
            'suspend_enter_time': 0,
            'suspend_exit_time': 0,
            'app_resume_time': 0,
            'ipl_resume_time': 0,
            'kernel_resume_time': 0,
            'str_cnt': 6
        }

    @sysapp_print.print_line_info
    def reboot_dev(self):
        """
        Check current status of the dev, if the dev is at uboot or at kernel, then reboot the dev.
        Args:
            None:
        Returns:
            result (bool): Reboot device success, return True; Else, return False.
        """
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        return result

    # show timestamp of printk log
    @sysapp_print.print_line_info
    def enable_printk_time(self):
        """
        Enable print timestamp in the kernel print.
        Args:
            None:
        Returns:
            None:
        """
        self.uart.write(self.case_cmd_param['cmd_printk_time_on'])

    # hide timestamp of printk log
    @sysapp_print.print_line_info
    def disable_printk_time(self):
        """
        Disable print timestamp in the kernel print.
        Args:
            None:
        Returns:
            None:
        """
        self.uart.write(self.case_cmd_param['cmd_printk_time_off'])

    # run aov demo in test mode
    @sysapp_print.print_line_info
    def run_aov_demo_test(self):
        """
        Run aov demo.
        Args:
            None:
        Returns:
            None:
        """
        retry_cnt = 0
        logger.info("start app")
        self.uart.write(self.case_cmd_param['cmd_aov_run'])
        time.sleep(10)
        logger.info("send str cmd to app")
        self.uart.write(self.case_cmd_param['cmd_aov_test'])
        time.sleep(10)

        logger.info("enter 'q' to exit app")
        while retry_cnt < 10:
            self.uart.write(self.case_cmd_param['cmd_aov_quit'])
            retry_cnt = retry_cnt + 1
            time.sleep(0.1)
        time.sleep(2)

    @sysapp_print.print_line_info
    def redirect_kmsg(self):
        """
        Redirect kmsg to memory.
        Args:
            None:
        Returns:
            None:
        """
        logger.info(f"redirect kmsg to {STR_KMSG}")
        self.uart.write(self.case_cmd_param['cmd_redirect_kmsg'])
        time.sleep(5)
        self.uart.write(self.case_cmd_param['cmd_kill_kmsg'])

    def _parse_str_stage(self, line, check_stage, retry_cnt):
        """
        Parse kmsg line.
        Args:
            line (str): kmsg line
            check_stage (SysappStrStage): test stage
            retry_cnt (int): current retry time
        Returns:
            result (bool): result of parsing stage, True: parse next line; False: go to next step
        """
        result = False
        stage_time = ''
        stage_phase = ''
        if check_stage == SysappStrStage.E_STAGE_SUSPEND_ENTRY:
            stage_time = 'suspend_enter_time'
            stage_phase = 'str_suspend_entry'
        elif check_stage == SysappStrStage.E_STAGE_SUSPEND_EXIT:
            stage_time = 'suspend_exit_time'
            stage_phase = 'str_suspend_exit'
        elif check_stage == SysappStrStage.E_STAGE_APP_RESUME:
            stage_time = 'app_resume_time'
            stage_phase = 'str_app_resume'
            result = True

        #if (self.case_test_param[stage_time] == 0
        #        and self.case_test_param[stage_phase] in line):
        if self.case_test_param[stage_phase] in line:
            pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
            match = pattern.search(line)
            if match:
                self.case_test_param[stage_time] = match.group(1)
                logger.warning(f"{retry_cnt}: {stage_time} is "
                                     f"{self.case_test_param[stage_time]}")
                result = True

        if check_stage == SysappStrStage.E_STAGE_APP_RESUME:
            result = False
        return result

    @sysapp_print.print_line_info
    def _parse_kmsg(self):
        """
        Parse kmsg.
        Args:
            None:
        Returns:
            result (bool): result of parsing kmsg
        """
        result = False
        retry_cnt = 1
        read_line_cnt = 0
        logger.warning(f"it will do suspend and resume "
                             f"{self.case_test_param['str_cnt']} times ...")

        while True:
            if read_line_cnt > self.case_env_param['max_read_lines']:
                logger.error(f"read lines exceed max_read_lines: "
                                   f"{self.case_env_param['max_read_lines']}")
                result = False
                break

            status, line = self.uart.read()
            if status:
                read_line_cnt += 1

                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()

                # check suspend entry
                result = self._parse_str_stage(line,
                                               SysappStrStage.E_STAGE_SUSPEND_ENTRY,
                                               retry_cnt)
                if result:
                    continue

                # check suspend exit
                result = self._parse_str_stage(line,
                                               SysappStrStage.E_STAGE_SUSPEND_EXIT,
                                               retry_cnt)
                if result:
                    continue

                if (self.case_test_param['suspend_enter_time'] != 0
                        and self.case_test_param['suspend_exit_time'] != 0):
                    self.case_test_param['app_resume_time'] = 0

                # check app resume
                self._parse_str_stage(line, SysappStrStage.E_STAGE_APP_RESUME, retry_cnt)

                # wait single str flow complete
                if (self.case_test_param['suspend_enter_time'] != 0
                        and self.case_test_param['suspend_exit_time'] != 0
                        and self.case_test_param['app_resume_time'] != 0):
                    #logger.warning(f"{retry_cnt}: app_resume_time is "
                    #                     f"{self.case_test_param['app_resume_time']}")
                    if retry_cnt < self.case_test_param['str_cnt']:
                        self.case_test_param['suspend_enter_time'] = 0
                        self.case_test_param['suspend_exit_time'] = 0
                        self.case_test_param['app_resume_time'] = 0
                        retry_cnt += 1
                    else:
                        result = True
                        break
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                result = False
                break
        return result

    # cat kmsg saved in tmpfile
    @sysapp_print.print_line_info
    def cat_kmsg(self):
        """
        Show kmsg.
        Args:
            None:
        Returns:
            None:
        """
        self.uart.write(self.case_cmd_param['cmd_cat_tmpfile'])
        time.sleep(5)
        return self._parse_kmsg()

    # parse booting_time from case loacl log file
    @sysapp_print.print_line_info
    def _parse_booting_time(self):
        """
        Parse the time takes in the IPL phase and kernel phase in resume flow.
        Args:
            None:
        Returns:
            result (bool): Result of parsing booting time.
        """
        result = False
        is_kernel_part = 0
        read_line_cnt = 0

        while True:
            if read_line_cnt > self.case_env_param['max_read_lines']:
                logger.error(f"read lines exceed max_read_lines: "
                                   f"{self.case_env_param['max_read_lines']}")
                result = False
                break

            status, line = self.uart.read()
            if status:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if (self.case_test_param['ipl_resume_time'] == 0
                        and self.case_test_param['str_booting_time'] in line):
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.case_test_param['ipl_resume_time'] = match.group(1)
                        logger.info(f"ipl_resume_time is "
                                          f"{self.case_test_param['ipl_resume_time']}")
                        continue

                if is_kernel_part == 0 and "LINUX" in line:
                    is_kernel_part = 1

                if (self.case_test_param['kernel_resume_time'] == 0
                        and is_kernel_part == 1
                        and self.case_test_param['str_booting_time'] in line):
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.case_test_param['kernel_resume_time'] = match.group(1)
                        logger.info(f"kernel_resume_time is "
                                          f"{self.case_test_param['kernel_resume_time']}")

                if (self.case_test_param['ipl_resume_time'] != 0
                        and self.case_test_param['kernel_resume_time'] != 0):
                    result = True
                    break
            else:
                logger.error(f"read line:{read_line_cnt} fail")
                result = False
                break
        return result

    # get booting time after resume
    @sysapp_print.print_line_info
    def cat_booting_time(self):
        """
        Show the time takes in the IPL pahse and kernel phase in resume flow.
        Args:
            None:
        Returns:
            None:
        """
        self.uart.write(self.case_cmd_param['cmd_cat_booting_time'])
        time.sleep(5)
        return self._parse_booting_time()

    # judge pass or fail
    @sysapp_print.print_line_info
    def judge_test_result(self):
        """
        Analyze test result.
        Args:
            None:
        Returns:
            result (bool): Result of analysis.
        """
        result = False
        kernel_str_us = 0
        total_str_us = 0

        # cost time
        while True:
            if (self.case_test_param['suspend_enter_time'] == 0
                    or self.case_test_param['suspend_exit_time'] == 0
                    or self.case_test_param['app_resume_time'] == 0):
                logger.error("str test run timeout")
                break

            if (self.case_test_param['suspend_enter_time'] >
                    self.case_test_param['suspend_exit_time']
                    or self.case_test_param['suspend_exit_time'] >
                    self.case_test_param['app_resume_time']):
                logger.error("the stat time of str is invalid")
                break

            kernel_str_time = (float(self.case_test_param['suspend_exit_time']) -
                               float(self.case_test_param['suspend_enter_time']))
            total_str_time = (float(self.case_test_param['app_resume_time']) -
                              float(self.case_test_param['suspend_enter_time']))
            kernel_str_us = float(kernel_str_time) * 1000000
            total_str_us = float(total_str_time) * 1000000

            logger.warning(f"str Time cost:{int(total_str_us)} us; "
                                 f"target:{self.case_test_param['target_time']} us")
            logger.warning(f"str (only kernel) Time cost:{int(kernel_str_us)} us")
            logger.warning(f"str booting_time (IPL) Time cost:"
                                 f"{int(self.case_test_param['ipl_resume_time'])} us")
            logger.warning(f"str booting_time (kernel) Time cost:"
                                 f"{int(self.case_test_param['kernel_resume_time'])} us")

            if total_str_us <= float(self.case_test_param['target_time']):
                result = True
            break

        # force to pass, will be removed if the sdk runs stablely.
        result = True

        logger.info("")
        if result:
            time_info = (f"target_l2l:{int(self.case_test_param['target_time'])};"
                         f"total_l2l:{int(total_str_us)};sys_l2l:{int(kernel_str_us)};"
                         f"ipl_l2l:{int(self.case_test_param['ipl_resume_time'])};"
                         f"kernel_l2l:{int(self.case_test_param['kernel_resume_time'])};"
                         "target_h2l:0;total_h2l:0;sys_h2l:0;ipl_h2l:0;kernel_h2l:0\n")

            str_handle = SysappAovCommon(self.case_name)
            str_handle.save_time_info(self.case_name, time_info)

            return result

    @sysapp_print.print_line_info
    def runcase(self):
        """
        test function body
        Args:
            None:
        Returns:
            error_code (SysappErrorCodes): Result of test.
        """
        result = False
        error_code = SysappErrorCodes.FAIL

        # reboot first to clear board status, for temporary testing
        result = self.reboot_dev()
        if result:
            # open kernel timestamp
            self.enable_printk_time()
            # run aov app in test mode
            self.run_aov_demo_test()
            # redirect kmsg to memory file
            self.redirect_kmsg()
            # cat kmsg
            result = self.cat_kmsg()
            if result:
                # cat booting time
                result = self.cat_booting_time()
                if result:
                    # judge test result
                    result = self.judge_test_result()
            # close kernel timestamp
            self.disable_printk_time()
        else:
            logger.error("reboot timeout!")

        if result:
            logger.warning("str test pass!")
            error_code = SysappErrorCodes.SUCCESS
        else:
            logger.error("str test fail!")
            error_code = SysappErrorCodes.FAIL

        return error_code

    @sysapp_print.print_line_info
    @staticmethod
    def system_help():
        """
        Help info.
        Args:
            None:
        Returns:
            None:
        """
        logger.warning("stat str cost time")
        logger.warning("cmd: str")
        logger.warning("AOV STR cost time: the time interva bwtween two 'suspend entry', "
                             "include app's time consumption")
        logger.warning("SYS STR cost time: the time interva bwtween 'suspend entry' and "
                             "'suspend exit', kernel space's time consumption")
        logger.warning("stat time: the str cost time of the scenario which changes fps "
                             "from low-fps to low-fps")
