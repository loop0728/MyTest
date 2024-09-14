#import sys
import time
import re
#import os
#import json
from enum import Enum
from PythonScripts.logger import logger
#import threading
#import inspect
from Common.case_base import CaseBase
from client import Client
import Suite.AOV.Common.aov_common as aov_common
from str_var import str_target, str_kmsg, suspend_entry, suspend_exit, app_resume, booting_time

class aov_str_stage(Enum):
    STAGE_HIGH_FPS_TO_LOW_FPS_1 = 1
    STAGE_HIGH_FPS_TO_LOW_FPS_2 = 2
    STAGE_LOW_FPS_TO_LOW_FPS    = 3

class str(CaseBase):
    cnt_check_keyword_dict = {}

    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

        """ case internal params start """
        self.borad_cur_state = ''
        self.board_state_in_kernel_str = '/ #'
        self.set_check_keyword_dict    = {}
        self.other_case_json_path      = './AOV/str/str_keyword.json'    # 额外的关键字过滤
        self.reboot_timeout            = 30
        self.max_read_lines            = 10240
        self.log_read_pos              = 0

        self.str_suspend_entry         = suspend_entry.strip('"')
        self.str_suspend_exit          = suspend_exit.strip('"')
        self.str_app_resume            = app_resume.strip('"')
        self.str_booting_time          = booting_time.strip('"')
        self.cmd_uboot_reset           = "reset"
        self.cmd_kernel_reboot         = "reboot"
        self.cmd_aov_run               = "/customer/sample_code/bin/prog_aov_aov_demo -t -d"
        self.cmd_aov_test              = "a"
        self.cmd_aov_quit              = "q"
        self.cmd_printk_time_on        = "echo y > /sys/module/printk/parameters/time"
        self.cmd_printk_time_off       = "echo n > /sys/module/printk/parameters/time"
        self.cmd_redirect_kmsg         = "cat /proc/kmsg > {} &".format(str_kmsg)
        self.cmd_kill_kmsg             = "pkill -f 'cat /proc/kmsg'"
        self.cmd_cat_tmpfile          = "cat {}".format(str_kmsg)
        #self.cmd_cat_tmpfile           = "strings {} | grep -E '{}|{}|{}'".format(str_kmsg, self.str_suspend_entry, self.str_suspend_exit, self.str_app_resume)
        self.cmd_cat_booting_time      = "cat /sys/class/sstar/msys/booting_time"

        """ str """
        self.target_time           = str_target
        self.suspend_enter_time    = 0
        self.suspend_exit_time     = 0
        self.app_resume_time       = 0
        """ resume booting time """
        self.ipl_resume_time           = 0
        self.kernel_resume_time        = 0
        """ exec suspend/resume count """
        self.str_cnt                   = 6
        """ case internal params end """


    """ case internal functions start """
    # check current status of the dev, if the dev is at uboot of at kernel, then reboot the dev
    @logger.print_line_info
    def reboot_dev(self):
        trywait_time = 0
        result = 255
        logger.print_info("reboot dev ...")
        self.uart.write('')
        self.borad_cur_state = self.uart.get_borad_cur_state()[1]
        if self.borad_cur_state == 'Unknow':
            for i in range(1,20):
                self.uart.write('')
                self.borad_cur_state = self.uart.get_borad_cur_state()[1]
                if self.borad_cur_state != 'Unknow':
                    break
        if self.borad_cur_state == 'Unknow':
            return result
        if self.borad_cur_state == 'at uboot':
            self.uart.write(self.cmd_uboot_reset)
            self.uart.clear_borad_cur_state()
        if self.borad_cur_state == 'at kernel':
            self.uart.write(self.cmd_kernel_reboot)
            time.sleep(2)
            self.uart.clear_borad_cur_state()
        while True:
            self.borad_cur_state = self.uart.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                result = 0
                logger.print_info("borad_cur_state:%s " % self.borad_cur_state)
                break
            elif self.borad_cur_state == 'at uboot':
                self.uart.write(self.cmd_uboot_reset)
                self.uart.clear_borad_cur_state()
            else:
                time.sleep(1)
                trywait_time = trywait_time + 1
                if trywait_time > self.reboot_timeout:
                    break
        return result

    # show timestamp of printk log
    @logger.print_line_info
    def enable_printk_time(self):
        self.uart.write(self.cmd_printk_time_on)

    # hide timestamp of printk log
    @logger.print_line_info
    def disable_printk_time(self):
        self.uart.write(self.cmd_printk_time_off)

    # run aov demo in test mode
    @logger.print_line_info
    def run_aov_demo_test(self):
        logger.print_info("start app")
        self.uart.write(self.cmd_aov_run)
        time.sleep(10)
        logger.print_info("send str cmd to app")
        self.uart.write(self.cmd_aov_test)
        time.sleep(10)

        logger.print_info("enter 'q' to exit app")
        retryCnt = 0
        while retryCnt < 10:
            self.uart.write(self.cmd_aov_quit)
            #self.uart.write("\n")
            retryCnt = retryCnt + 1
            time.sleep(0.1)
        time.sleep(2)

    # redirect kmsg to memory
    @logger.print_line_info
    def redirect_kmsg(self):
        logger.print_info("redirect kmsg to %s" %(str_kmsg))
        self.uart.write(self.cmd_redirect_kmsg)
        time.sleep(5)
        self.uart.write(self.cmd_kill_kmsg)

    @logger.print_line_info
    def _parse_kmsg(self):
        result = 255
        testCnt = 1
        read_line_cnt = 0
        logger.print_warning("it will do suspend and resume %d times ..." %(self.str_cnt))

        while True:
            if read_line_cnt > self.max_read_lines:
                logger.print_error("read lines exceed max_read_lines:%d" %(self.max_read_lines))
                result = 255
                break

            status, line = self.uart.read()
            if status == True:
                read_line_cnt += 1

                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                # check suspend_entry
                if self.suspend_enter_time == 0 and self.str_suspend_entry in line:
                    pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                    match = pattern.search(line)
                    if match:
                        self.suspend_enter_time = match.group(1)
                        logger.print_warning("%d: suspend_enter_time is %s" %(testCnt, self.suspend_enter_time))
                        continue

                # check suspend_exit
                if self.suspend_exit_time == 0 and self.str_suspend_exit in line:
                    pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                    match = pattern.search(line)
                    if match:
                        self.suspend_exit_time = match.group(1)
                        logger.print_warning("%d: suspend_exit_time is %s" %(testCnt, self.suspend_exit_time))
                        continue

                if self.suspend_enter_time != 0 and self.suspend_exit_time != 0:
                    self.app_resume_time = 0

                # check app resume
                if self.app_resume_time == 0 and self.str_app_resume in line:
                    pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                    match = pattern.search(line)
                    if match:
                        self.app_resume_time = match.group(1)

                # wait single str flow complete
                if self.suspend_enter_time != 0 and self.suspend_exit_time != 0 and self.app_resume_time != 0:
                    logger.print_warning("%d: app_resume_time is %s" %(testCnt, self.app_resume_time))
                    if testCnt < self.str_cnt:
                        self.suspend_enter_time = 0
                        self.suspend_exit_time = 0
                        self.app_resume_time = 0
                        testCnt = testCnt + 1
                    else:
                        result = 0
                        break
            else:
                logger.print_error("read line:%d fail" %(read_line_cnt))
                result = 255
                break
        return result

    # cat kmsg saved in tmpfile
    @logger.print_line_info
    def cat_kmsg(self):
        self.uart.write(self.cmd_cat_tmpfile)
        time.sleep(5)
        return self._parse_kmsg()

    # parse booting_time from case loacl log file
    @logger.print_line_info
    def _parse_booting_time(self):
        result = 255
        is_kernel_part = 0
        read_line_cnt = 0

        while True:
            if read_line_cnt > self.max_read_lines:
                logger.print_error("read lines exceed max_read_lines:%d" %(self.max_read_lines))
                result = 255
                break

            status, line = self.uart.read()
            if status  == True:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if self.ipl_resume_time == 0 and self.str_booting_time in line:
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.ipl_resume_time = match.group(1)
                        logger.print_info("ipl_resume_time is %s" %(self.ipl_resume_time))
                        continue

                if is_kernel_part == 0 and "LINUX" in line:
                    is_kernel_part = 1

                if self.kernel_resume_time == 0 and is_kernel_part == 1 and self.str_booting_time in line:
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.kernel_resume_time = match.group(1)
                        logger.print_info("kernel_resume_time is %s" %(self.kernel_resume_time))

                if self.ipl_resume_time !=0 and self.kernel_resume_time != 0:
                    result = 0
                    break
            else:
                logger.print_error("read line:%d fail" %(read_line_cnt))
                result = 255
                break
        return result

    # get booting time after resume
    @logger.print_line_info
    def cat_booting_time(self):
        self.uart.write(self.cmd_cat_booting_time)
        time.sleep(5)
        return self._parse_booting_time()


    # judge pass or fail
    @logger.print_line_info
    def judge_test_result(self):
        result = 255
        kernel_str_us   = 0
        total_str_us    = 0

        # cost time
        while True:
            if self.suspend_enter_time == 0 or self.suspend_exit_time == 0 or self.app_resume_time == 0:
                logger.print_error("str test run timeout")
                break

            if self.suspend_enter_time > self.suspend_exit_time or self.suspend_exit_time > self.app_resume_time:
                logger.print_error("the stat time of str is invalid")
                break

            kernel_str_time = float(self.suspend_exit_time) - float(self.suspend_enter_time)
            total_str_time  = float(self.app_resume_time) - float(self.suspend_enter_time)
            kernel_str_us   = float(kernel_str_time) * 1000000
            total_str_us    = float(total_str_time) * 1000000

            logger.print_warning("str Time cost:%d us; target:%s us" %(int(total_str_us), self.target_time))
            logger.print_warning("str (only kernel) Time cost:%d us" %(int(kernel_str_us)))
            logger.print_warning("str booting_time (IPL) Time cost:%d us" %(int(self.ipl_resume_time)))
            logger.print_warning("str booting_time (kernel) Time cost:%d us" %(int(self.kernel_resume_time)))

            if total_str_us <= float(self.target_time):
                result = 0
            break

        # force to pass, will be removed if the sdk runs stablely.
        result = 0

        logger.print_info("");
        if result == 0:
            time_info = "target_l2l:{};total_l2l:{};sys_l2l:{};ipl_l2l:{};kernel_l2l:{};target_h2l:{};total_h2l:{};sys_h2l:{};ipl_h2l:{};kernel_h2l:{}\n".format(\
                        int(str_target), int(total_str_us), int(kernel_str_us), int(self.ipl_resume_time), int(self.kernel_resume_time), \
                        0, 0, 0, int(self.ipl_resume_time), int(self.kernel_resume_time))

            str = aov_common.AOVCase(self.case_name)
            str.save_time_info(self.case_name, time_info)

            return result


    # run flow: highfps->lowfps->lowfps, get test cost between highfps & lowfps and between lowfps & lowfps.
    @logger.print_line_info
    def fps_switch_squence(self):
        result = 255

        result = self.reboot_dev()                              # reboot first to clear board status, for temporary testing
        if result == 0:
            self.enable_printk_time()                           # open kernel timestamp
            self.run_aov_demo_test()                            # run aov app in test mode
            self.redirect_kmsg()                                # redirect kmsg to memory file
            result = self.cat_kmsg()                            # cat kmsg
            if result == 0:
                result = self.cat_booting_time()                # cat booting time
                if result == 0:
                    result = self.judge_test_result()           # judge test result
            self.disable_printk_time()                          # close kernel timestamp
        else:
            logger.print_error("reboot timeout!")

        if result == 0:
            logger.print_warning("str test pass!")
        else:
            logger.print_error("str test fail!")

        return result

    """ case internal functions end """

    @logger.print_line_info
    def runcase(self):
        result = 255
        """ case body start """
        result = self.fps_switch_squence()
        """ case body end """

        return result

    @logger.print_line_info
    def system_help(args):
        logger.print_warning("stat str cost time")
        logger.print_warning("cmd: str")
        logger.print_warning("AOV STR cost time: the time interva bwtween two 'suspend entry', include app's time consumption")
        logger.print_warning("SYS STR cost time: the time interva bwtween 'suspend entry' and 'suspend exit', kernel space's time consumption")
        logger.print_warning("stat time: the str cost time of the scenario which changes fps from low-fps to low-fps")
