import time
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common

class os_switch(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

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

    def runcase(self):
        result = 0
        # step1 判断是否在kernel下
        result = sys_common.goto_kernel(self.uart)
        if result != True:
            logger.print_warning(f"caseName[{self.case_name}] not in kernel!")
            return 255
        # step2 切换到dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.print_warning(f"caseName[{self.case_name}] run done!")
            return 255
        # step3 切换到purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.print_warning(f"caseName[{self.case_name}] run done!")
            return 255

        self.uart.close()
        return 0