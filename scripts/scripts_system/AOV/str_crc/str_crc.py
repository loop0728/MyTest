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
boot_key_stage          = 0

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
    global boot_key_stage
    uboot_stage = 0
    boot_key_stage = 0

    uboot_prompt_str = "SigmaStar #"

    while uboot_thread_run is True:
        cur_line = uartlog_contrl_handle.get_serial_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if "U-Boot" in cur_line:
            #logger.info("press any key to enter uboot cmdline\n")
            boot_key_stage = 1

        if boot_key_stage == 1 and uboot_prompt_str in cur_line:
            logger.info("run in uboot\n")
            uboot_stage = 1
            break

        time.sleep(0.001)

"""
brief:
- thread function, check whether enter in kernel stage
"""
def handle_kernel_stage():
    global kernel_thread_run
    global kernel_stage
    kernel_stage = 0
    #kernel_prompt_str = kernel_prompt.strip('"')
    kernel_prompt_str = "/ #"

    prekernel = 0

    while kernel_thread_run is True:
        cur_line = uartlog_contrl_handle.get_serial_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if "Starting kernel" in cur_line:
            prekernel = 1

        if prekernel == 1 and kernel_prompt_str in cur_line:
            kernel_stage = 1
            break

        time.sleep(0.001)

def check_uboot_stage_with_enter(timeout):
    enterCnt = 0

    #logger.info("check_uboot_stage_with_enter: %s \n" %enterCnt)
    while True:
        if boot_key_stage == 1:
            uartlog_contrl_handle.send_command("\n")
            enterCnt = enterCnt + 1
            if uboot_stage == 1:
                break
            if enterCnt > timeout * 100:
                break
        time.sleep(0.01)

def check_kernel_stage(timeout):
    enterCnt = 0
    while kernel_stage == 0:
        enterCnt = enterCnt + 1
        if enterCnt > timeout * 100:
            break
        time.sleep(0.01)

def set_crc_env():
    suspend_crc_bootargs = "suspend_crc=" + str(suspend_crc_start_addr) + "," + str(suspend_crc_end_addr)
    #logger.info("suspend_crc_bootargs is %s\n" %suspend_crc_bootargs)
    cmd_crc_env = "setenv suspend_crc_env ${bootargs_linux_only} " + suspend_crc_bootargs

    uartlog_contrl_handle.send_command("\n")
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
    if dev_default_crc == 0:
        logger.info("remove suspend_crc\n")
        uartlog_contrl_handle.send_command("\n")
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
    else:
        logger.info("suspend_crc has been set defaultly, not need to remove\n")
        uartlog_contrl_handle.send_command("\n")
        time.sleep(1)
        uartlog_contrl_handle.send_command("reset")


"""
brief:
- switch bootargs between suspend_crc on and suspend_crc off.

param:
- expect_crc_state: expect the crc state should be. 0, not set suspend_crc; 1, has set suspend_crc.
"""
def change_bootargs(expect_crc_state):
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
    check_uboot_stage_with_enter(10)

    uboot_thread_run = False
    uboot_handler.join()

    logger.info("uboot_stage is %s\n" %uboot_stage)
    if uboot_stage == 1:
        global kernel_handler
        global kernel_thread_run
        global is_boot_up_fail

        if expect_crc_state == "0":
            logger.info("set_crc_env\n")
            set_crc_env()
        else:
            logger.info("recovery_default_env\n")
            recovery_default_env()

        kernel_thread_run = True
        kernel_handler = threading.Thread(target=handle_kernel_stage)
        kernel_handler.start()

        check_kernel_stage(40)
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

    suspend_crc_bootargs="suspend_crc=" + str(suspend_crc_start_addr) + "," + str(suspend_crc_end_addr)
    #logger.info("suspend_crc_bootargs is %s\n" %suspend_crc_bootargs)

    while judge_thread_run is True:
        cur_line = uartlog_contrl_handle.get_serial_buf()

        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if is_cmd_match == 0 and "cat /proc/cmdline" in cur_line:
            is_cmd_match = 1

        if is_cmd_match == 1 and "root=" in cur_line:
            if str(suspend_crc_bootargs) in cur_line:
                is_suspend_crc_on = 1
                logger.info("suspend_crc is enabled\n")
            else:
                is_suspend_crc_on = 0
                logger.info("suspend_crc is disabled\n")

            break

        time.sleep(0.00001)

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
    time.sleep(1)

    uartlog_contrl_handle.send_command("cat /proc/cmdline")
    time.sleep(2)

    judge_thread_run = False
    judge_handler.join()

    return is_suspend_crc_on


