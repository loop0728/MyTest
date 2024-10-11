#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""utils interfaces"""

import os
import time
import json
from suite.common.sysapp_common_logger import logger, sysapp_print


def nothing():
    """Nothing"""
    pass

def match_keyword(device_handle, keyword, lines=100):
    """
    Match keyword.

    Args:
        device_handle (object): device
        keyword (str): keyword
        lines (int): max lines

    Returns:
        bool, data: result and data
    """
    curr_line = 0
    while curr_line < lines:
        result, data = device_handle.read()
        if result is True:
            if keyword in data:
                return True, data
            else:
                curr_line += 1
        else:
            logger.warning("Read timeout: 5S")
            break
    return False, ""

def write_and_match_keyword(device_handle, ss_input, keyword, lines=100):
    """
    Write cmd and match keyword.

    Args:
        device_handle (object): device
        ss_input (str): write cmd
        keyword (str): keyword
        lines (int): lines

    Returns:
        bool, data: result and data
    """
    result = device_handle.write(ss_input)
    if result is True:
        result, data = match_keyword(device_handle, keyword, lines)
        return result, data
    else:
        logger.warning(f"Write {ss_input} fail.")
        return False, ""

def get_write_cmd_ret(device_handle: object, line=1, max_line=4):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    device_handle.write("echo $?")
    try_cnt = 0
    while True:
        try_cnt += 1
        ret, data = device_handle.read(line)
        if bool(ret) and data is not None and data.strip().isdigit():
            print(f"ret: {ret} value:{data}")
            break
        if try_cnt > max_line:
            logger.error(f"ret: {ret} value:{data}")
            logger.error("no found return value!")
            ret = False
            break
    return ret, data

# unused yet
def write_return_ret(device_handle: object, cmd, line=1, max_line=10):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    logger.warning(f"cmd:{cmd}")
    device_handle.write(cmd)
    device_handle.write("echo $?")
    try_cnt = 0
    while True:
        try_cnt += 1
        ret, data = device_handle.read(line)
        if bool(ret) and data is not None and data.strip().isdigit():
            print(f"ret: {ret} value:{data}")
            break
        if try_cnt > max_line:
            logger.error("no found return value!")
            ret = False
            break
    return ret, data

# unused yet
def wait_keyword_write_cmd(
        device_handle: object, cmd, check_keyword=None, max_readline=4
):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    try_cnt = 0
    while try_cnt < max_readline:
        ret, data = device_handle.read()
        if check_keyword is not None and bool(ret) and check_keyword in data:
            device_handle.write(cmd)
            break
        try_cnt += 1








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



def write_cmd(
        device_handle: object, cmd, is_return_value=False, check_keyword=None, max_line=4
):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    logger.warning(f"cmd:{cmd}")
    ret = device_handle.write(cmd)
    try_cnt = 0
    data = None
    while is_return_value:
        ret, data = device_handle.read()
        if check_keyword is not None and bool(ret) and check_keyword in data:
            print(f"ret: {ret} value:{data}")
            break
        elif (
                check_keyword is None
                and bool(ret)
                and data is not None
                and data.strip().isdigit()
        ):
            print(f"ret: {ret} value:{data}")
            break
        if try_cnt > max_line:
            logger.error("no found return value!")
            ret = False
            break
        try_cnt += 1
    return ret, data


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
    with open(file1, "r", encoding="utf-8") as f1, open(
            file2, "r", encoding="utf-8"
    ) as f2:
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                print(f"{line1} not equal {line2}")
                return 255
        if len(f1.readline()) == 0 and len(f2.readline()) == 0:
            result = 0
        else:
            result = 255
        return result

# internal function, used by get_case_json_key_value
def get_json_content(json_path) -> dict:
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
            with open(json_path, "r", encoding='utf-8') as f:
                json_content = json.load(f)
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
    json_content_dict = get_json_content(json_file_path)
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

# used by aov scenarios
def get_ko_insmod_state(uart: object, koname=''):
    """ get_ko_insmod_state
        uart (object): 仅支持uart
        koname (str): mi_sys
    """
    result = ""
    cmd = f"lsmod | grep {koname} | wc -l"
    # 检查串口信息
    res = uart.write(cmd)
    if res is False:
        logger.error(f"{uart} is disconnected.")
        return "Unknown"
    wait_keyword = "0"
    status, data = uart.read()
    if status  is True:
        if wait_keyword in data:
            result = "none"
        else:
            result = "insmod"
    else:
        result = "Unknown"
    return result

