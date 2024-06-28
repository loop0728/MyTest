import sys
import time
import re
from logger import logger

from rs232_contrl import rs232_contrl
from variables import dev_uart, relay_port

def system_runcase(args):
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

def system_help(args):
    print("only for reboot test")

