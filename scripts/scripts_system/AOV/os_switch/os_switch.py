import sys
import time
import re
from logger import logger

from uartlog_contrl import uartlog_contrl
from uart_record import uartlog_contrl_handle
from variables import ttff_target, ttcl_target, dev_uart, relay_port
from rs232_contrl import rs232_contrl
sys.path.append("..")
from AOV.common.aov_common import AOVCase

def system_reboot(args):
    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0

    # 创建和启动 rs232_contrl_handle
    rs232_contrl_handle = rs232_contrl(relay=int(relay_port), com=dev_uart)

    logger.warning("init rs232_contrl_handle, [%s:%s]!\n" \
                                             %(dev_uart,relay_port))
    rs232_contrl_handle.power_off()
    time.sleep(2)
    rs232_contrl_handle.power_on()

    rs232_contrl_handle.close()
    logger.warning("closed rs232_contrl_handle.")

    return result

def system_runcase(args):
    Case_Name = args[0]
    print("caseName:",Case_Name)
    result = 0
    cur_line = ""
    cnt = 0
    retrycnt = 0
    target_os = ""

    os_switch = AOVCase(Case_Name)
    # 进入kernel
    result = os_switch.goto_kernel()
    if result != 0:
        return result
    while True:
        uartlog_contrl_handle.send_command("if [ $(lsmod | grep mi_sys | wc -l) == 0 ]; then  echo dualos; else echo purelinux; fi;")

        while True:
            cur_line = uartlog_contrl_handle.get_searia_buf()
            # 如果是字节串，则解码成字符串
            if isinstance(cur_line, bytes):
                cur_line = cur_line.decode('utf-8').strip()
            logger.warning("current system is [%s]!\n" %(cur_line))
            if cur_line == "dualos" or cur_line == "purelinux":
                break;
            else:
                time.sleep(1)
                retrycnt = retrycnt + 1

            if retrycnt > 10:
                logger.warning("current retrycnt is [%d] we test failed!\n" %(retrycnt))
                result = 255
                break;

        if result == 255:
            logger.warning("we will reboot now!\n")
            system_reboot("666")
            time.sleep(15)
            break;


        logger.warning("cnt:[%d] current system is [%s]!\n" %(cnt, cur_line))
        cnt = cnt + 1

        if cnt > 1:
            if target_os == cur_line:
                logger.warning("cnt:[%d] we had switch to %s successful!\n" %(cnt-1, target_os))
            else:
                logger.error("cnt:[%d] we switch to %s failed! now system: %s\n" %(cnt-1, target_os, cur_line))
                result = 255
                break;

        if cnt >= 3:
            logger.warning("OS switch test pass!\n")
            break;


        if cur_line == "purelinux":
            target_os = "dualos"
            logger.warning("we will switch to %s!\n" %(target_os))
            time.sleep(1)
            uartlog_contrl_handle.send_command("cd /customer/sample_code/bin/")
            uartlog_contrl_handle.send_command("./prog_aov_aov_demo -t")
            time.sleep(15)
            logger.warning("we send switch command in %s system!\n" %(cur_line))
            uartlog_contrl_handle.send_command("c")
        else:
            target_os = "purelinux"
            logger.warning("we will switch to %s!\n" %(target_os))
            uartlog_contrl_handle.send_command("cd /customer/sample_code/bin/")
            uartlog_contrl_handle.send_command("./prog_preload_linux -t")
            time.sleep(15)
            logger.warning("we send switch command in %s system!\n" %(cur_line))
            uartlog_contrl_handle.send_command("c")
        time.sleep(20)


    if result == 255 and cur_line != "purelinux":
        uartlog_contrl_handle.send_command("/customer/riu_w 34 00 400")
        uartlog_contrl_handle.send_command("/customer/riu_w 34 04 3")
        uartlog_contrl_handle.send_command("/customer/riu_w 34 05 0")
        uartlog_contrl_handle.send_command("/customer/riu_w 34 30 1")
        uartlog_contrl_handle.send_command("/customer/riu_w 34 32 1")
        uartlog_contrl_handle.send_command("/customer/riu_w 34 00 0")
        time.sleep(0.1)
        uartlog_contrl_handle.send_command("reboot")

    return result

def system_help(args):
    print("only for OS switch test")

