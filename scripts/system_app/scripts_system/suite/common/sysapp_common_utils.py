#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""utils interfaces"""

import os
import subprocess
import json
from suite.common.sysapp_common_logger import logger, sysapp_print

def nothing():
    """Nothing"""
    pass

def _match_keyword(device: object, keyword, read_all_data=False, max_read_lines=100, timeout=5):
    """
    Read the returned info until match keyword or exceed the max read times.
    Args:
        device (object): client handle
        keyword (str): keyword
        read_all_data (bool): Defaultly set 'False', return the single line with keyword, if
            set 'True', return all the read lines.
        max_read_lines (int): max read lines
        timeout (int): Timeout for reading a single line, in milliseconds.
    Returns:
        tuple:
            - result (bool): If reads keyword success, return True; Else, return False.
            - data (str): Read line data
    """
    read_cnt = 0
    all_data = ""
    while read_cnt < max_read_lines:
        result, line = device.read(wait_timeout=timeout)
        if result is True:
            all_data += line
            if keyword in line:
                if read_all_data:
                    return result, all_data
                else:
                    return result, line
            read_cnt += 1
        else:
            logger.error("Read timeout!")
            break
    return False, ""

def write_and_match_keyword(device: object, cmd, keyword, read_all_data=False,
                            max_read_lines=100, timeout=5):
    """
    Write cmd and read the returned info until match keyword or exceed the max read times.
    Args:
        device (object): client handle
        cmd (str): write cmd
        keyword (str): check keyword
        read_all_data (bool): Defaultly set 'False', return the single line with keyword, if
            set 'True', return all the read lines.
        max_read_lines (int): max read lines
        timeout (int): Timeout for reading a single line, in milliseconds.
    Returns:
        tuple:
            - result (bool): If reads keyword success, return True; Else, return False.
            - data (str): Read data
    """
    result = device.write(cmd)
    if result is True:
        result, data = _match_keyword(device, keyword, read_all_data, max_read_lines, timeout)
        return result, data
    else:
        logger.error(f"Write {cmd} fail.")
        return False, ""

def change_server_dir(path):
    """
    Change current directory on server.
    Args:
        path (str): destination directory
    Returns:
        result (bool): If execute success, return True; else, return False
    """
    try:
        logger.info(f"Changed directory to {path} ...")
        os.chdir(path)
    except OSError as error:
        logger.error(f"Error changing directory: {error.strerror}")
        return False
    return True

def run_server_cmd(cmd):
    """
    Run cmd on server.
    Args:
        cmd (str): command string
    Returns:
        result (bool): execute success, return True; else, return False
    """
    result = False
    logger.info(f"server run {cmd}")
    try:
        ret = subprocess.run(cmd, universal_newlines=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=True)
        logger.info(f"Command output: {ret.stdout}")
    except subprocess.CalledProcessError as error:
        logger.error(f'Command failed with return code: {error.returncode}')
        logger.error(f'Output: {error.output}')
        logger.error(f'Error: {error.stderr}')

    if ret.returncode == 0:
        logger.info(f"run {cmd} ok")
        result = True
    else:
        logger.error(f"run {cmd} fail, errorcode: {ret.returncode}")
        result = False
    return result

# show timestamp of printk log
@sysapp_print.print_line_info
def enable_printk_time(device_handle):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    cmd_printk_time_on = "echo y > /sys/module/printk/parameters/time"
    device_handle.write(cmd_printk_time_on)

# hide timestamp of printk log
@sysapp_print.print_line_info
def disable_printk_time(device_handle):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    cmd_printk_time_off = "echo n > /sys/module/printk/parameters/time"
    device_handle.write(cmd_printk_time_off)

# used by sysapp_dev_sys & ut cases
def ensure_file_exists(file_path) -> None:
    """
    Ensure file exists.

    Args:
        file_path: file path
    """
    dir_path = os.path.dirname(file_path)

    if not dir_path:
        dir_path = os.getcwd()

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, "a", encoding='utf-8'):
            pass
        logger.info(f"Create file: {file_path}")
    else:
        logger.info(f"File existed: {file_path}")

# used by ut cases
def are_files_equal_line_by_line(file1, file2) -> int:
    """
    Are files equal line by line.

    Args:
        file1 (str): file1 path
        file2 (str): file2 path

    Returns:
        int: result
    """
    with open(file1, "r", encoding="utf-8") as test_file1, open(
            file2, "r", encoding="utf-8"
    ) as test_file2:
        for line1, line2 in zip(test_file1, test_file2):
            if line1 != line2:
                print(f"{line1} not equal {line2}")
                return 255
        if test_file1.readline() == test_file2.readline():
            result = 0
        else:
            result = 255
        return result

def _get_json_content(json_path) -> dict:
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    json_content = None
    json_content_dict = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding='utf-8') as json_file:
                json_content = json.load(json_file)
                json_content_dict = dict(json_content)
        except json.JSONDecodeError:
            return None
    return json_content_dict

# used by sysapp_common_case_base
def get_case_json_key_value(key_str, case_name, json_file_path=""):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    result = "no_find_key"
    if json_file_path == "":
        return result
    json_content_dict = _get_json_content(json_file_path)
    if json_content_dict is not None:
        if case_name in json_content_dict:
            if key_str in json_content_dict[case_name]:
                result = json_content_dict[case_name].get(key_str, "no_find_key")
                # logger.warning("{}:{}".format(key_str,result))
        else:
            logger.warning(
                f"no find {key_str} key, will use default value"
            )
    return result
