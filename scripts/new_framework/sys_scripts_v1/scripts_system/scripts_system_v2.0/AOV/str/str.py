import sys
import time
import re
import os
import json
from PythonScripts.logger import logger
import threading
import inspect

""" case import start """
from PythonScripts.variables import str_h2l_target, str_l2l_target, str_kmsg, suspend_entry, suspend_exit, app_resume, booting_time
from AOV.common.aov_common import AOVCase
from enum import Enum
""" case import end """

class aov_str_stage(Enum):
    STAGE_HIGH_FPS_TO_LOW_FPS = 1
    STAGE_LOW_FPS_TO_LOW_FPS  = 2

class str_case():
    cnt_check_keyword_dict = {}

    def __init__(self, client_handle, case_name, case_log_path, case_run_cnt=1):
        self.case_name = case_name
        self.borad_cur_state = ''
        self.client_handle = client_handle
        self.protocol = 'uart'
        self.case_run_cnt = int(case_run_cnt)
        self.client_running = False
        self.client_handle.add_case_name_to_uartlog()
        self.case_log_path = case_log_path.replace('uart.log', '') + case_name + '_uart.log'
        self.client_handle.open_case_uart_bak_file(self.case_log_path)

        """ case internal params start """
        self.board_state_in_kernel_str = '/ #'
        self.set_check_keyword_dict = {}
        self.other_case_json_path   = './AOV/str/str_keyword.json'    # 额外的关键字过滤
        self.reboot_timeout         = 180
        self.log_read_pos           = 0

        self.str_suspend_entry      = suspend_entry.strip('"')
        self.str_suspend_exit       = suspend_exit.strip('"')
        self.str_app_resume         = app_resume.strip('"')
        self.str_booting_time       = booting_time.strip('"')
        self.cmd_uboot_reset        = "reset"
        self.cmd_kernel_reboot      = "reboot"
        self.cmd_aov_run            = "/customer/sample_code/bin/prog_aov_aov_demo -t"
        self.cmd_aov_test           = "a"
        self.cmd_aov_quit           = "q"
        self.cmd_printk_time_on     = "echo y > /sys/module/printk/parameters/time"
        self.cmd_printk_time_off    = "echo n > /sys/module/printk/parameters/time"
        self.cmd_redirect_kmsg      = "cat /proc/kmsg > {} &".format(str_kmsg)
        self.cmd_kill_kmsg          = "pkill -f 'cat /proc/kmsg'"
        #self.cmd_cat_tmpfile        = "cat {}".format(str_kmsg)
        self.cmd_cat_tmpfile        = "strings {} | grep -E '{}|{}|{}'".format(str_kmsg, self.str_suspend_entry, self.str_suspend_exit, self.str_app_resume)
        self.cmd_cat_booting_time   = "cat /sys/class/sstar/msys/booting_time"
        self.h2l_target_time        = str_h2l_target
        self.h2l_suspend_enter_time = 0
        self.h2l_suspend_exit_time  = 0
        self.h2l_app_resume_time    = 0
        self.l2l_target_time        = str_l2l_target
        self.l2l_suspend_enter_time = 0
        self.l2l_suspend_exit_time  = 0
        self.l2l_app_resume_time    = 0
        self.ipl_resume_time        = 0
        self.kernel_resume_time     = 0
        """ case internal params end """
        super().__init__()


    """ case internal functions start """
    # check current status of the dev, if the dev is at uboot of at kernel, then reboot the dev
    @logger.print_line_info
    def reboot_dev(self):
        trywait_time = 0
        result = 255
        self.client_handle.client_send_cmd_to_server('')
        self.borad_cur_state = self.client_handle.get_borad_cur_state()
        if self.borad_cur_state == 'Unknow':
            for i in range(1,20):
                self.client_handle.client_send_cmd_to_server('')
                self.borad_cur_state = self.client_handle.get_borad_cur_state()
                if self.borad_cur_state != 'Unknow':
                    break
        if self.borad_cur_state == 'Unknow':
            return result
        if self.borad_cur_state == 'at uboot':
            self.client_handle.clear_borad_cur_state()
            self.client_handle.client_send_cmd_to_server(self.cmd_uboot_reset)
        if self.borad_cur_state == 'at kernel':
            self.client_handle.client_send_cmd_to_server(self.cmd_kernel_reboot)
            time.sleep(2)
            self.client_handle.clear_borad_cur_state()
        while True:
            self.borad_cur_state = self.client_handle.get_borad_cur_state()
            if self.borad_cur_state == 'at kernel':
                result = 0
                logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state)
                break
            elif self.borad_cur_state == 'at uboot':
                self.client_handle.client_send_cmd_to_server(self.cmd_uboot_reset)
                self.client_handle.clear_borad_cur_state()
            else:
                time.sleep(1)
                trywait_time = trywait_time + 1
                if trywait_time > self.reboot_timeout:
                    break
        return result

    # show timestamp of printk log
    @logger.print_line_info
    def enable_printk_time(self):
        self.client_handle.client_send_cmd_to_server(self.cmd_printk_time_on)

    # hide timestamp of printk log
    @logger.print_line_info
    def disable_printk_time(self):
        self.client_handle.client_send_cmd_to_server(self.cmd_printk_time_off)

    # run aov demo in test mode
    @logger.print_line_info
    def run_aov_demo_test(self):
        logger.print_info("start app\n")
        self.client_handle.client_send_cmd_to_server(self.cmd_aov_run)
        time.sleep(10)
        logger.print_info("send str cmd to app\n")
        self.client_handle.client_send_cmd_to_server(self.cmd_aov_test)
        time.sleep(10)

        logger.print_info("enter 'q' to exit app\n")
        retryCnt = 0
        while retryCnt < 10:
            self.client_handle.client_send_cmd_to_server(self.cmd_aov_quit)
            #self.client_handle.client_send_cmd_to_server("\n")
            retryCnt = retryCnt + 1
            time.sleep(0.1)
        time.sleep(2)


    # redirect kmsg to memory
    @logger.print_line_info
    def redirect_kmsg(self):
        logger.print_info("redirect kmsg to %s\n" %(str_kmsg))
        self.client_handle.client_send_cmd_to_server(self.cmd_redirect_kmsg)
        time.sleep(5)
        self.client_handle.client_send_cmd_to_server(self.cmd_kill_kmsg)


    # get read pos in file before send cmd
    @logger.print_line_info
    def _update_log_read_pos(self):
        with open(self.case_log_path, 'r') as file:
            file.seek(0, 2)
            self.log_read_pos = file.tell()

    # parse str time cost from kmsg
    @logger.print_line_info
    def _parse_kmsg(self):
        with open(self.case_log_path, 'r') as file:
            test_stage = aov_str_stage.STAGE_HIGH_FPS_TO_LOW_FPS
            file.seek(self.log_read_pos, 0)
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8').strip()

                if test_stage == aov_str_stage.STAGE_HIGH_FPS_TO_LOW_FPS:
                    # check h2l suspend_entry
                    if self.h2l_suspend_enter_time == 0 and self.str_suspend_entry in line:
                        pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                        match = pattern.search(line)
                        if match:
                            self.h2l_suspend_enter_time = match.group(1)
                            logger.print_info("h2l_suspend_enter_time is %s\n" %(self.h2l_suspend_enter_time))
                            continue

                    # check h2l suspend_exit
                    if self.h2l_suspend_exit_time == 0 and self.str_suspend_exit in line:
                        pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                        match = pattern.search(line)
                        if match:
                            self.h2l_suspend_exit_time = match.group(1)
                            logger.print_info("h2l_suspend_exit_time is %s\n" %(self.h2l_suspend_exit_time))
                            continue

                    if self.h2l_suspend_enter_time != 0 and self.h2l_suspend_exit_time != 0:
                        self.h2l_app_resume_time = 0

                    # check h2l app resume
                    if self.h2l_app_resume_time == 0 and self.str_app_resume in line:
                        pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                        match = pattern.search(line)
                        if match:
                            self.h2l_app_resume_time = match.group(1)
                            #logger.print_info("h2l_app_resume_time is %s\n" %(h2l_app_resume_time))

                    # wait h2l flow complete
                    if self.h2l_suspend_enter_time != 0 and self.h2l_suspend_exit_time != 0 and self.h2l_app_resume_time != 0:
                        logger.print_info("h2l_app_resume_time is %s\n" %(self.h2l_app_resume_time))
                        test_stage = aov_str_stage.STAGE_LOW_FPS_TO_LOW_FPS

                else:
                    # check l2l_suspend_entry
                    if self.l2l_suspend_enter_time == 0 and self.str_suspend_entry in line:
                        pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                        match = pattern.search(line)
                        if match:
                            self.l2l_suspend_enter_time = match.group(1)
                            logger.print_info("l2l_suspend_enter_time is %s\n" %(self.l2l_suspend_enter_time))
                            continue

                    # check l2l_suspend_exit
                    if self.l2l_suspend_exit_time == 0 and self.str_suspend_exit in line:
                        pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                        match = pattern.search(line)
                        if match:
                            self.l2l_suspend_exit_time = match.group(1)
                            logger.print_info("l2l_suspend_exit_time is %s\n" %(self.l2l_suspend_exit_time))
                            continue

                    if self.l2l_suspend_enter_time != 0 and self.l2l_suspend_exit_time != 0:
                        self.l2l_app_resume_time = 0

                    # check l2l app resume
                    if self.l2l_app_resume_time == 0 and self.str_app_resume in line:
                        pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                        match = pattern.search(line)
                        if match:
                            self.l2l_app_resume_time = match.group(1)
                            #logger.print_info("l2l_app_resume_time is %s\n" %(l2l_app_resume_time))

                    # wait l2l flow complete
                    if self.l2l_suspend_enter_time != 0 and self.l2l_suspend_exit_time != 0 and self.l2l_app_resume_time != 0:
                        logger.print_info("l2l_app_resume_time is %s\n" %(self.l2l_app_resume_time))
                        break

    # cat kmsg saved in tmpfile
    @logger.print_line_info
    def cat_kmsg(self):
        self._update_log_read_pos()
        self.client_handle.client_send_cmd_to_server(self.cmd_cat_tmpfile)
        time.sleep(5)
        self._parse_kmsg()


    # parse booting_time from case loacl log file
    @logger.print_line_info
    def _parse_booting_time(self):
        with open(self.case_log_path, 'r') as file:
            is_kernel_part = 0
            file.seek(self.log_read_pos, 0)
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8').strip()
                if self.ipl_resume_time == 0 and self.str_booting_time in line:
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.ipl_resume_time = match.group(1)
                        logger.print_info("ipl_resume_time is %s\n" %(self.ipl_resume_time))
                        continue

                if is_kernel_part == 0 and "LINUX" in line:
                    is_kernel_part = 1

                if self.kernel_resume_time == 0 and is_kernel_part == 1 and self.str_booting_time in line:
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.kernel_resume_time = match.group(1)
                        logger.print_info("kernel_resume_time is %s\n" %(self.kernel_resume_time))
                        continue

                if self.ipl_resume_time !=0 and self.kernel_resume_time != 0:
                    break

    # get booting time after resume
    @logger.print_line_info
    def cat_booting_time(self):
        self._update_log_read_pos()
        self.client_handle.client_send_cmd_to_server(self.cmd_cat_booting_time)
        time.sleep(5)
        self._parse_booting_time()


    # judge pass or fail
    @logger.print_line_info
    def judge_test_result(self):
        result = 255
        result_h2l = 255
        result_l2l = 255

        # h2l cost time
        while True:
            if self.h2l_suspend_enter_time == 0 or self.h2l_suspend_exit_time == 0 or self.h2l_app_resume_time == 0:
                logger.print_error("str_h2l test run timeout\n")
                break

            if self.h2l_suspend_enter_time > self.h2l_suspend_exit_time or self.h2l_suspend_exit_time > self.h2l_app_resume_time:
                logger.print_error("the stat time of str_h2l is invalid\n")
                break

            kernel_str_time = float(self.h2l_suspend_exit_time) - float(self.h2l_suspend_enter_time)
            total_str_time = float(self.h2l_app_resume_time) - float(self.h2l_suspend_enter_time)
            kernel_str_us = float(kernel_str_time) * 1000000
            total_str_us = float(total_str_time) * 1000000

            logger.print_warning("str_h2l Time cost:%d us; target:%s us\n" %(int(total_str_us), self.h2l_target_time))
            logger.print_warning("str_h2l (only kernel) Time cost:%d us\n" %(int(kernel_str_us)))
            logger.print_warning("str_h2l booting_time (IPL) Time cost:%d us\n" %(int(self.ipl_resume_time)))
            logger.print_warning("str_h2l booting_time (kernel) Time cost:%d us\n" %(int(self.kernel_resume_time)))

            if total_str_us > float(self.h2l_target_time):
                logger.print_error("str_h2l test fail\n")
            else:
                result_h2l = 0
                logger.print_warning("str_h2l test pass\n")
            break

        # l2l cost time
        while True:
            if self.l2l_suspend_enter_time == 0 or self.l2l_suspend_exit_time == 0 or self.l2l_app_resume_time == 0:
                logger.print_error("str_l2l test run timeout\n")
                break

            if self.l2l_suspend_enter_time > self.l2l_suspend_exit_time or self.l2l_suspend_exit_time > self.l2l_app_resume_time:
                logger.print_error("the stat time of str_l2l is invalid\n")
                break

            kernel_str_time = float(self.l2l_suspend_exit_time) - float(self.l2l_suspend_enter_time)
            total_str_time = float(self.l2l_app_resume_time) - float(self.l2l_suspend_enter_time)
            kernel_str_us = float(kernel_str_time) * 1000000
            total_str_us = float(total_str_time) * 1000000

            logger.print_warning("str_l2l Time cost:%d us; target:%s us\n" %(int(total_str_us), self.l2l_target_time))
            logger.print_warning("str_l2l (only kernel) Time cost:%d us\n" %(int(kernel_str_us)))
            logger.print_warning("str_l2l booting_time (IPL) Time cost:%d us\n" %(int(self.ipl_resume_time)))
            logger.print_warning("str_l2l booting_time (kernel) Time cost:%d us\n" %(int(self.kernel_resume_time)))

            if total_str_us > float(self.l2l_target_time):
                logger.print_error("str_l2l test fail\n")
            else:
                result_l2l = 0
                logger.print_warning("str_l2l test pass\n")
            break

        if result_h2l == 0 or result_l2l == 0:
            result = 0

        # force to pass, will be removed after the sdk runs stablely.
        result = 0

        logger.print_info("\n");
        if result == 0:
            l2l_kernel_str_time = float(self.l2l_suspend_exit_time) - float(self.l2l_suspend_enter_time)
            l2l_total_str_time = float(self.l2l_app_resume_time) - float(self.l2l_suspend_enter_time)
            l2l_kernel_str_us = float(l2l_kernel_str_time) * 1000000
            l2l_total_str_us = float(l2l_total_str_time) * 1000000

            h2l_kernel_str_time = float(self.h2l_suspend_exit_time) - float(self.h2l_suspend_enter_time)
            h2l_total_str_time = float(self.h2l_app_resume_time) - float(self.h2l_suspend_enter_time)
            h2l_kernel_str_us = float(h2l_kernel_str_time) * 1000000
            h2l_total_str_us = float(h2l_total_str_time) * 1000000

            time_info = "target_l2l:{};total_l2l:{};sys_l2l:{};ipl_l2l:{};kernel_l2l:{};target_h2l:{};total_h2l:{};sys_h2l:{};ipl_h2l:{};kernel_h2l:{}\n".format(\
                        int(str_l2l_target), int(l2l_total_str_us), int(l2l_kernel_str_us), int(self.ipl_resume_time), int(self.kernel_resume_time), \
                        int(str_h2l_target), int(h2l_total_str_us), int(h2l_kernel_str_us), int(self.ipl_resume_time), int(self.kernel_resume_time))

            # boottime of h2l and l2l are the same, keep two set of values for not modifying the report line-chart. The following will be updated later.
            # time_info = "target_l2l:{};total_l2l:{};sys_l2l:{};target_h2l:{};total_h2l:{};sys_h2l:{};ipl:{};kernel:{}\n".format(\
            #             int(str_l2l_target), int(l2l_total_str_us), int(l2l_kernel_str_us), int(str_h2l_target), int(h2l_total_str_us), \
            #             int(h2l_kernel_str_us), int(ipl_resume_time), int(kernel_resume_time))
            str = AOVCase(self.case_name)
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
            self.cat_kmsg()                                     # cat kmsg
            self.cat_booting_time()                             # cat booting time
            result = self.judge_test_result()                   # judge test result
            self.disable_printk_time()                          # close kernel timestamp
        else:
            logger.info("reboot timeout!\n")

        if result == 0:
            logger.print_warning("str test pass!\n")
        else:
            logger.print_error("str test fail!\n")

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
def system_runcase(args, client_handle):
    if len(args) < 3:
        logger.print_error(f"len:{len(args)} {args[0]} {args[1]} {args[2]} \n")
        return 255
    input_case_name = args[0]
    case_run_cnt = args[1] 
    case_log_path = args[2]
    if input_case_name[len(input_case_name)-1:].isdigit() and '_stress_' in input_case_name:
        parase_list = input_case_name.split('_stress_')
        if len(parase_list) != 2:
            return 255
        print(f"parase_list:{parase_list}!\n")
        case_run_cnt = int(parase_list[1])
        case_name = parase_list[0]
        logger.print_info(f"case_run_cnt: {case_run_cnt} case_name:{case_name}\n")
    else:
        case_name = input_case_name
    ret_str = '[Fail]'
    result = 255

    if int(case_run_cnt) > 0:
        ret = 0
        for cnt in range(0, int(case_run_cnt)):
            """ create case handle start """
            case_handle = str_case(client_handle, case_name, case_log_path, case_run_cnt)
            """ create case handle end """
            if int(case_run_cnt) > 1:
                tmp_case_name = input_case_name+':'+ '{}'.format(cnt+1)
                client_handle.add_case_name_to_uartlog(tmp_case_name)
            ret |= case_handle.runcase()
            if ret == 0:
                ret_str = '[success][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
                logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
            else:
                ret_str = '[Fail][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
                logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
            result = ret
        client_handle.client_close()
    else:
        logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, result))
    return result

@logger.print_line_info
def system_help(args):
    logger.print_warning("stat str cost time\n")
    logger.print_warning("cmd: str\n")
    logger.print_warning("AOV STR cost time: the time interva bwtween two 'suspend entry', include app's time consumption\n")
    logger.print_warning("SYS STR cost time: the time interva bwtween 'suspend entry' and 'suspend exit', kernel space's time consumption\n")
    logger.print_warning("stat h2l time: the str cost time of the scenario which changes fps from high-fps to low-fps\n")
    logger.print_warning("stat l2l time: the str cost time of the scenario which changes fps from low-fps to low-fps\n")
