import sys
import time
import re
from logger import logger

from uartlog_contrl import uartlog_contrl
from uart_record import uartlog_contrl_handle
from variables import ttff_target, ttcl_target


def system_runcase(args):
    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0
    uartlog_contrl_handle.open_case_uart_bak_file('./'+Case_Name+'_uart.log')
    uartlog_contrl_handle.send_command("cat /sys/class/sstar/msys/booting_time")
    ttff_time_value = 0
    ttcl_time_value = 0
    cur_line = ""
    try_time = 0
    while True:
        #获取串口一行信息
        cur_line = uartlog_contrl_handle.get_searia_buf()
        # 如果是字节串，则解码成字符串
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if ttff_time_value == 0 and "005 time:" in cur_line and "OSJMP" in cur_line:
            pattern = re.compile(r'005 time:\s+(\d+),.*OSJMP\+')
            match = pattern.search(cur_line)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttff_time_value = match.group(1)
                logger.info("TTFF Time value:%s; target:%s\n" %(ttff_time_value, ttff_target))
                if ttff_time_value > ttff_target:
                    logger.error("TTFF out of target\n")
                    result = 255

        if ttcl_time_value == 0 and "ramdisk_execute_command" in cur_line:
            pattern = re.compile(r'time:\s+(\d+),.*ramdisk_execute_command\+')
            match = pattern.search(cur_line)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的时间字符串
                ttcl_time_value = match.group(1)
                logger.info("TTCL Time value:%s; target:%s\n" %(ttcl_time_value, ttcl_target))
                if ttcl_time_value > ttcl_target:
                    logger.error("TTCL out of target\n")
                    result = 255
                break;
        time.sleep(0.001)
        try_time = try_time + 1
        if try_time > 5000:
            logger.warning("case%s run timeout\n" %Case_Name)
            result = 255
            break;
    uartlog_contrl_handle.close_case_uart_bak()
    return result

def system_help(args):
    print("cat ttff/ttcl time")
    print("cmd : cat /sys/class/sstar/msys/booting_time")
    print("check TTFF: 005 time:  xxx, diff: 44, OSJMP+")
    print("check TTCL: 008 time:  xxx, diff: 358, ramdisk_execute_command+, 1456")