def check_insmod_ko(uart: object, koname=''):
    """ check_insmod_ko
        uart (object): 仅支持uart
        koname (str): mi_sys
    """
    wait_keyword = "none"
    ko_path = f"/config/modules/5.10/{koname}.ko"
    data = get_ko_insmod_state(uart, f"{koname}")
    if wait_keyword in data:
        cmd = f"insmod {ko_path}"
        logger.warning(f"we will {cmd}")
        uart.write(cmd)
        result = "true"
    else:
        logger.warning(f"we no need insmod {koname}")
        result = "false"
    return result

# used by aov scenarios
def get_current_os(uart: object):
    """ get_current_os
        uart (object): 仅支持uart
    """
    wait_keyword = "none"
    data = get_ko_insmod_state(uart, "mi_sys")
    if wait_keyword in data:
        result = "dualos"
    else:
        result = "purelinux"
    return result

# used by aov scenarios
def switch_os_aov(uart: object, target_os=''):
    """ switch_os by aov pipe case
        uart (object): 仅支持uart
        target_os (str): purelinux or dualos
    """
    result = 0
    cur_os = get_current_os(uart)
    if cur_os == target_os:
        logger.warning(f"current os is match {target_os}")
        return 0

    logger.warning(f"will switch to OS({target_os})!")
    if target_os == "dualos":
        cmd = "cd /customer/sample_code/bin/"
        uart.write(cmd)
        wait_keyword = "/customer/sample_code/bin #"
        status, data = uart.read()
        if status is True:
            if wait_keyword not in data:
                return 255
        else:
            logger.error(f"Read fail,no keyword: {wait_keyword}")
            return 255
        cmd = "./prog_aov_aov_demo -t"
        uart.write(cmd)
        time.sleep(10)
        cmd = "c"
        uart.write(cmd)

    if target_os == "purelinux":
        cmd = "cd /customer/sample_code/bin/"
        uart.write(cmd)
        time.sleep(1)
        wait_keyword = "/customer/sample_code/bin #"
        status, data = uart.read()
        if status is True:
            if wait_keyword not in data:
                result = 255
                return result

        cmd = "./prog_preload_linux -t"
        wait_keyword = "press c to change mode"
        result, data = write_and_match_keyword(uart, cmd, wait_keyword)
        if result is False:
            return 255

        cmd = "c"
        uart.write(cmd)

    time.sleep(20)
    return result

# unused yet
def get_cfg_file(module_path, chip, case_name):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    config_name_path = module_path + "/" + chip + "_" + case_name + "_config.json"
    return config_name_path

# unused yet
def modfiy_dev_cfg_file(
        device_handle: object, file_name, key=None, target_value=None, num=-1
):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    result = 255
    if key is None or target_value is None or key == "" or target_value == "":
        logger.error(f"modfiy_dev_json_file:json_name[{file_name}] is vaild!")
        return result
    cat_file_cmd_grep_key = f"cat {file_name} | grep {key} | wc -l"
    logger.warning(cat_file_cmd_grep_key)
    # write_cmd(device_handle, cat_file_cmd_grep_key)
    # ret,data = read_line(device_handle, 2)
    ret, data = write_cmd(device_handle, cat_file_cmd_grep_key, True)
    if bool(ret):
        if "No such file or directory" in data or data == "0":
            return result
    else:
        return result
    if num < 0:
        modfiy_key_value_cmd = f"sed -i 's/{key}/{target_value}/g' {file_name}"
    else:
        modfiy_key_value_cmd = f"sed -i '{key}s/{target_value}/{file_name}/g' {num}"
    logger.warning(modfiy_key_value_cmd)

    write_cmd(device_handle, modfiy_key_value_cmd)
    result, data = get_write_cmd_ret(device_handle)
    if not bool(result):
        if data is not None:
            logger.error(data)
        return 255
    cat_file_cmd_grep_key = f"cat {file_name} | grep {key} | wc -l"

    result, data = write_cmd(device_handle, cat_file_cmd_grep_key, True)
    if not bool(result):
        if data is not None:
            logger.error(data)
    result, data = get_write_cmd_ret(device_handle)
    if not bool(result):
        if data is not None:
            logger.error(data)
        return 255
    if data.strip().isdigit():
        result = int(data)
    else:
        result = 255
        if data is not None:
            logger.error(f"data:{data}")
    return result
