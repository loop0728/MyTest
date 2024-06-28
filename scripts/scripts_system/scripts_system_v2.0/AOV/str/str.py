import sys
import time
import re
import threading
from logger import logger

from uartlog_contrl import uartlog_contrl
from uart_record import uartlog_contrl_handle
from variables import str_target, str_kmsg

parse_handler      = None
parse_thread_run   = True
suspend_enter_time = 0
suspend_exit_time  = 0
app_resume_time    = 0

def handle_parse():
    global parse_thread_run
    global suspend_enter_time
    global suspend_exit_time
    global app_resume_time
    cur_line = ""
    try_time = 0
    while parse_thread_run is True:
        #获取串口一行信息
        cur_line = uartlog_contrl_handle.get_searia_buf()
        # 如果是字节串，则解码成字符串
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if suspend_enter_time == 0 and "PM: suspend entry" in cur_line:
            pattern = re.compile(r'\d+\.\d+')
            match = pattern.search(cur_line)
            if match:
                suspend_enter_time = match.group(0)
                logger.info("suspend_enter_time is %s\n" %(suspend_enter_time))
                continue

        if suspend_exit_time == 0 and "PM: suspend exit" in cur_line:
            pattern = re.compile(r'\d+\.\d+')
            match = pattern.search(cur_line)
            if match:
                suspend_exit_time = match.group(0)
                logger.info("suspend_exit_time is %s\n" %(suspend_exit_time))
                continue

        if app_resume_time == 0 and "PM: app resume" in cur_line:
            pattern = re.compile(r'\d+\.\d+')
            match = pattern.search(cur_line)
            if match:
                app_resume_time = match.group(0)
                logger.info("app_resume_time is %s\n" %(app_resume_time))

        if suspend_enter_time !=0 and suspend_exit_time != 0 and app_resume_time != 0:
            break

        time.sleep(0.0001)

def redirect_kmsg():
    command_redirect="cat /proc/kmsg > {} &".format(str_kmsg)
    uartlog_contrl_handle.send_command(command_redirect)
    logger.info("redirect kmsg to %s\n" %(str_kmsg))
    time.sleep(3)
    uartlog_contrl_handle.send_command("pkill -f 'cat /proc/kmsg'")
    #uartlog_contrl_handle.send_command("pgrep -l 'cat /proc/kmsg' | awk '{print $1}' | xargs kill -9")


#无App运行场景测试
def system_runcase(args):
    global handle_parse
    global parse_thread_run
    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0
    #重定向kmsg到指定的文件
    redirect_kmsg()

    #执行suspend & resume操作
    #App运行场景测试
    #uartlog_contrl_handle.send_command("str")
    #no App运行场景测试
    uartlog_contrl_handle.send_command("echo 5 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
    uartlog_contrl_handle.send_command("echo mem > /sys/power/state")
    logger.info("send str cmd\n")
    time.sleep(7)

    #重定向kmsg到指定的文件进行覆盖
    redirect_kmsg()

    #创建接收和解析线程，接收和解析串口接收的log
    parse_thread_run = True
    parse_handler = threading.Thread(target=handle_parse)
    parse_handler.start()
    time.sleep(1)

    #读取保存kmsg的文件内容到串口
    command_cat_tmpfile="cat {}".format(str_kmsg)
    uartlog_contrl_handle.send_command(command_cat_tmpfile)
    logger.info("read log file and parse\n")
    time.sleep(3)

    #判断结果, 删除保存的文件
    parse_thread_run = False
    parse_handler.join()

    while True:
        if suspend_enter_time == 0 or suspend_exit_time == 0 or app_resume_time == 0:
            logger.warning("case %s run timeout\n" %Case_Name)
            result = 255
            break

        if suspend_enter_time > suspend_exit_time or suspend_exit_time > app_resume_time:
            logger.error("the stat time of str is invalid\n")
            result = 255
            break

        kernel_str_time = float(suspend_exit_time) - float(suspend_enter_time)
        total_str_time = float(app_resume_time) - float(suspend_enter_time)
        kernel_str_us = float(kernel_str_time) * 1000000
        total_str_us = float(total_str_time) * 1000000

        logger.info("STR Time cost:%d; target:%s\n" %(int(total_str_us), str_target))
        logger.info("STR (only kernel) Time cost:%d\n" %(int(kernel_str_time)))

        if total_str_us > float(str_target):
            logger.info("STR test fail\n")
            result = 255
        else:
            logger.info("STR test pass\n")

        break

    command_del_tmpfile="rm {}".format(str_kmsg)
    uartlog_contrl_handle.send_command(command_del_tmpfile)

    return result

def system_help(args):
    print("stat str cost time")
    print("cmd : str")
    print("AOV STR cost time：the time interva bwtween two 'suspend entry', include app's time consumption")
    print("SYS STR cost time：the time interva bwtween 'suspend entry' and 'suspend exit', kernel space's time consumption")
