import sys
import os
import time
import re
import threading
from logger import logger

from uartlog_contrl import uartlog_contrl
from uart_record import uartlog_contrl_handle
from variables import ttff_target, ttcl_target

sys.path.append("..")
from AOV.common.aov_common import AOVCase

parse_handler      = None
parse_thread_run   = False
ttff_time_value = 0
ttcl_time_value = 0

def handle_parse():
    global parse_thread_run
    global ttff_time_value
    global ttcl_time_value
    cur_line = ""

    while parse_thread_run is True:
        cur_line = uartlog_contrl_handle.get_searia_buf()
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if ttff_time_value == 0 and "diff" in cur_line and "VIF" in cur_line:
            logger.info("cur_line:%s\n" %(cur_line))
            pattern = re.compile(r'time:\s+(\d+),.*int*')
            match = pattern.search(cur_line)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttff_time_value = match.group(1)
                logger.info("TTFF Time value:%s; target:%s\n" %(ttff_time_value, ttff_target))

        if ttcl_time_value == 0 and "diff" in cur_line and "ramdisk_execute_command" in cur_line:
            pattern = re.compile(r'time:\s+(\d+),.*ramdisk_execute_command\+')
            match = pattern.search(cur_line)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttcl_time_value = match.group(1)
                logger.info("TTCL Time value:%s; target:%s\n" %(ttcl_time_value, ttcl_target))

        if ttff_time_value != 0 and ttcl_time_value != 0:
            break;

        time.sleep(0.0001)

def get_current_os():
    global uartlog_contrl_handle
    cur_line = ""
    try_cnt = 0

    uartlog_contrl_handle.send_command("if [ $(lsmod | grep mi_sys | wc -l) == 0 ]; then  echo dualos; else echo purelinux; fi;")
    time.sleep(0.1)
    while True:
        cur_line = uartlog_contrl_handle.get_searia_buf()
        # 如果是字节串，则解码成字符串
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()
        #logger.warning("current line log is [%s]!\n" %(cur_line))
        if cur_line == "dualos" or cur_line == "purelinux":
            logger.warning("current os is %s\n" %(cur_line))
            break;

        if cur_line == "/ #":
            uartlog_contrl_handle.send_command("if [ $(lsmod | grep mi_sys | wc -l) == 0 ]; then  echo dualos; else echo purelinux; fi;")

        time.sleep(0.1)
        try_cnt = try_cnt + 1
        if try_cnt > 200:
            logger.warning("get current os timeout\n")
            result = ""
            return result

    return cur_line

def switch_os(target_os):
    global uartlog_contrl_handle
    result = 0
    try_cnt = 0
    cur_os  = ""
    uartlog_contrl_handle.send_command("\n")
    while True:
        uartlog_contrl_handle.send_command("\n")
        cur_env = uartlog_contrl_handle.get_borad_cur_state()
        if cur_env == 'at uboot':
            uartlog_contrl_handle.send_command("reset")
        elif cur_env == 'at kernel':
            logger.warning("run to command line!\n")
            break

        time.sleep(20)
        try_cnt = try_cnt + 1
        if try_cnt > 2:
            logger.warning("get env timeout\n")
            result = 255
            return result

    cur_os = get_current_os()
    if cur_os == target_os:
        logger.warning("current os is match %s\n" %(target_os))
        return 0

    logger.warning("will switch to OS(%s)!\n" %(target_os))
    if target_os == "dualos":
        uartlog_contrl_handle.send_command("cd /customer/sample_code/bin/")
        uartlog_contrl_handle.send_command("./prog_aov_aov_demo -t")
        time.sleep(15)
        uartlog_contrl_handle.send_command("c")

    if target_os == "purelinux":
        uartlog_contrl_handle.send_command("cd /customer/sample_code/bin/")
        uartlog_contrl_handle.send_command("./prog_preload_linux -t")
        time.sleep(15)
        uartlog_contrl_handle.send_command("c")

    time.sleep(20)

    return result

def system_runcase(args):
    global uartlog_contrl_handle
    global parse_handler
    global parse_thread_run
    global ttff_time_value
    global ttcl_time_value
    global time_file
    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0
    try_cnt = 0
    cur_line = ""
    uartlog_contrl_handle.open_case_uart_bak_file('./'+Case_Name+'_uart.log')

    result = switch_os("dualos")
    if result == 255:
        uartlog_contrl_handle.close_case_uart_bak()
        logger.warning("caseName[%s] run done!\n" %(Case_Name))
        return result

    #create thread to recv and parse log from serial
    parse_thread_run = True
    parse_handler = threading.Thread(target=handle_parse)
    parse_handler.start()

    uartlog_contrl_handle.send_command("cat /sys/class/sstar/msys/booting_time")
    time.sleep(3)
    while ttff_time_value == 0:
        uartlog_contrl_handle.send_command("cat /sys/class/sstar/msys/booting_time | grep 'VIF ch0 int 0'")
        time.sleep(0.1)
        try_cnt = try_cnt + 1
        if try_cnt > 20:
            result = 255
            break

    try_cnt = 0
    while ttcl_time_value == 0:
        uartlog_contrl_handle.send_command("cat /sys/class/sstar/msys/booting_time | grep ramdisk_execute_command")

        time.sleep(0.1)
        try_cnt = try_cnt + 1
        if try_cnt > 20:
            result = 255
            break

    parse_thread_run = False
    parse_handler.join()

    result = switch_os("purelinux")
    uartlog_contrl_handle.close_case_uart_bak()

    time_info = f"TTFF_target:{ttff_target};TTFF:{ttff_time_value};TTCL_target:{ttcl_target};TTCL:{ttcl_time_value}\n"
    ttff_ttcl = AOVCase(Case_Name)
    ttff_ttcl.save_time_info(Case_Name, time_info)

    if ttff_time_value == 0 or ttff_time_value > ttff_target:
        logger.warning("ttff time [%s] is error target[%s]!\n" %(ttff_time_value, ttff_target))
        result = 255
    if ttcl_time_value == 0 or ttcl_time_value > ttcl_target:
        logger.warning("ttcl time [%s] is error, target[%s]!\n" %(ttcl_time_value, ttcl_target))
        result = 255

    logger.warning("caseName[%s] run done!\n" %(Case_Name))
    return 0

def system_help(args):
    print("cat ttff/ttcl time")
    print("cmd : cat /sys/class/sstar/msys/booting_time")
    print("check TTFF: 006 time:  xxx, diff: 1, run_EIB, 0")
    print("check TTCL: 010 time:  xxx, diff: 358, ramdisk_execute_command+, 1456")
