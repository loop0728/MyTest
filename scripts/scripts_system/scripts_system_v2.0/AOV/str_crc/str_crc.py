import sys
import time
import re
import threading
from logger import logger

from uartlog_contrl import uartlog_contrl
from uart_record import uartlog_contrl_handle
from variables import str_crc_ok, str_crc_fail, uboot_prompt, kernel_prompt, suspend_crc_start_addr, suspend_crc_end_addr

uboot_handler           = None
uboot_thread_run        = False
uboot_stage             = 0

kernel_handler          = None
kernel_thread_run       = False
kernel_stage            = 0

judge_handler           = None
judge_thread_run        = False
is_suspend_crc_on       = 0

is_set_bootargs_fail    = 0
is_boot_up_fail         = 0
is_change_bootargs_fail = 0

str_crc_handler         = None
str_crc_thread_run      = False
#result, 0: not match; 1: success; 2: fail
str_crc_rst             = 0

result                  = 0

"""
brief:
- thread function, check whether enter in uboot stage
"""
def handle_uboot_stage():
    global uboot_thread_run
    global uboot_stage
    uboot_stage = 0

    uboot_prompt_str = uboot_prompt.strip('"')

    while uboot_thread_run is True:
        cur_line = uartlog_contrl_handle.get_searia_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if uboot_prompt_str in cur_line:
            uboot_stage = 1
            break

        time.sleep(0.0001)

"""
brief:
- thread function, check whether enter in kernel stage
"""
def handle_kernel_stage():
    global kernel_thread_run
    global kernel_stage
    kernel_stage = 0
    kernel_prompt_str = kernel_prompt.strip('"')

    while kernel_thread_run is True:
        cur_line = uartlog_contrl_handle.get_searia_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if kernel_prompt_str in cur_line:
            kernel_stage = 1
            break

        time.sleep(0.0001)

def check_uboot_stage_with_enter(timeout):
    enterCnt = 0

    while uboot_stage == 0:
        logger.info("check_uboot_stage_with_enter: %s \n" %enterCnt)
        uartlog_contrl_handle.send_command("\n")
        enterCnt = enterCnt + 1
        if enterCnt > timeout * 10:
            break
        time.sleep(0.1)
    time.sleep(1)

def check_kernel_stage(timeout):
    enterCnt = 0
    while kernel_stage == 0:
        enterCnt = enterCnt + 1
        if enterCnt > timeout * 10:
            break
        time.sleep(0.1)
    time.sleep(1)

def set_crc_env():
    suspend_crc_bootargs = "suspend_crc=" + str(suspend_crc_start_addr) + "," + str(suspend_crc_end_addr)
    #logger.info("suspend_crc_bootargs is %s\n" %suspend_crc_bootargs)
    cmd_crc_env = "setenv suspend_crc_env ${bootargs_linux_only} " + suspend_crc_bootargs

    uartlog_contrl_handle.send_command("")
    time.sleep(1)
    uartlog_contrl_handle.send_command("setenv default_env ${bootargs_linux_only}")
    time.sleep(1)
    uartlog_contrl_handle.send_command(cmd_crc_env)
    time.sleep(1)
    uartlog_contrl_handle.send_command("setenv bootargs_linux_only ${suspend_crc_env}")
    time.sleep(1)
    uartlog_contrl_handle.send_command("saveenv")
    time.sleep(1)
    uartlog_contrl_handle.send_command("reset")

def recovery_default_env():
    uartlog_contrl_handle.send_command("")
    time.sleep(1)
    uartlog_contrl_handle.send_command("setenv bootargs_linux_only ${default_env}")
    time.sleep(1)
    uartlog_contrl_handle.send_command("setenv default_env")
    time.sleep(1)
    uartlog_contrl_handle.send_command("setenv suspend_crc_env")
    time.sleep(1)
    uartlog_contrl_handle.send_command("saveenv")
    time.sleep(1)
    uartlog_contrl_handle.send_command("reset")



"""
brief:
- switch bootargs between suspend_crc on and suspend_crc off.

param:
- suspend_crc_state: current bootargs status. 0, not set suspend_crc; 1, has set suspend_crc.
"""
def change_bootargs(suspend_crc_state):
    global uboot_handler
    global uboot_thread_run
    global is_set_bootargs_fail
    global uboot_stage

    is_set_bootargs_fail = 0
    uboot_stage = 0
    uboot_thread_run = True
    uboot_handler = threading.Thread(target=handle_uboot_stage)
    uboot_handler.start()

    logger.info("reboot to change bootargs\n")
    uartlog_contrl_handle.send_command("reboot")
    check_uboot_stage_with_enter(20)

    uboot_thread_run = False
    uboot_handler.join()

    logger.info("uboot_stage is %s\n" %uboot_stage)
    if uboot_stage == 1:
        global kernel_handler
        global kernel_thread_run
        global is_boot_up_fail

        kernel_thread_run = True
        kernel_handler = threading.Thread(target=handle_kernel_stage)
        kernel_handler.start()
        time.sleep(5)

        if suspend_crc_state == "0":
            logger.info("set_crc_env\n")
            set_crc_env()
        else:
            logger.info("recovery_default_env\n")
            recovery_default_env()

        time.sleep(20)
        logger.info("check kernel stage\n")
        uartlog_contrl_handle.send_command("")
        time.sleep(1)
        uartlog_contrl_handle.send_command("lsmod")
        check_kernel_stage(10)

        logger.info("kernel_stage is %s\n" %kernel_stage)
        if kernel_stage == 0:
            logger.warning("boot up timeout\n")
            is_boot_up_fail = 1
    else:
        logger.warning("reboot timeout\n")
        is_set_bootargs_fail = 1

