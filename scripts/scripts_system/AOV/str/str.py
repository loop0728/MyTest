import sys
import time
import re
import threading
from logger import logger

from uartlog_contrl import uartlog_contrl
from uart_record import uartlog_contrl_handle
from variables import str_l2l_target, str_h2l_target, str_kmsg, suspend_entry, suspend_exit, app_resume, booting_time, uboot_prompt, kernel_prompt

sys.path.append("..")
from AOV.common.aov_common import AOVCase

parse_handler           = None
parse_thread_run        = False
booting_time_handler    = None
booting_time_thread_run = False

h2l_suspend_enter_time  = 0
h2l_suspend_exit_time   = 0
h2l_app_resume_time     = 0
l2l_suspend_enter_time  = 0
l2l_suspend_exit_time   = 0
l2l_app_resume_time     = 0

ipl_resume_time         = 0
kernel_resume_time      = 0

HIGH_FPS_TO_LOW_FPS     = 0
LOW_FPS_TO_LOW_FPS      = 1


app_run_cmd                 = "/customer/sample_code/bin/prog_aov_aov_demo -t"

"""
brief:
- thread function, get the timestamp on the beginning of suspend, the end of kernel resume and the end of app resume
    suspend_entry, suspend_exit and app_resume should appear in order
"""
def handle_parse():
    global parse_thread_run
    global h2l_suspend_enter_time
    global h2l_suspend_exit_time
    global h2l_app_resume_time
    global l2l_suspend_enter_time
    global l2l_suspend_exit_time
    global l2l_app_resume_time

    cur_line = ""
    h2l_suspend_enter_time = 0
    h2l_suspend_exit_time  = 0
    h2l_app_resume_time    = 0
    l2l_suspend_enter_time = 0
    l2l_suspend_exit_time  = 0
    l2l_app_resume_time    = 0
    test_stage = HIGH_FPS_TO_LOW_FPS

    suspend_entry_str = suspend_entry.strip('"')
    suspend_exit_str = suspend_exit.strip('"')
    app_resume_str = app_resume.strip('"')

    while parse_thread_run is True:
        cur_line = uartlog_contrl_handle.get_serial_buf()
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if test_stage == HIGH_FPS_TO_LOW_FPS:
            # check h2l suspend_entry
            if h2l_suspend_enter_time == 0 and suspend_entry_str in cur_line:
                pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                match = pattern.search(cur_line)
                if match:
                    h2l_suspend_enter_time = match.group(1)
                    logger.info("h2l_suspend_enter_time is %s\n" %(h2l_suspend_enter_time))
                    continue

            # check h2l suspend_exit
            if h2l_suspend_exit_time == 0 and suspend_exit_str in cur_line:
                pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                match = pattern.search(cur_line)
                if match:
                    h2l_suspend_exit_time = match.group(1)
                    logger.info("h2l_suspend_exit_time is %s\n" %(h2l_suspend_exit_time))
                    continue

            if h2l_suspend_enter_time != 0 and h2l_suspend_exit_time != 0:
                h2l_app_resume_time = 0

            # check h2l app resume
            if h2l_app_resume_time == 0 and app_resume_str in cur_line:
                pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                match = pattern.search(cur_line)
                if match:
                    h2l_app_resume_time = match.group(1)
                    #logger.info("h2l_app_resume_time is %s\n" %(h2l_app_resume_time))

            # wait h2l flow complete
            if h2l_suspend_enter_time != 0 and h2l_suspend_exit_time != 0 and h2l_app_resume_time != 0:
                logger.info("h2l_app_resume_time is %s\n" %(h2l_app_resume_time))
                test_stage = LOW_FPS_TO_LOW_FPS

        else:
            # check l2l_suspend_entry
            if l2l_suspend_enter_time == 0 and suspend_entry_str in cur_line:
                pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                match = pattern.search(cur_line)
                if match:
                    l2l_suspend_enter_time = match.group(1)
                    logger.info("l2l_suspend_enter_time is %s\n" %(l2l_suspend_enter_time))
                    continue

            # check l2l_suspend_exit
            if l2l_suspend_exit_time == 0 and suspend_exit_str in cur_line:
                pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                match = pattern.search(cur_line)
                if match:
                    l2l_suspend_exit_time = match.group(1)
                    logger.info("l2l_suspend_exit_time is %s\n" %(l2l_suspend_exit_time))
                    continue

            if l2l_suspend_enter_time != 0 and l2l_suspend_exit_time != 0:
                l2l_app_resume_time = 0

            # check l2l app resume
            if l2l_app_resume_time == 0 and app_resume_str in cur_line:
                pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
                match = pattern.search(cur_line)
                if match:
                    l2l_app_resume_time = match.group(1)
                    #logger.info("l2l_app_resume_time is %s\n" %(l2l_app_resume_time))

            # wait l2l flow complete
            if l2l_suspend_enter_time != 0 and l2l_suspend_exit_time != 0 and l2l_app_resume_time != 0:
                logger.info("l2l_app_resume_time is %s\n" %(l2l_app_resume_time))
                break

        time.sleep(0.0001)


