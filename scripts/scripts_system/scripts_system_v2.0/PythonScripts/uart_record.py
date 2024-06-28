import sys
import time
from uartlog_contrl import uartlog_contrl
from rs232_contrl import rs232_contrl
from variables import log_path, uart_port
from logger import logger

# 全局变量
uartlog_contrl_handle = None

def create_and_start_uartlog_contrl():
    global uartlog_contrl_handle

    # 如果 handle 已经存在，则直接返回
    if uartlog_contrl_handle is not None:
        return uartlog_contrl_handle

    # 创建和启动 uartlog_contrl_handle
    uartlog_contrl_handle = uartlog_contrl(uart_port, log_path)
    uartlog_contrl_handle.start_record()

    #logger.warning("init uartlog_contrl_handle, open new uart_record thread[%s:%s:%s]!\n" \
    #                                         %(uart_port,log_path,uartlog_contrl_handle.is_open()))

    return uartlog_contrl_handle

def stop_and_close_uartlog_contrl():
    global uartlog_contrl_handle

    # 如果 handle 存在，则停止和关闭
    if uartlog_contrl_handle is not None:
        uartlog_contrl_handle.stop_record()
        #logger.warning("Stopped and closed uartlog_contrl_handle.")

        # 重置 handle 为 None，以便下次重新创建
        uartlog_contrl_handle = None