"""
brief:
- thread function, check whether suspend_crc is enabled in cmdline
"""
def handle_check_cmdline():
    global judge_thread_run
    global is_suspend_crc_on
    is_cmd_match = 0

    while judge_thread_run is True:
        cur_line = uartlog_contrl_handle.get_searia_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if is_cmd_match == 0 and "cat /proc/cmdline" in cur_line:
            is_cmd_match = 1

        if is_cmd_match == 1 and "root=" in cur_line:
            #logger.info("bootargs is %s\n" %cur_line)
            suspend_crc_bootargs="suspend_crc=" + str(suspend_crc_start_addr) + "," + str(suspend_crc_end_addr)
            #logger.info("suspend_crc_bootargs is %s\n" %suspend_crc_bootargs)

            if str(suspend_crc_bootargs) in cur_line:
                is_suspend_crc_on = 1
                logger.info("suspend_crc is enabled\n")
            else:
                is_suspend_crc_on = 0
                logger.info("suspend_crc is disabled\n")

            break

        time.sleep(0.0001)

"""
brief:
- check whether the cmdline contains the setting of suspend_crc

return:
- 0, suspend_crc off; 1, suspend_crc on
"""
def check_cmdline_suspend_crc():
    global judge_handler
    global judge_thread_run

    judge_thread_run = True
    judge_handler = threading.Thread(target=handle_check_cmdline)
    judge_handler.start()

    uartlog_contrl_handle.send_command("cat /proc/cmdline")
    time.sleep(2)

    judge_thread_run = False
    judge_handler.join()

    return is_suspend_crc_on


"""
brief:
- check bootargs and judge if add suspend_crc param or not.

param:
- suspend_crc_state: current bootargs status. 0, not set suspend_crc; 1, has set suspend_crc.
"""
def adjust_suspend_crc(suspend_crc_state):
    global is_change_bootargs_fail
    global result
    result = 0
    is_change_bootargs_fail = 0

    suspend_crc_state_1 = check_cmdline_suspend_crc()
    logger.info("is_suspend_crc_on:%s, suspend_crc_state_1:%s, suspend_crc_state:%s\n" %(is_suspend_crc_on, suspend_crc_state_1, suspend_crc_state))

    if str(suspend_crc_state_1) == suspend_crc_state:
        #logger.info("start to change bootargs\n")
        change_bootargs(suspend_crc_state)

        if is_set_bootargs_fail == 0 and is_boot_up_fail == 0:
            suspend_crc_state_2 = check_cmdline_suspend_crc()
            if suspend_crc_state_1 == suspend_crc_state_2:
                logger.warning("change bootargs timeout\n")
                is_change_bootargs_fail = 1
            else:
                logger.info("change bootargs ok\n")

"""
brief:
- thread function, check whether the str crc test is ok
"""
def handle_str_crc():
    global parse_thread_run
    global str_crc_rst
    cur_line = ""
    str_crc_rst = 0
    str_crc_ok_str=str_crc_ok.strip('"')
    str_crc_fail_str=str_crc_fail.strip('"')

    while str_crc_thread_run is True:
        cur_line = uartlog_contrl_handle.get_searia_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if str_crc_ok_str in cur_line:
            str_crc_rst = 1
            break

        if str_crc_fail_str in cur_line:
            str_crc_rst = 2
            break

        time.sleep(0.0001)

"""
brief:
- do str crc test.
"""
def str_crc_test():
    global str_crc_handler
    global str_crc_thread_run
    global result
    str_crc_thread_run = True

    str_crc_handler = threading.Thread(target=handle_str_crc)
    str_crc_handler.start()

    uartlog_contrl_handle.send_command("echo 10 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
    time.sleep(1)
    uartlog_contrl_handle.send_command("echo mem > /sys/power/state")
    logger.info("send str cmd\n")

    time.sleep(15)
    str_crc_thread_run = False
    str_crc_handler.join()

    logger.info("check str crc\n")
    if str_crc_rst == 1:
        logger.info("STR CRC test success\n")
    elif str_crc_rst == 2:
        logger.warning("STR CRC test fail\n")
        result = 255
    else:
        result = 255


def system_runcase(args):
    global result
    global is_set_bootargs_fail
    global is_boot_up_fail
    global is_change_bootargs_fail

    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0
    is_set_bootargs_fail = 0
    is_boot_up_fail = 0
    is_change_bootargs_fail = 0

    logger.info("uboot_prompt is %s, kernel_prompt is %s, suspend_crc_start_addr is %s, suspend_crc_end_addr is %s\n" %(uboot_prompt, kernel_prompt, suspend_crc_start_addr, suspend_crc_end_addr))

    logger.info("check and set suspend_crc env\n")
    adjust_suspend_crc("0")

    # do test
    if is_set_bootargs_fail == 0 and is_boot_up_fail == 0 and is_change_bootargs_fail == 0:
        str_crc_test()
    else:
        result = 255

    logger.info("check and remove suspend_crc env\n")
    adjust_suspend_crc("1")

    if is_set_bootargs_fail != 0 or is_boot_up_fail != 0 or is_change_bootargs_fail != 0 or result == 255:
        logger.warning("case %s run timeout\n" %Case_Name)
        result = 255

    return result

def system_help(args):
    print("stat str crc test")
    print("cmd : echo 3 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
    print("cmd : echo mem > /sys/power/state")
    print("if the result return 'CRC check success', test pass; if the result return 'CRC check fail', test fail.")

