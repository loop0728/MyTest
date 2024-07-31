import re
import os
import time
from AOV.ttff_ttcl.ttff_ttcl_var import ttff_target, ttcl_target
from PythonScripts.logger import logger
import common.system_common as system_common


def goto_uboot(client_handle):
    client_handle.write("reboot")
    keyword = 'Loading Environment'
    result = client_handle.match_keyword_return(keyword)
    if result == True:
        client_handle.write("")
        client_handle.write("")
        client_handle.write("")
        client_handle.write("")
        client_handle.write("")

    keyword = 'SigmaStar #'
    result = client_handle.match_keyword_return(keyword)
    if result == True:
        logger.print_info("in uboot\n")
        return True
    else:
        return False

def goto_kernel(client_handle, reset_wait_time = 20, retry = 3):
    """ 进入 kernel cmdline """
    result = False
    while retry > 0:
        keyword = '/ #'
        client_handle.write("cd /")
        wait_time = 2
        result, data = client_handle.match_keyword_return(keyword, wait_time)
        if result == True:
            logger.print_info("in kernel.")
            return True
        keyword = 'SigmaStar #'
        client_handle.write("")
        result, data = client_handle.match_keyword_return(keyword, wait_time)
        if result == True:
            client_handle.write("reset")
            time.sleep(reset_wait_time)
        retry -= 1
    logger.print_error("goto kernel timeout!\n")
    return False