def h2l_handle_parse():
    global h2l_parse_thread_run
    global h2l_suspend_enter_time
    global h2l_suspend_exit_time
    global h2l_app_resume_time
    cur_line = ""
    h2l_suspend_enter_time = 0
    h2l_suspend_exit_time  = 0
    h2l_app_resume_time    = 0

    suspend_entry_str = suspend_entry.strip('"')
    suspend_exit_str = suspend_exit.strip('"')
    app_resume_str = app_resume.strip('"')

    while h2l_parse_thread_run is True:
        cur_line = uartlog_contrl_handle.get_serial_buf()
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if h2l_suspend_enter_time == 0 and suspend_entry_str in cur_line:
            pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
            match = pattern.search(cur_line)
            if match:
                h2l_suspend_enter_time = match.group(1)
                logger.info("h2l_suspend_enter_time is %s\n" %(h2l_suspend_enter_time))
                continue

        if h2l_suspend_exit_time == 0 and suspend_exit_str in cur_line:
            pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
            match = pattern.search(cur_line)
            if match:
                h2l_suspend_exit_time = match.group(1)
                logger.info("h2l_suspend_exit_time is %s\n" %(h2l_suspend_exit_time))
                continue

        if h2l_suspend_enter_time != 0 and h2l_suspend_exit_time != 0:
            h2l_app_resume_time = 0

        if h2l_app_resume_time == 0 and app_resume_str in cur_line:
            pattern = re.compile(r'\[\s*([\d]+\.[\d]+)\]\s')
            match = pattern.search(cur_line)
            if match:
                h2l_app_resume_time = match.group(1)
                #logger.info("h2l_app_resume_time is %s\n" %(h2l_app_resume_time))

        if h2l_suspend_enter_time == 0 or h2l_suspend_exit_time == 0:
            h2l_app_resume_time = 0

        if h2l_suspend_enter_time !=0 and h2l_suspend_exit_time != 0 and h2l_app_resume_time != 0:
            logger.info("h2l_app_resume_time is %s\n" %(h2l_app_resume_time))
            break

        time.sleep(0.0001)

def handle_booting_time():
    global booting_time_thread_run
    global ipl_resume_time
    global kernel_resume_time

    cur_line = ""
    ipl_resume_time = 0
    kernel_resume_time  = 0
    is_kernel_part = 0

    booting_time_str = booting_time.strip('"')

    while booting_time_thread_run is True:
        cur_line = uartlog_contrl_handle.get_serial_buf()
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if ipl_resume_time == 0 and booting_time_str in cur_line:
            pattern = re.compile(r'(\d+)\(us\)')
            match = pattern.search(cur_line)
            if match:
                ipl_resume_time = match.group(1)
                logger.info("ipl_resume_time is %s\n" %(ipl_resume_time))
                continue

        if is_kernel_part == 0 and "LINUX" in cur_line:
            is_kernel_part = 1

        if kernel_resume_time == 0 and is_kernel_part == 1 and booting_time_str in cur_line:
            pattern = re.compile(r'(\d+)\(us\)')
            match = pattern.search(cur_line)
            if match:
                kernel_resume_time = match.group(1)
                logger.info("kernel_resume_time is %s\n" %(kernel_resume_time))
                continue

        if ipl_resume_time !=0 and kernel_resume_time != 0:
            break

        time.sleep(0.0001)


