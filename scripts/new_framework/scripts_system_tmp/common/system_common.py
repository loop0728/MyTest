#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/29 21:48:14
# @file        : system_common.py
# @description :

import os
import time
from PythonScripts.logger import logger

def goto_uboot(client_handle):
    client_handle.write_serial("reboot")
    keyword = 'Loading Environment'
    result = client_handle.match_keyword_return(keyword)
    if result == True:
        client_handle.write_serial("")
        client_handle.write_serial("")
        client_handle.write_serial("")
        client_handle.write_serial("")
        client_handle.write_serial("")

    keyword = 'SigmaStar #'
    result = client_handle.match_keyword_return(keyword)
    if result == True:
        logger.print_info("in uboot.\n")
        return True
    else:
        logger.print_warning("go to uboot fail.\n")
        return False

def goto_kernel(client_handle, reset_wait_time = 20, retry = 3):
    """ 进入 kernel cmdline """
    result = False
    while retry > 0:
        keyword = '/ #'
        client_handle.write_serial("cd /")
        wait_time = 2
        result, data = client_handle.match_keyword_return(keyword, wait_time)
        if result == True:
            logger.print_info("in kernel.")
            return True
        keyword = 'SigmaStar #'
        client_handle.write_serial("")
        result, data = client_handle.match_keyword_return(keyword, wait_time)
        if result == True:
            client_handle.write_serial("reset")
            time.sleep(reset_wait_time)
        retry -= 1
    logger.print_error("go to kernel timeout!\n")
    return False

def ensure_file_exists(file_path):
    """
    保证传入的文件存在，不存在则创建

    Args:
        file_path: 文件路径

    Returns:
        NA
    """
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'a'):
            os.utime(file_path, None)                   # 更新文件时间戳
        logger.print_info(f"Create file: {file_path}")
    else:
        logger.print_info(f"File existed: {file_path}")