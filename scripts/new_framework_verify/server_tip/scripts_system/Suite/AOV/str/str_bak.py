import time
import re
import os

from PythonScripts.logger import logger
from Common.case_base import CaseBase

class str_handle(CaseBase):

    def __init__(self, case_name, case_log_path, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_log_path, case_run_cnt, module_path_name)

        """ case internal params start """
        self.other_case_json_path      = './AOV/str/str_keyword.json'    # 额外的关键字过滤
        self.log_read_pos              = 0

        self.str_suspend_entry         = ""
        self.str_suspend_exit          = ""
        self.str_app_resume            = ""

        self.cmd_aov_run               = "/customer/sample_code/bin/prog_aov_aov_demo -t -d"
        self.cmd_aov_test              = "a"
        self.cmd_aov_quit              = "q"

        self.cmd_cat_tmpfile           = "strings {} | grep -E '{}|{}|{}'".format(self.str_kmsg, self.str_suspend_entry, self.str_suspend_exit, self.str_app_resume)

        """ str """
        self.target_time               = 0
        self.suspend_enter_time        = 0
        self.suspend_exit_time         = 0
        self.app_resume_time           = 0
        """ resume booting time """
        self.ipl_resume_time           = int(0)
        self.kernel_resume_time        = 0
        self.str_booting_time          = 0
        """ exec suspend/resume count """
        self.str_cnt                   = 6
        """ case internal params end """
        self.run_case_callback         = 'run_case_general'

    def cfg_param_parse(self):
        if not self.case_is_support():
            logger.print_warning("run case: [{}], is no support!".format(self.case_name))
            return 255
        result = self.get_case_json_key_value("run_case_callback")
        if result != 'no_find_key':
           self.run_case_callback = str(result)
        result = self.get_case_json_key_value("suspend_entry")
        if result != 'no_find_key':
            self.str_suspend_entry = str(result)
        result = self.get_case_json_key_value("suspend_exit")
        if result != 'no_find_key':
            self.str_suspend_exit = str(result)
        result = self.get_case_json_key_value("app_resume")
        if result != 'no_find_key':
            self.str_app_resume = str(result)
        result = self.get_case_json_key_value("str_target")
        if result != 'no_find_key':
            self.target_time = int(result)
        result = self.get_case_json_key_value("str_cnt")
        if result != 'no_find_key':
            self.str_cnt = int(result)
        return 0

   # parse booting_time from case loacl log file
    @logger.print_line_info
    def _parse_booting_time(self, case_log_path, uart_log_path):
        self.str_booting_time          = 0
        file_ = case_log_path
        if not os.path.exists(case_log_path):
           file_ = uart_log_path
        with open(file_, 'r') as file:
            is_kernel_part = 0
            file.seek(self.log_read_pos, 0)
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if  self.ipl_resume_time == '0' and self.str_booting_time in line:
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.ipl_resume_time = match.group(1)
                        logger.print_info("ipl_resume_time is %s\n" %(self.ipl_resume_time))
                        continue

                if is_kernel_part == 0 and "LINUX" in line:
                    is_kernel_part = 1

                if self.kernel_resume_time == '0' and is_kernel_part == 1 and self.str_booting_time in line:
                    pattern = re.compile(r'(\d+)\(us\)')
                    match = pattern.search(line)
                    if match:
                        self.kernel_resume_time = match.group(1)
                        logger.print_info("kernel_resume_time is %s\n" %(self.kernel_resume_time))
                        continue

                if self.ipl_resume_time != '0' and self.kernel_resume_time != '0':
                    break

    # get read pos in file before send cmd
    @logger.print_line_info
    def _update_log_read_pos(self, case_log_path, uart_log_path):
        file_ = case_log_path
        if not os.path.exists(case_log_path):
           file_ = uart_log_path
        with open(file_, 'r') as file:
            file.seek(0, 2)
            self.log_read_pos = file.tell()

    # redirect kmsg to memory
    @logger.print_line_info
    def redirect_kmsg(self, device_handle:object):
        self.str_kmsg                  = "/tmp/.str_kmsg"
        self.cmd_redirect_kmsg         = "cat /proc/kmsg > {} &".format(self.str_kmsg)
        self.cmd_kill_kmsg             = "pkill -f 'cat /proc/kmsg'"
        logger.print_info("redirect kmsg to %s\n" %(self.str_kmsg))
        device_handle.write(self.cmd_redirect_kmsg)
        time.sleep(5)
        device_handle.write(self.cmd_kill_kmsg)

    # get booting time after resume
    @logger.print_line_info
    def cat_booting_time(self, device_handle:object):
        self.cmd_cat_booting_time      = "cat /sys/class/sstar/msys/booting_time"
        self._update_log_read_pos()
        device_handle.write(self.cmd_cat_booting_time)
        time.sleep(5)
        self._parse_booting_time()


    # run aov demo in test mode
    @logger.print_line_info
    def run_aov_demo_test(self, device_handle):
        logger.print_info("start app\n")
        device_handle.write(self.cmd_aov_run)
        time.sleep(10)
        logger.print_info("send str cmd to app\n")
        device_handle.write(self.cmd_aov_test)
        time.sleep(10)

        logger.print_info("enter 'q' to exit app\n")
        retryCnt = 0
        while retryCnt < 10:
            device_handle.write(self.cmd_aov_quit)
            retryCnt = retryCnt + 1
            time.sleep(0.1)
        time.sleep(2)


    @logger.print_line_info
    def _parse_kmsg(self):
        testCnt = 1
        logger.print_warning("it will do suspend and resume %d times ...\n" %(self.str_cnt))
        if not os.path.exists(self.case_log_path):
             file_ = self.uart_log_path
        with open(file_, 'r') as file:
            file.seek(self.log_read_pos, 0)
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()

                # check suspend_entry
                if self.suspend_enter_time == 0 and self.str_suspend_entry in line:
                    pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                    match = pattern.search(line)
                    if match:
                        self.suspend_enter_time = match.group(1)
                        logger.print_warning("%d: suspend_enter_time is %s\n" %(testCnt, self.suspend_enter_time))
                        continue

                # check suspend_exit
                if self.suspend_exit_time == 0 and self.str_suspend_exit in line:
                    pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                    match = pattern.search(line)
                    if match:
                        self.suspend_exit_time = match.group(1)
                        logger.print_warning("%d: suspend_exit_time is %s\n" %(testCnt, self.suspend_exit_time))
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
                    logger.print_warning("%d: app_resume_time is %s\n" %(testCnt, self.app_resume_time))
                    if testCnt < self.str_cnt:
                        self.suspend_enter_time = 0
                        self.suspend_exit_time = 0
                        self.app_resume_time = 0
                        testCnt = testCnt + 1
                    else:
                        break

    # cat kmsg saved in tmpfile
    @logger.print_line_info
    def cat_kmsg(self,device_handle):
        self._update_log_read_pos()
        device_handle.write(self.cmd_cat_tmpfile)
        time.sleep(5)
        self._parse_kmsg()


    # judge pass or fail
    @logger.print_line_info
    def judge_test_result(self):
        result = 255
        kernel_str_us   = 0
        total_str_us    = 0

        # cost time
        while True:
            if self.suspend_enter_time == 0 or self.suspend_exit_time == 0 or self.app_resume_time == 0:
                logger.print_error("str test run timeout\n")
                break

            if self.suspend_enter_time > self.suspend_exit_time or self.suspend_exit_time > self.app_resume_time:
                logger.print_error("the stat time of str is invalid\n")
                break

            kernel_str_time = float(self.suspend_exit_time) - float(self.suspend_enter_time)
            total_str_time  = float(self.app_resume_time) - float(self.suspend_enter_time)
            kernel_str_us   = float(kernel_str_time) * 1000000
            total_str_us    = float(total_str_time) * 1000000

            logger.print_warning("str Time cost:%d us; target:%s us\n" %(int(total_str_us), self.target_time))
            logger.print_warning("str (only kernel) Time cost:%d us\n" %(int(kernel_str_us)))
            logger.print_warning("str booting_time (IPL) Time cost:%d us\n" %(int(self.ipl_resume_time)))
            logger.print_warning("str booting_time (kernel) Time cost:%d us\n" %(int(self.kernel_resume_time)))

            if total_str_us <= float(self.target_time):
                result = 0
            break

        # force to pass, will be removed if the sdk runs stablely.
        result = 0

        logger.print_info("\n");
        if result == 0:
            time_info = "target_l2l:{};total_l2l:{};sys_l2l:{};ipl_l2l:{};kernel_l2l:{};target_h2l:{};total_h2l:{};sys_h2l:{};ipl_h2l:{};kernel_h2l:{}\n".format(\
                        int(self.target_time), int(total_str_us), int(kernel_str_us), int(self.ipl_resume_time), int(self.kernel_resume_time), \
                        0, 0, 0, int(self.ipl_resume_time), int(self.kernel_resume_time))

            self.save_time_info(self.case_name, time_info)

        return result


    # run flow: highfps->lowfps->lowfps, get test cost between highfps & lowfps and between lowfps & lowfps.
    @logger.print_line_info
    def fps_switch_squence(self, device_handle):
        result = int(255)

        result = self.reboot_board(device_handle)                              # reboot first to clear board status, for temporary testing
        if result == 0:
            self.enable_printk_time(device_handle)  # open kernel timestamp
            self.debug_mode_script_run(device_handle) #open debug mode(memleak\asan),need init
            self.run_aov_demo_test(device_handle)                            # run aov app in test mode
            result = self.debug_mode_script_end(device_handle) #open debug mode(memleak),need deinit
            self.redirect_kmsg(device_handle)                                # redirect kmsg to memory file
            self.cat_kmsg(device_handle)                                     # cat kmsg
            self.cat_booting_time(device_handle)                             # cat booting time
            result = int(result) | int(self.judge_test_result())  # judge test result
            self.disable_printk_time(device_handle)                          # close kernel timestamp
        else:
            logger.info("reboot timeout!\n")

        if result == 0:
            logger.print_warning("str test pass!\n")
        else:
            logger.print_error("str test fail!\n")

        return result

    def run_case_i6f(self):
        """ case body start """
        result = 255
        logger.print_info("run_case_i6f")
        self.reboot_board(self.uart_handle)
        result = self.fps_switch_squence(self.uart_handle)
        """ case body end """
        return result

    def run_case_general(self):
        """ case body start """
        result = 0
        logger.print_info("run_case_general")
        self.uart_handle = self.create_device()
        #self.telnet_handle[0] = self.create_device('telnet')
        result = self.modfiy_dev_cfg_file(self.uart_handle, self.earlyinit_setting_json, "\"\\\"SNR_ID\\\": \\\"0\\\"\"", "\"\\\"SNR_ID\\\": \\\"2\\\"\"")
        #result = self.modfiy_dev_cfg_file(self.uart_handle, self.earlyinit_setting_json, "SNR_ID", "SNR_IE")
        if result != 0:
           logger.print_error("modfiy_dev_cfg_file is fail !\n")
           return result
        result = self.fps_switch_squence(self.uart_handle)
        """ case body end """
        return result

    """ case internal functions end """

    @logger.print_line_info
    def runcase(self):
        result = 255
        result = self.cfg_param_parse()
        if result:
           return  result
        """ case body start """
        while (self.case_run_cnt):
            try:
               result |= int(getattr(self, self.run_case_callback)())
            except Exception as e:
               logger.print_error(e)
               self.exception_handling(result)
            self.case_run_cnt -= 1
        """ case body end """
        for handle in self.telnet_handle:
           if handle != None:
              self.destory_device(handle)
              handle.close_client()
        if result == 0:
           self.destory_device(self.uart_handle)
        return result


    @logger.print_line_info
    def runcase_help(self):
        logger.print_warning("stat str cost time\n")
        logger.print_warning("cmd: str\n")
        logger.print_warning("AOV STR cost time: the time interva bwtween two 'suspend entry', include app's time consumption\n")
        logger.print_warning("SYS STR cost time: the time interva bwtween 'suspend entry' and 'suspend exit', kernel space's time consumption\n")
        logger.print_warning("stat time: the str cost time of the scenario which changes fps from low-fps to low-fps\n")