class ttff_ttcl_case():
    def __init__(self, client_handle, case_name, case_log_path, case_run_cnt=1):
        self.case_name = case_name
        self.client_handle = client_handle
        self.case_run_cnt = case_run_cnt
        self.case_log_path = case_log_path.replace('uart.log', '') + case_name + '_uart.log'

    def save_time_info(self, name, info):
        file = None
        result = 0
        filePath = "out/{}/time.txt".format(name)
        try:
            directory = os.path.dirname(filePath)
            os.makedirs(directory, exist_ok=True)
            file = open(filePath, "w")
            file.write(info)
        except FileNotFoundError:
            result = 255
        except PermissionError:
            result = 255
        finally:
            if file is not None:
                file.close()
        return result

    def get_current_os(self):
        result = ""
        cmd = "lsmod | grep mi_sys | wc -l"
        check_keyword = "0"
        # 检查串口信息
        self.client_handle.write(cmd)
        result, data = self.client_handle.match_keyword_return(check_keyword)
        if result == False:
            result = "purelinux"
            return result
        else:
            result = "dualos"
            return result

    def switch_os(self, target_os):
        result = 0
        cur_os = self.get_current_os()
        if cur_os == target_os:
            logger.print_warning("[{}] current os is match {}\n".format(self.case_name, target_os))
            return 0

        logger.print_warning("will switch to OS({})!\n".format(target_os))
        if target_os == "dualos":
            cmd = "cd /customer/sample_code/bin/"
            self.client_handle.write(cmd)
            wait_time = 2
            wait_keyword = "/customer/sample_code/bin #"
            result, data = self.client_handle.match_keyword_return(wait_keyword, wait_time)
            if result == False:
                result = 255
                return result
            cmd = "./prog_aov_aov_demo -t"
            self.client_handle.write(cmd)
            time.sleep(15)
            cmd = "c"
            self.client_handle.write(cmd)

        if target_os == "purelinux":
            cmd = "cd /customer/sample_code/bin/"
            self.client_handle.write(cmd)
            wait_time = 2
            wait_keyword = "/customer/sample_code/bin #"
            result, data = self.client_handle.match_keyword_return(wait_keyword, wait_time)
            if result == False:
                result = 255
                return result

            cmd = "./prog_preload_linux -t"
            self.client_handle.write(cmd)
            time.sleep(15)
            cmd = "c"
            self.client_handle.write(cmd)

        time.sleep(20)
        return result

    def get_ttff_ttcl(self):
        result = 0
        wait_time = 2
        ttff_time_value = 0
        ttcl_time_value = 0

        cmd = "cat /sys/class/sstar/msys/booting_time"
        self.client_handle.write(cmd)
        wait_keyword = "/ #"
        result, data = self.client_handle.match_keyword_return(wait_keyword, wait_time)
        if result == False:
            result = 255
            return result
        time.sleep(2)
        cmd = "cat /sys/class/sstar/msys/booting_time | grep 'VIF ch0 int 0'"
        self.client_handle.write(cmd)
        wait_keyword = "diff"
        result, ret_match_buffer = self.client_handle.match_keyword_return(wait_keyword, wait_time)
        if result == False:
            result = 255
            return result
        print("TTFF time log")
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode('utf-8').strip()
        if "diff" in ret_match_buffer and "VIF" in ret_match_buffer:
            logger.info("ret_match_buffer:%s\n" %(ret_match_buffer))
            pattern = re.compile(r'time:\s+(\d+),.*int*')
            match = pattern.search(ret_match_buffer)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttff_time_value = match.group(1)
                if ttff_time_value != 'int':
                    ttff_time_value = int(ttff_time_value)
                logger.info("TTFF Time value:%s; target:%s\n" %(ttff_time_value, ttff_target))
        time.sleep(2)
        cmd = "cat /sys/class/sstar/msys/booting_time | grep ramdisk_execute_command"
        self.client_handle.write(cmd)
        wait_keyword = "diff"
        result, ret_match_buffer = self.client_handle.match_keyword_return(wait_keyword, wait_time)
        if result == False:
            result = 255
            return result
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode('utf-8').strip()
        if "diff" in ret_match_buffer and "ramdisk_execute_command" in ret_match_buffer:
            logger.info("ret_match_buffer:%s\n" %(ret_match_buffer))
            pattern = re.compile(r'time:\s+(\d+),.*ramdisk_execute_command\+')
            match = pattern.search(ret_match_buffer)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttcl_time_value = match.group(1)
                if type(ttcl_time_value) != 'int':
                    ttcl_time_value = int(ttff_time_value)
                logger.info("TTCL Time value:%s; target:%s\n" %(ttcl_time_value, ttcl_target))

        time_info = f"TTFF_target:{ttff_target};TTFF:{ttff_time_value};TTCL_target:{ttcl_target};TTCL:{ttcl_time_value}\n"
        self.save_time_info(self.case_name, time_info)
        if ttff_time_value == 0 or ttff_time_value > ttff_target:
            logger.warning("ttff time [%s] is error target[%s]!\n" %(ttff_time_value, ttff_target))
            result = 255
        if ttcl_time_value == 0 or ttcl_time_value > ttcl_target:
            logger.warning("ttcl time [%s] is error, target[%s]!\n" %(ttcl_time_value, ttcl_target))
            result = 255

        return result

    def runcase(self):
        result = 0
        # step1 判断是否在kernel下
        result = goto_kernel(self.client_handle)
        if result != True:
            logger.warning("caseName[{}] not in kernel!\n".format(self.case_name))
            return 0
        # step2 切换到dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.warning("caseName[{}] run done!\n".format(self.case_name))
            return 0
        # step3 cat booting time
        result = self.get_ttff_ttcl()
        # step4 切换到purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.warning("caseName[{}] run done!\n".format(self.case_name))
            return 0
        return 0


def system_runcase(args, client_handle):
    case_run_cnt = args[1]
    case_name = args[2]
    case_log_path = args[3]
    ttff_ttcl_case_handle = ttff_ttcl_case(client_handle, case_name, case_log_path, case_run_cnt)
    result = ttff_ttcl_case_handle.runcase()
    return result

def system_help(args):
    print("cat ttff/ttcl time")
    print("cmd : cat /sys/class/sstar/msys/booting_time")
    print("check TTFF: 006 time:  xxx, diff: 1, run_EIB, 0")
    print("check TTCL: 010 time:  xxx, diff: 358, ramdisk_execute_command+, 1456")