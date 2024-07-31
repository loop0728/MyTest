import time
from PythonScripts.logger import logger

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
            print("in kernel.")
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

class os_switch_case():
    def __init__(self, client_handle, case_name, case_log_path, case_run_cnt=1):
        self.case_name = case_name
        self.client_handle = client_handle
        self.case_run_cnt = case_run_cnt
        self.case_log_path = case_log_path.replace('uart.log', '') + case_name + '_uart.log'

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
            wait_keyword = "/customer/sample_code/bin #"
            cmd = "cd /customer/sample_code/bin/"
            self.client_handle.write(cmd)
            result, data = self.client_handle.match_keyword_return(wait_keyword)
            if result == False:
                result = 255
                return result
            cmd = "./prog_aov_aov_demo -t"
            self.client_handle.write(cmd)
            time.sleep(15)
            cmd = "c"
            self.client_handle.write(cmd)

        if target_os == "purelinux":
            wait_keyword = "/customer/sample_code/bin #"
            cmd = "cd /customer/sample_code/bin/"
            self.client_handle.write(cmd)
            result, data = self.client_handle.match_keyword_return(wait_keyword)
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

    def runcase(self):
        result = 0
        # step1 判断是否在kernel下
        result = goto_kernel(self.client_handle)
        if result != True:
            logger.print_warning("caseName[{}] not in kernel!\n".format(self.case_name))
            return 0
        # step2 切换到dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.print_warning("caseName[{}] purelinux to dualos fail!\n".format(self.case_name))
            return 0
        # step3 切换到purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.print_warning("caseName[{}] dualos to purelinux fail!\n".format(self.case_name))
            return 0
        return 0


def system_runcase(args, client_handle):
    case_run_cnt = args[1]
    case_name = args[2]
    case_log_path = args[3]
    result = 255
    os_switch_case_handle = os_switch_case(client_handle, case_name, case_log_path, case_run_cnt)
    result = os_switch_case_handle.runcase()
    return result

def system_help(args):
    print("only for OS switch test")