"""
brief:
- check bootargs and judge if add suspend_crc param or not.

param:
- expect_crc_state: current bootargs status. 0, not set suspend_crc; 1, has set suspend_crc.

test flow:
    adjust_suspend_crc("0"):
    expect_not_set_crc(0) -> actual_not_set_crc(0) -> set crc
    expect_not_set_crc(0) -> actual_set_crc(1)

    adjust_suspend_crc("1"):
    expect_set_crc(1) -> actual_set_crc(1) -> remove crc
    expect_set_crc(1) -> actual_set_crc(0)  // impossible
"""
def  adjust_suspend_crc(expect_crc_state):
    global is_change_bootargs_fail
    global result
    result = 0
    is_change_bootargs_fail = 0

    suspend_crc_state_1 = check_cmdline_suspend_crc()
    logger.info("is_suspend_crc_on:%s, suspend_crc_state_1:%s, expect_crc_state:%s\n" %(is_suspend_crc_on, suspend_crc_state_1, expect_crc_state))

    need_to_change_bootargs = 0

    if str(suspend_crc_state_1) == expect_crc_state:
        if expect_crc_state == "0":
            logger.info("device has not set suspend_crc, should reboot to set suspend_crc\n")
            need_to_change_bootargs = 1
        else:
            if dev_default_crc == 0:
                logger.info("device has set suspend_crc, should reboot to remove suspend_crc\n")
                need_to_change_bootargs = 1

        if need_to_change_bootargs == 1:
            change_bootargs(expect_crc_state)
            suspend_crc_state_2 = check_cmdline_suspend_crc()

            if suspend_crc_state_1 == suspend_crc_state_2:
                logger.warning("change bootargs timeout\n")
                is_change_bootargs_fail = 1
            else:
                logger.info("change bootargs ok\n")
    else:
        if expect_crc_state == "0":
            logger.info("device has already set suspend_crc, doesn't need to change bootargs\n")
        else:
            logger.info("could never happen\n")

    return suspend_crc_state_1

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
        cur_line = uartlog_contrl_handle.get_serial_buf()

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

check_boot_handler = None
check_boot_thread_run = False
# boot state, 0: booting; 1: uboot; 2: kernel
E_STATE_BOOTING   = 0
E_STATE_UBOOT     = 1
E_STATE_PREKERNEL = 2
E_STATE_KERNEL    = 3
boot_state        = E_STATE_BOOTING

# isReboot, 0: only check; 1: check & reboot
def handle_check_boot():
    global check_boot_thread_run
    global boot_state

    boot_state = E_STATE_BOOTING
    cur_line = ""

    # debug
    global debug_cur_line_blank
    debug_cur_line_blank = 0

    uboot_prompt_str = "SigmaStar #"
    prekernel_prompt_str = "Starting kernel"
    kernel_prompt_str = "/ #"
    is_run_in_uboot = 0

    while check_boot_thread_run == True:
        cur_line = uartlog_contrl_handle.get_serial_buf()
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if boot_state == E_STATE_BOOTING and uboot_prompt_str in cur_line:
            boot_state = E_STATE_UBOOT
            logger.info("initial state: run in uboot, do reset\n")
            is_run_in_uboot = 1
            uartlog_contrl_handle.send_command("reset")

        if boot_state == E_STATE_UBOOT and prekernel_prompt_str in cur_line:
            boot_state = E_STATE_PREKERNEL
            #logger.info("Starting kernel now\n")

        if kernel_prompt_str in cur_line:
            if is_run_in_uboot == 0:
                boot_state = E_STATE_KERNEL
                logger.info("initial state: run in kernel\n")
                break
            else:
                if boot_state == E_STATE_PREKERNEL:
                    boot_state = E_STATE_KERNEL
                    logger.info("run in kernel now\n")
                    break

        time.sleep(0.0001)

def check_boot_statge():
    global check_boot_handler
    global check_boot_thread_run
    global boot_state

    boot_state = E_STATE_BOOTING
    check_boot_thread_run = True
    check_boot_handler = threading.Thread(target=handle_check_boot)
    check_boot_handler.start()

    # enter blank to get cmdline prompt
    uartlog_contrl_handle.send_command(" ")

    tryCnt = 400
    while tryCnt > 0:
        if boot_state == E_STATE_KERNEL:
            break;
        time.sleep(0.1)
        tryCnt = tryCnt - 1

    logger.info("tryCnt: %s, boot_state: %s\n" %(tryCnt, boot_state))
    if boot_state != E_STATE_KERNEL:
        logger.info("reboot timeout!\n")

    check_boot_thread_run = False
    check_boot_handler.join()
    time.sleep(3)

def system_runcase(args):
    global result
    global is_set_bootargs_fail
    global is_boot_up_fail
    global is_change_bootargs_fail
    global dev_default_crc

    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0
    is_set_bootargs_fail = 0
    is_boot_up_fail = 0
    is_change_bootargs_fail = 0
    dev_default_crc = 0

    # open case log file
    uartlog_contrl_handle.open_serial_buf()

    # check and ensure run in pure linux
    check_boot_statge()

    logger.info("uboot_prompt is %s, kernel_prompt is %s, suspend_crc_start_addr is %s, suspend_crc_end_addr is %s\n" \
                %(uboot_prompt, kernel_prompt, suspend_crc_start_addr, suspend_crc_end_addr))
    logger.info("check and set suspend_crc env\n")
    dev_default_crc = adjust_suspend_crc("0")

    # do test
    if is_set_bootargs_fail == 0 and is_boot_up_fail == 0 and is_change_bootargs_fail == 0:
        str_crc_test()
    else:
        result = 255

    logger.info("check and recovery suspend_crc env\n")
    adjust_suspend_crc("1")

    # close case log file
    uartlog_contrl_handle.close_serial_buf()

    if is_set_bootargs_fail != 0 or is_boot_up_fail != 0 or is_change_bootargs_fail != 0 or result == 255:
        logger.warning("case %s run timeout\n" %Case_Name)
        result = 255

    return result

def system_help(args):
    print("stat str crc test")
    print("cmd : echo 3 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
    print("cmd : echo mem > /sys/power/state")
    print("if the result return 'CRC check success', test pass; if the result return 'CRC check fail', test fail.")