"""
brief:
- redirect kmsg to memory
"""
def redirect_kmsg():
    command_redirect="cat /proc/kmsg > {} &".format(str_kmsg)
    uartlog_contrl_handle.send_command(command_redirect)
    logger.info("redirect kmsg to %s\n" %(str_kmsg))
    time.sleep(5)
    uartlog_contrl_handle.send_command("pkill -f 'cat /proc/kmsg'")
    #uartlog_contrl_handle.send_command("pgrep -l 'cat /proc/kmsg' | awk '{print $1}' | xargs kill -9")

def quit_app():
    logger.info("enter 'q' to exit app\n")
    retryCnt = 0
    while retryCnt < 10:
        # ctrl+c, ascii: 3
        #uartlog_contrl_handle.send_command("\003")
        uartlog_contrl_handle.send_command("q")
        uartlog_contrl_handle.send_command("\n")
        retryCnt = retryCnt + 1
        time.sleep(0.1)

def ctrl_z_and_kill():
    logger.info("kill to exit app\n")
    app_kill_cmd = "pkill -9 -f '" + app_run_cmd + "'"
    # ctrl+z, ascii: 26
    uartlog_contrl_handle.send_command("\034")
    time.sleep(1)
    uartlog_contrl_handle.send_command(app_kill_cmd)
    time.sleep(1)
    uartlog_contrl_handle.send_command("")

def run_aov_demo_test():
    # run demo
    logger.info("start app\n")
    uartlog_contrl_handle.send_command(app_run_cmd)
    time.sleep(10)
    logger.info("send str cmd to app\n")
    uartlog_contrl_handle.send_command("a")
    time.sleep(10)

    # enter 'q' to quit app
    quit_app()
    time.sleep(2)

def echo_mem_test():
    uartlog_contrl_handle.send_command("echo 5 > /sys/devices/virtual/sstar/rtcpwc/alarm_timer")
    uartlog_contrl_handle.send_command("echo mem > /sys/power/state")
    logger.info("send str cmd\n")
    time.sleep(7)

def enable_printk_time():
    uartlog_contrl_handle.send_command("echo y > /sys/module/printk/parameters/time")

def disable_printk_time():
    uartlog_contrl_handle.send_command("echo n > /sys/module/printk/parameters/time")

def parse_kmsg():
    global parse_handler
    global parse_thread_run

    parse_thread_run = True
    parse_handler = threading.Thread(target=handle_parse)
    parse_handler.start()

    #cat memory file to serial
    command_cat_tmpfile="cat {}".format(str_kmsg)
    uartlog_contrl_handle.send_command(command_cat_tmpfile)
    logger.info("read log file and parse\n")
    time.sleep(5)

    #check the result and del memory file
    parse_thread_run = False
    parse_handler.join()

    command_del_tmpfile="rm {}".format(str_kmsg)
    uartlog_contrl_handle.send_command(command_del_tmpfile)


def cat_booting_time():
    global booting_time_handler
    global booting_time_thread_run

    booting_time_thread_run = True
    booting_time_handler = threading.Thread(target=handle_booting_time)
    booting_time_handler.start()

    #cat memory file to serial
    uartlog_contrl_handle.send_command("cat /sys/class/sstar/msys/booting_time")
    logger.info("cat booting time\n")
    time.sleep(2)

    booting_time_thread_run = False
    booting_time_handler.join()


