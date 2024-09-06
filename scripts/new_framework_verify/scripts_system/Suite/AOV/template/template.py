import sys
import time
import re
import os
import json
from PythonScripts.logger import logger
import threading
import inspect

""" case import start """

""" case import end """

class template_case():
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
        self.set_check_keyword_dict = {'bug on':0, 'unknown symbol': 0, 'Call trace':0, 'Exception stack':0, 'oom-killer':0, 'fifo full bypass':0, 'Sensor is abnormal':0}
        self.other_case_json_path = './AOV/template/template_keyword.json'    # 额外的关键字过滤
        self.reboot_timeout = 180
        #""" case internal params end """
        super().__init__()

    """ case internal functions start """
    # eg.1: cmd which dose not need return
    @logger.print_line_info
    def get_ls_info(self):
        self.client_handle.client_send_cmd_to_server("ls")
        return 0


    # eg.2: cmd which needs parse single line
    """
    获取设备 LX_MEM 大小：
    / # cat /proc/cmdline
    root=/dev/ram rdinit=/linuxrc initrd=0x21800000,0x60000 rootwait LX_MEM=0x10000000 mma_heap=mma_heap_name0,
        miu=0,sz=0xb000000 mma_memblock_remove=1 cma=2M disable_rtos=1 loglevel=3 mtdparts=nor0:0x5F000(BOOT),
        0x1000(ENV),0x240000(KERNEL),0x210000(rootfs),0xE0000(MISC),0x240000(RO_FILES),0x170000(RTOS),
        0x60000(RAMDISK),0x400000(miservice),0x260000(customer) nohz=off
    """
    @logger.print_line_info
    def get_lx_mem_size(self):
        self.lx_mem_size = ''
        result = 255
        lx_mem_key = "LX_MEM="
        cmd = 'cat /proc/cmdline'
        wait_keyword = self.board_state_in_kernel_str
        check_keyword = 'root='
        cmd_exc_sta,ret_buf,ret_match_buffer = self.client_handle.client_send_cmd_to_server(cmd, True, wait_keyword, check_keyword, 10)
        if cmd_exc_sta == 'run_ok':
            logger.print_info(f"check_cmdline_info cmd_exc_sta:{cmd_exc_sta}, ret_buf:{ret_buf} ret_match_buffer:{ret_match_buffer},check_keyword:{check_keyword}\n")
            logger.print_info(f"lx_mem_key:{lx_mem_key}\n")
            if lx_mem_key in ret_match_buffer:
                # parse ret_match_buffer
                parts = ret_match_buffer.split()
                for part in parts:
                    if part.startswith(lx_mem_key):
                        self.lx_mem_size = part[len(lx_mem_key):]
                        logger.print_info(f"success,lx_mem_size:{self.lx_mem_size}\n")
                        result = 0
                        break
        else:
            if cmd_exc_sta == 'cmd_no_run':
                logger.print_error(f"fail,wait_keyword:{wait_keyword}, exec cmd:{cmd}:cmd is not excuted\n")
        if result == 255:
            logger.print_error(f"fail,wait_keyword:{wait_keyword}, exec cmd:{cmd}:cmd runs error\n")
        return result

    # eg.3: cmd which needs parse multi line and save multi results
    """
    deal flow:
    1. send cmd, not need return
    2. open case log file to parse line by line, save results
    3. judge results
    """
    @logger.print_line_info
    def get_ipl_kernel_boot_time(self):
        self.ipl_total_time    = ""
        self.kernel_total_time = ""
        cmd = 'cat /proc/cmdline'
        # send cmd
        self.client_handle.client_send_cmd_to_server(cmd)
        time.sleep(5)
        # parse case log file
        # parse self.case_log_path
        with open(self.case_log_path, 'r') as file:
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                # deal stuff

        # judge results

    """ case internal functions end """

    @logger.print_line_info
    def runcase(self):
        result = 255
        """ case body start """
        #result = self.get_ls_info()
        result = self.get_lx_mem_size()
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
            case_handle = template_case(client_handle, case_name, case_log_path, case_run_cnt)
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
    logger.print_warning("script template, not executable\n")
