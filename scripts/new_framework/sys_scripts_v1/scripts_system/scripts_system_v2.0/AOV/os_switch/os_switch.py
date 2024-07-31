import time
from logger import logger

class os_switch_case():
    def __init__(self, client_handle, case_name, case_log_path, case_run_cnt=1):
        self.case_name = case_name
        self.borad_cur_state = ''
        self.client_handle = client_handle
        self.protocol = 'uart'
        self.case_run_cnt = case_run_cnt
        self.client_running = False
        self.case_log_path = case_log_path.replace('uart.log', '') + case_name + '_uart.log'
        self.reset_wait_time = 20
        self.cmd_a_wait_time = 5
        self.threshold_time = 1000
        self.goto_kernel_retry = 3
        self.return_way = 'still_case_run_cnt_to_0' #'have_fail_return'

    def goto_kernel(self):
        """ 进入 kernel cmdline """
        result = 0
        try_cnt = 1
        self.client_handle.client_send_cmd_to_server("cd /")
        while True:
            cur_env = self.client_handle.get_borad_cur_state()
            if cur_env == 'at uboot':
                self.client_handle.client_send_cmd_to_server("reset")
            elif cur_env == 'at kernel':
                logger.print_info("[{}] at kernel!\n".format(self.case_name))
                break
            time.sleep(self.reset_wait_time)
            try_cnt = try_cnt + 1
            if try_cnt > self.goto_kernel_retry:
                logger.print_error("goto kernel timeout!\n")
                return 255
        return result

    def get_current_os(self):
        result = ""
        cmd = "lsmod | grep mi_sys | wc -l"
        wait_keyword = "no_check"
        check_keyword = "0"
        wait_time = self.cmd_a_wait_time
        # 获取串口一行信息
        cmd_exc_sta,ret_buf,ret_match_buffer = self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)
        if cmd_exc_sta == 'run_fail':
            logger.print_error("[{}] {} run fail!".format(self.case_name, cmd))
            result = "purelinux"
            return result
        else:
            logger.warning("[{}] {}\n".format(self.case_name, ret_match_buffer))
            result = "dualos"
            return result

    def switch_os(self, target_os):
        result = 0
        cur_os = self.get_current_os()
        if cur_os == target_os:
            logger.warning("[{}] current os is match %s\n".format(self.case_name, target_os))
            return 0

        logger.warning("will switch to OS({})!\n".format(target_os))
        if target_os == "dualos":
            cmd = "cd /customer/sample_code/bin/"
            wait_keyword = "/ #"
            check_keyword = ""
            wait_time = 1
            self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)
            cmd = "./prog_aov_aov_demo -t"
            wait_keyword = "/customer/sample_code/bin #"
            check_keyword = ""
            wait_time = 5
            self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)
            time.sleep(15)
            cmd = "c"
            wait_keyword = "no_check"
            check_keyword = ""
            wait_time = 60
            self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)

        if target_os == "purelinux":
            cmd = "cd /customer/sample_code/bin/"
            wait_keyword = "/ #"
            check_keyword = ""
            wait_time = 1
            self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)
            cmd = "./prog_preload_linux -t"
            wait_keyword = "/customer/sample_code/bin #"
            check_keyword = ""
            wait_time = 5
            self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)
            time.sleep(15)
            cmd = "c"
            wait_keyword = "no_check"
            check_keyword = ""
            wait_time = 60
            self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)

        time.sleep(20)
        return result

    def runcase(self):
        result = 0
        # step1 判断是否在kernel下
        result = self.goto_kernel()
        if result != 0:
            logger.warning("caseName[{}] not in kernel!\n".format(self.case_name))
            return 0
        # step2 切换到dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.warning("caseName[{}] purelinux to dualos fail!\n".format(self.case_name))
            return 0
        # step3 切换到purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.warning("caseName[{}] dualos to purelinux fail!\n".format(self.case_name))
            return 0
        return 0


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
            os_switch_case_handle = os_switch_case(client_handle, case_name, case_log_path, case_run_cnt)
            if int(case_run_cnt) > 1:
                tmp_case_name = '{}:{}'.format(input_case_name, cnt+1)
                client_handle.add_case_name_to_uartlog(tmp_case_name)
            ret = os_switch_case_handle.runcase()
            if ret == 0:
                ret_str = '[success][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
                logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
            else:
                ret_str = '[Fail][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
                logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
                if os_switch_case_handle.return_way == 'have_fail_return':
                    return ret
            result = ret
        client_handle.client_close()
    else:
        logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, result))
    return result

def system_help(args):
    print("only for OS switch test")