def judge_test_result(param):
    result = 0

    if param == LOW_FPS_TO_LOW_FPS:
        if l2l_suspend_enter_time == 0 or l2l_suspend_exit_time == 0 or l2l_app_resume_time == 0:
            logger.warning("str_l2l test run timeout\n")
            result = 255
            return result

        if l2l_suspend_enter_time > l2l_suspend_exit_time or l2l_suspend_exit_time > l2l_app_resume_time:
            logger.error("the stat time of str_l2l is invalid\n")
            result = 255
            return result

        kernel_str_time = float(l2l_suspend_exit_time) - float(l2l_suspend_enter_time)
        total_str_time = float(l2l_app_resume_time) - float(l2l_suspend_enter_time)
        kernel_str_us = float(kernel_str_time) * 1000000
        total_str_us = float(total_str_time) * 1000000

        logger.warning("str_l2l Time cost:%d us; target:%s us\n" %(int(total_str_us), str_l2l_target))
        logger.warning("str_l2l (only kernel) Time cost:%d us\n" %(int(kernel_str_us)))
        logger.warning("str_l2l booting_time (IPL) Time cost:%d us\n" %(int(ipl_resume_time)))
        logger.warning("str_l2l booting_time (kernel) Time cost:%d us\n" %(int(kernel_resume_time)))

        if total_str_us > float(str_l2l_target):
            logger.info("str_l2l test fail\n")
            result = 255
        else:
            logger.info("str_l2l test pass\n")
        return result
    else:
        if h2l_suspend_enter_time == 0 or h2l_suspend_exit_time == 0 or h2l_app_resume_time == 0:
            logger.warning("str_h2l test run timeout\n")
            result = 255
            return result

        if h2l_suspend_enter_time > h2l_suspend_exit_time or h2l_suspend_exit_time > h2l_app_resume_time:
            logger.error("the stat time of str_h2l is invalid\n")
            result = 255
            return result

        kernel_str_time = float(h2l_suspend_exit_time) - float(h2l_suspend_enter_time)
        total_str_time = float(h2l_app_resume_time) - float(h2l_suspend_enter_time)
        kernel_str_us = float(kernel_str_time) * 1000000
        total_str_us = float(total_str_time) * 1000000

        logger.warning("str_h2l Time cost:%d us; target:%s us\n" %(int(total_str_us), str_h2l_target))
        logger.warning("str_h2l (only kernel) Time cost:%d us\n" %(int(kernel_str_us)))
        logger.warning("str_h2l booting_time (IPL) Time cost:%d us\n" %(int(ipl_resume_time)))
        logger.warning("str_h2l booting_time (kernel) Time cost:%d us\n" %(int(kernel_resume_time)))

        if total_str_us > float(str_h2l_target):
            logger.info("str_h2l test fail\n")
            result = 255
        else:
            logger.info("str_h2l test pass\n")
        return result


check_boot_handler = None
check_boot_thread_run = False
# boot state, 0: booting; 1: uboot; 2: kernel
E_STATE_BOOTING   = 0
E_STATE_UBOOT     = 1
E_STATE_PREKERNEL = 2
E_STATE_KERNEL    = 3
boot_state        = E_STATE_BOOTING

def handle_check_boot():
    global check_boot_thread_run
    global boot_state

    boot_state = E_STATE_BOOTING
    cur_line = ""

    uboot_prompt_str = "SigmaStar #"
    prekernel_prompt_str = "Starting kernel"
    kernel_prompt_str = "/ #"
    reboot_cmd_send = 0

    while check_boot_thread_run == True:
        cur_line = uartlog_contrl_handle.get_serial_buf()
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if uboot_prompt_str in cur_line:
            if reboot_cmd_send == 0:
                logger.info("run in uboot cmdline now, do reset\n")
                uartlog_contrl_handle.send_command("reset")
                boot_state = E_STATE_UBOOT
                reboot_cmd_send = 1
            else:
                boot_state = E_STATE_UBOOT
                logger.info("reboot to uboot cmdline now\n")
            continue

        if prekernel_prompt_str in cur_line:
            if reboot_cmd_send == 1:
                boot_state = E_STATE_PREKERNEL
                #logger.info("Starting kernel now\n")

        if kernel_prompt_str in cur_line:
            if reboot_cmd_send == 0:
                logger.info("run in kernel now, do reboot\n")
                uartlog_contrl_handle.send_command("reboot")
                boot_state = E_STATE_UBOOT
                reboot_cmd_send = 1
                continue
            else:
                if boot_state == E_STATE_PREKERNEL:
                    boot_state = E_STATE_KERNEL
                    logger.info("reboot to kernel now\n")
                    break
        time.sleep(0.001)

def check_boot_stage():
    global check_boot_handler
    global check_boot_thread_run
    global boot_state

    boot_state = E_STATE_BOOTING
    check_boot_thread_run = True
    check_boot_handler = threading.Thread(target=handle_check_boot)
    check_boot_handler.start()

    uartlog_contrl_handle.send_command(" ")

    tryCnt = 400
    while tryCnt > 0:
        if boot_state == E_STATE_KERNEL:
            break
        time.sleep(0.1)
        tryCnt = tryCnt - 1

    if boot_state != E_STATE_KERNEL:
        logger.info("reboot timeout!\n")

    check_boot_thread_run = False
    check_boot_handler.join()

