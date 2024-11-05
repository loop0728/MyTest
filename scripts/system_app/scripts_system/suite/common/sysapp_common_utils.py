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
            - data (str): Read data
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
    if read_all_data:
        return False, all_data
    else:
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
        tuple:
            - result (bool): execute success, return True; else, return False
            - data (str): cmd log
    """
    result = False
    data = ""
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
        data = ret.stdout
    else:
        logger.error(f"run {cmd} fail, errorcode: {ret.returncode}")
        result = False
    return result, data

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

def check_device_file_exist(device: object, file_path):
    """
    Check if the file on the device exists.
    Args:
        device (objecet): device handle
        file_path: file path
    Returns:
        result (bool): If the file exists, return True; Else, return False.
    """
    result = False
    result = device.check_kernel_phase()
    if result:
        cmd = f"ls {file_path} > /dev/null;echo $?"
        result = device.write(cmd)
        if result:
            result, data = device.read()
            if result and "0" in data:
                result = True
            else:
                result = False
    else:
        logger.error("the device is not in kernel phase now")
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

def _get_ko_symbol_name_from_path(device: object, ko_path):
    """
    Get the symbol name of ko from path.
    Args:
        device (): device handle
        ko_path (str): the file path of ko
    Returns:
        tuple:
            - result (bool): if ko removes success, return True; Else, return False.
            - symbol_name (str): the symbol name of ko.
    """
    result = False
    symbol_name = ""
    # workaround for the dev_base does not clear the send cmd probability when executing write cmd
    parse_result = False
    result = device.check_kernel_phase()
    if result:
        cmd = f'strings {ko_path} | grep "name="'
        result = device.write(cmd)
        if result:
            while not parse_result:
                result, line = device.read()
                if result:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8', errors='replace')
                    line = line.strip()
                    if cmd in line:
                        continue
                    parse_result = True
                    if "name=" in line:
                        symbol_name = line.split('=')[1]
                    else:
                        result = False
    else:
        logger.error("the device is not in kernel phase now")
    # print(f"{result}: symbol_name[{symbol_name}], line:{line}")
    return result, symbol_name

def check_ko_insmod_status(device: object, ko_path):
    """
    Check if ko has been insmoded.
    Args:
        device (object): device handle
        ko_path (str): the file path of ko
    Returns:
        result (bool): if ko has been insmoded, return True; Else, return False.
    """
    result = False
    result = device.check_kernel_phase()
    if result:
        result, ko_name = _get_ko_symbol_name_from_path(device, ko_path)
        if result:
            cmd = f"lsmod | grep {ko_name} | wc -l"
            result = device.write(cmd)
            if result:
                result, data = device.read()
                if result and "0" in data:
                    result = False
    else:
        logger.error("the device is not in kernel phase now")
    return result

def insmod_ko(device: object, ko_path, ko_param):
    """
    Insmod ko.
    Args:
        device (objecet): device handle
        ko_path (str): the file path of ko
        ko_param (str): the insmod param of ko
    Returns:
        result (bool): if ko has been insmoded or insmods success, return True;
        Else, return False.
    """
    result = False
    result = device.check_kernel_phase()
    if result:
        result = check_ko_insmod_status(device, ko_path)
        if not result:
            cmd_insmod_ko = f"insmod {ko_path} {ko_param}"
            result = device.write(cmd_insmod_ko)
            if result:
                result = check_ko_insmod_status(device, ko_path)
            else:
                logger.error(f"write cmd:{cmd_insmod_ko} fail")
    else:
        logger.error("the device is not in kernel phase now")

    if result:
        logger.warning(f"insmod {ko_path} success")
    else:
        logger.error(f"insmod {ko_path} fail")
    return result

def rmmod_ko(device: object, ko_path):
    """
    Remove ko.
    Args:
        device (): device handle
        ko_path (str): the file path of ko
    Returns:
        result (bool): if ko removes success, return True; Else, return False
    """
    result = False
    result = device.check_kernel_phase()
    if result:
        result, ko_name = _get_ko_symbol_name_from_path(device, ko_path)
        if result:
            if check_ko_insmod_status(device, ko_path):
                cmd_rmmod_ko = f"rmmod {ko_name}"
                result = device.write(cmd_rmmod_ko)
                if result:
                    result = check_ko_insmod_status(device, ko_path)
                    result = not result
                else:
                    logger.error(f"write cmd:{cmd_rmmod_ko} fail")
            else:
                result = True
    else:
        logger.error("the device is not in kernel phase now")

    if result:
        logger.warning(f"rmmod {ko_name} success")
    else:
        logger.error(f"rmmod {ko_name} fail")

    return result
