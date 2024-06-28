import time
from logger import logger

class change_fps_case():
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

    def TargetBufferGetTime(self):
        """ 获取检测到人形之后得到buffer的时间 """
        BufferGetTime = 0 # 初始化默认时间 ms
        cmd = "a"
        wait_keyword = "no_check"
        check_keyword = "[AUTO TEST]TargetBufferGet cost"
        wait_time = self.cmd_a_wait_time
        # 获取串口一行信息
        cmd_exc_sta,ret_buf,ret_match_buffer = self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, wait_time)
        if cmd_exc_sta == 'run fail':
            logger.print_error("[change_fps] {} run fail!".format(cmd))
            return BufferGetTime
        # 如果是字节串，则解码成字符串
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode('utf-8').strip()
        if "[AUTO TEST]TargetBufferGet cost" in ret_match_buffer:
            value = ret_match_buffer.split('=')[1].strip()
            BufferGetTime = int(value)
        return BufferGetTime

    def CompBufferGetTime(self, BufferGetTime):
        """ 判断时间是否满足要求 """
        result = 0
        if BufferGetTime == 0:
            logger.print_error("[change_fps] get time fail!\n")
            result = 255
        if  BufferGetTime > self.threshold_time:
            logger.print_error("[change_fps] {} > {}\n".format(BufferGetTime, self.threshold_time))
            result = 255
        return result

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
                logger.print_info("[change_fps] at kernel!\n")
                break
            time.sleep(self.reset_wait_time)
            try_cnt = try_cnt + 1
            if try_cnt > self.goto_kernel_retry:
                logger.print_error("goto kernel timeout!\n")
                return 255
        return result

    def quit_demo(self):
        """ 退出aov demo """
        self.client_handle.client_send_cmd_to_server("q")
        time.sleep(2)
        self.client_handle.client_send_cmd_to_server("")
        time.sleep(5)
        self.client_handle.client_send_cmd_to_server("cd /")
        cur_env = self.client_handle.get_borad_cur_state()
        if cur_env == 'at kernel':
            return 0
        else:
            return 255

    def runcase(self):
        result = 255
        # step1 判断是否在kernel下
        result = self.goto_kernel()
        if result != 0:
            return result
        # step2 进入aov demol
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
        time.sleep(10)
        # step3 下发高低帧率切换命令,获取切换时间
        BufferGetTime = self.TargetBufferGetTime()
        # step4 判断时间是否正确
        result_tmp = self.CompBufferGetTime(BufferGetTime)
        if result_tmp != 0:
            logger.print_error("[change_fps] {} get time FAIL!\n".format(self.case_name))
            result = result_tmp
        else:
            logger.print_info("[change_fps] time is {}ms!\n".format(BufferGetTime))
        # step5 退出aov demo
        result_tmp = self.quit_demo()
        if result_tmp != 0:
            logger.print_error("[change_fps] {} quit aov demo FAIL!\n".format(self.case_name))
            result = result_tmp
        return result


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
            change_fps_case_handle = change_fps_case(client_handle, case_name, case_log_path, case_run_cnt)
            if int(case_run_cnt) > 1:
                tmp_case_name = input_case_name+':'+ '{}'.format(cnt+1)
                client_handle.add_case_name_to_uartlog(tmp_case_name)
            ret = change_fps_case_handle.runcase()
            if ret == 0:
                ret_str = '[success][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
                logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
            else:
                ret_str = '[Fail][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
                logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
                if change_fps_case_handle.return_way == 'have_fail_return':
                    return ret
            result = ret
        client_handle.client_close()
    else:
        logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, result))
    return result

def system_help(args):
    print("change fps case")