def reboot_dev():
    logger.info("reboot dev and check test env\n")
    check_boot_stage()

def simple_reboot():
    global boot_state
    boot_state = E_STATE_KERNEL
    time.sleep(5)
    uartlog_contrl_handle.send_command("reboot")
    time.sleep(30)

# param, 0: lowfps->lowfps; 1: highfps->lowfps
def fps_switch_squence():
    result = 0
    result_h2l = 0
    result_l2l = 0

    # reboot first to clear board status, for temporary testing
    reboot_dev()

    if boot_state == E_STATE_KERNEL:
        # open kernel timestamp
        enable_printk_time()

        # redirect kmsg to memory file
        redirect_kmsg()

        # communicate with app
        run_aov_demo_test()
        # test without app
        #echo_mem_test()

        # redirect kmsg to memory file and cover the old kmsg
        redirect_kmsg()

        # create thread to recv and parse kmsg log from serial
        parse_kmsg()

        # cat booting time
        cat_booting_time()

        # judge test result
        result_h2l = judge_test_result(HIGH_FPS_TO_LOW_FPS)
        result_l2l = judge_test_result(LOW_FPS_TO_LOW_FPS)

        if result_l2l != 0 or result_h2l != 0:
            result = 255

        # close kernel timestamp
        disable_printk_time()
    else:
        logger.info("reboot timeout!\n")
        result = 255

    return result


def system_runcase(args):
    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0

    # open case log file
    uartlog_contrl_handle.open_serial_buf()

    # test str time cost
    logger.info("========= STR: high_fps -> low_fps -> low_fps =========\n")
    result = fps_switch_squence()

    # close case log file
    uartlog_contrl_handle.close_serial_buf()

    # force to pass
    result = 0

    logger.info("\n");
    if result == 0:
        l2l_kernel_str_time = float(l2l_suspend_exit_time) - float(l2l_suspend_enter_time)
        l2l_total_str_time = float(l2l_app_resume_time) - float(l2l_suspend_enter_time)
        l2l_kernel_str_us = float(l2l_kernel_str_time) * 1000000
        l2l_total_str_us = float(l2l_total_str_time) * 1000000

        h2l_kernel_str_time = float(h2l_suspend_exit_time) - float(h2l_suspend_enter_time)
        h2l_total_str_time = float(h2l_app_resume_time) - float(h2l_suspend_enter_time)
        h2l_kernel_str_us = float(h2l_kernel_str_time) * 1000000
        h2l_total_str_us = float(h2l_total_str_time) * 1000000

        time_info = "target_l2l:{};total_l2l:{};sys_l2l:{};ipl_l2l:{};kernel_l2l:{};target_h2l:{};total_h2l:{};sys_h2l:{};ipl_h2l:{};kernel_h2l:{}\n".format(\
                    int(str_l2l_target), int(l2l_total_str_us), int(l2l_kernel_str_us), int(ipl_resume_time), int(kernel_resume_time), \
                    int(str_h2l_target), int(h2l_total_str_us), int(h2l_kernel_str_us), int(ipl_resume_time), int(kernel_resume_time))

        # boottime of h2l and l2l are the same, keep two set of values for not modifying the report line-chart. The following will be updated later.
        # time_info = "target_l2l:{};total_l2l:{};sys_l2l:{};target_h2l:{};total_h2l:{};sys_h2l:{};ipl:{};kernel:{}\n".format(\
        #             int(str_l2l_target), int(l2l_total_str_us), int(l2l_kernel_str_us), int(str_h2l_target), int(h2l_total_str_us), \
        #             int(h2l_kernel_str_us), int(ipl_resume_time), int(kernel_resume_time))
        str = AOVCase(Case_Name)
        str.save_time_info(Case_Name, time_info)

        logger.info("str test pass!\n");
    else:
        result = 255
        logger.info("str test fail!\n");

    return result

def system_help(args):
    print("stat str cost time")
    print("cmd: str")
    print("AOV STR cost time: the time interva bwtween two 'suspend entry', include app's time consumption")
    print("SYS STR cost time: the time interva bwtween 'suspend entry' and 'suspend exit', kernel space's time consumption")
