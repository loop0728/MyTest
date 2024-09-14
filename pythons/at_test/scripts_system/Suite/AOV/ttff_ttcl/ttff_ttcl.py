import re
import os
import time
from Suite.AOV.ttff_ttcl.ttff_ttcl_var import ttff_target, ttcl_target
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common

class ttff_ttcl(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

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
        # 检查串口信息
        res = self.uart.write(cmd)
        if res is False:
            logger.print_error(f"{self.uart} is disconnected.")
            return "Unknown"
        wait_keyword = "0"
        status, data = self.uart.read()
        if status  == True:
            if wait_keyword in data:
                result = "dualos"
                return result
            else:
                result = "purelinux"
                return result
        else:
            result = "Unknown"
            return result

    def switch_os(self, target_os):
        result = 0
        cur_os = self.get_current_os()
        if cur_os == target_os:
            logger.print_warning(f"[{self.case_name}] current os is match {target_os}")
            return 0

        logger.print_warning(f"will switch to OS({target_os})!")
        if target_os == "dualos":
            cmd = "cd /customer/sample_code/bin/"
            self.uart.write(cmd)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = self.uart.read()
            if status  == True:
                if wait_keyword not in data:
                    return 255
            else:
                logger.print_error(f"Read fail,no keyword: {wait_keyword}")
                return 255
            cmd = "./prog_aov_aov_demo -t"
            self.uart.write(cmd)
            time.sleep(10)
            cmd = "c"
            self.uart.write(cmd)

        if target_os == "purelinux":
            cmd = "cd /customer/sample_code/bin/"
            self.uart.write(cmd)
            time.sleep(1)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = self.uart.read()
            if status == True:
                if wait_keyword not in data:
                    result = 255
                    return result

            cmd = "./prog_preload_linux -t"
            wait_keyword = "press c to change mode"
            result, data = sys_common.write_and_match_keyword(self.uart, cmd, wait_keyword)
            if result == False:
                return 255

            cmd = "c"
            self.uart.write(cmd)

        time.sleep(20)
        return result

    def get_ttff_ttcl(self):
        result = 0
        ttff_time_value = 0
        ttcl_time_value = 0

        cmd = "cat /sys/class/sstar/msys/booting_time"
        wait_keyword = "VIF ch0 int 0"
        result, ret_match_buffer = sys_common.write_and_match_keyword(self.uart, cmd, wait_keyword)
        if result == False:
            result = 255
            return result
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode('utf-8', errors='replace').strip()
        if "diff" in ret_match_buffer and "VIF" in ret_match_buffer:
            logger.print_info(f"ret_match_buffer:{ret_match_buffer}")
            pattern = re.compile(r'time:\s+(\d+),.*int*')
            match = pattern.search(ret_match_buffer)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttff_time_value = match.group(1)
                if ttff_time_value != 'int':
                    ttff_time_value = int(ttff_time_value)
                logger.print_info(f"TTFF Time value:{ttff_time_value}; target:{ttff_target}")

        cmd = "cat /sys/class/sstar/msys/booting_time"
        wait_keyword = "ramdisk_execute_command"
        result, ret_match_buffer = sys_common.write_and_match_keyword(self.uart, cmd, wait_keyword)
        if result == False:
            result = 255
            return result
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode('utf-8', errors='replace').strip()
        if "diff" in ret_match_buffer and "ramdisk_execute_command" in ret_match_buffer:
            logger.print_info(f"ret_match_buffer:{ret_match_buffer}")
            pattern = re.compile(r'time:\s+(\d+),.*ramdisk_execute_command\+')
            match = pattern.search(ret_match_buffer)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttcl_time_value = match.group(1)
                if type(ttcl_time_value) != 'int':
                    ttcl_time_value = int(ttcl_time_value)
                logger.print_info(f"TTCL Time value:{ttcl_time_value}; target:{ttcl_target}")

        time_info = f"TTFF_target:{ttff_target};TTFF:{ttff_time_value};TTCL_target:{ttcl_target};TTCL:{ttcl_time_value}"
        self.save_time_info(self.case_name, time_info)
        if ttff_time_value == 0 or ttff_time_value > ttff_target:
            logger.print_warning(f"ttff time [{ttff_time_value}] is error target[{ttff_target}]!")
            result = 255
        if ttcl_time_value == 0 or ttcl_time_value > ttcl_target:
            logger.print_warning(f"ttcl time [{ttcl_time_value}] is error, target[{ttcl_target}]!")
            result = 255

        return result

    def runcase(self):
        # step1 判断是否在kernel下
        result = sys_common.goto_kernel(self.uart)
        if result != True:
            logger.print_warning(f"caseName[{self.case_name}] not in kernel!")
            return 0
        # step2 切换到dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.print_warning(f"caseName[{self.case_name}] run done!")
            return 0
        # step3 cat booting time
        result = self.get_ttff_ttcl()
        # step4 切换到purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.print_warning(f"caseName[{self.case_name}] run done!")
            return 0

        self.uart.close()
        return 0