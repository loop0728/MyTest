#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/29 21:48:14
# @file        : system_common.py
# @description :

import os
import time
import json
import re
from PythonScripts.logger import logger
from Device.rs232_contrl import rs232_contrl
import PythonScripts.variables as platform
from client import Client


def modfiy_dev_cfg_file(device_handle:object, file_name, key=None, target_value=None, num=-1):
    result = 255
    if key is None or target_value is None or key == '' or target_value == '':
        logger.print_error("modfiy_dev_json_file:json_name[%s] is vaild!" %(file_name))
        return result
    cat_file_cmd_grep_key = "cat {} | grep {} | wc -l".format(file_name, str(key))
    logger.print_warning(cat_file_cmd_grep_key)
    #write_cmd(device_handle, cat_file_cmd_grep_key)
    #ret,data = read_line(device_handle, 2)
    ret,data = write_cmd(device_handle, cat_file_cmd_grep_key,True)
    if bool(ret):
        if 'No such file or directory' in data or data == '0':
            return result
    else:
        return result
    if num < 0:
        modfiy_key_value_cmd = "sed -i 's/{}/{}/g' {}".format(key, target_value, file_name)#替换所有
    else:
        modfiy_key_value_cmd = "sed -i '{}s/{}/{}/g' {}".format(key, target_value,file_name,num)#替换指定第几个
    logger.print_warning(modfiy_key_value_cmd)

    write_cmd(device_handle,modfiy_key_value_cmd)
    result,data = get_write_cmd_ret(device_handle)
    if not bool(result):
        if data is not None:
            logger.print_error(data)
        return 255
    cat_file_cmd_grep_key = "cat {} | grep {} | wc -l".format(file_name, str(key))

    result,data = write_cmd(device_handle,cat_file_cmd_grep_key,True)
    if not bool(result):
        if data is not None:
            logger.print_error(data)
    result,data = get_write_cmd_ret(device_handle)
    if not bool(result):
        if data is not None:
            logger.print_error(data)
        return 255
    if data.strip().isdigit():
        result = int(data)
    else:
        result = 255
        if data is not None:
            logger.print_error("data:%s" %data)
    return result

""" case internal functions start """
# check current status of the dev, if the dev is at uboot of at kernel, then reboot the dev
@logger.print_line_info
def reboot_dev(device_handle:object, reboot_type="soft_reboot"):
    reboot_timeout            = 180
    cmd_uboot_reset           = "reset"
    cmd_kernel_reboot         = "reboot"
    trywait_time = 0
    result = 255
    if reboot_type == "soft_reboot":
        for i in range(1,20):
            borad_cur_state = get_borad_cur_state(device_handle)
            if borad_cur_state != 'Unknow':
                break
        if borad_cur_state == 'Unknow':
            logger.print_error("get cur state is unknow")
            return result

        if borad_cur_state == 'at uboot':
            borad_cur_state = 'Unknow'
            write_cmd(device_handle, cmd_uboot_reset)
            time.sleep(6) #wait uboot run finnish. for prevent goto uboot cmdline
        elif borad_cur_state == 'at kernel':
            borad_cur_state = 'Unknow'
            write_cmd(device_handle, cmd_kernel_reboot)
            ret,data = device_handle.read()
            if bool(ret) and data is not None:
                ret,data = device_handle.read()
                if bool(ret) and data is not None:
                    logger.print_warning(data)
                    if  "sh: can't execute" in data:
                        return result
                time.sleep(6) #wait uboot run finnish. for prevent goto uboot cmdline
            else:
                return result

    elif reboot_type != "soft_reboot":
        cold_reboot()
        time.sleep(6) #wait uboot run finnish. for prevent goto uboot cmdline
    logger.print_error("reboot_dev")
    while True:
        borad_cur_state = get_borad_cur_state(device_handle)
        if borad_cur_state == 'at kernel':
            result = 0
            logger.print_info("borad_cur_state:%s \n" % borad_cur_state)
            break
        elif borad_cur_state == 'at uboot':
            write_cmd(device_handle, cmd_uboot_reset)
            borad_cur_state = 'Unknow'
            time.sleep(6) #wait uboot run finnish. for prevent goto uboot cmdline
        else:
            time.sleep(1)
            trywait_time = trywait_time + 1
            if trywait_time > reboot_timeout:
                break
    return result

def reboot_board(device_handle:object, reboot_type='soft_reboot'):
    logger.print_error("reboot_board")
    result = 255
    if reboot_type == 'soft_reboot':
        result = reboot_dev(device_handle, reboot_type)
    elif reboot_type == 'cold_reboot':
        result = cold_reboot()
    return result


def get_write_cmd_ret(device_handle:object, line=1, max_line=4):
    device_handle.write("echo $?")
    try_cnt = 0
    while True:
        try_cnt += 1
        ret,data = device_handle.read(line)
        if bool(ret) and data is not None and data.strip().isdigit():
            print("ret: %s value:%s" %(ret,data))
            break
        if try_cnt > max_line:
            logger.print_error("ret: %s value:%s" %(ret,data))
            logger.print_error("no found return value!")
            ret = False
            break
    return ret,data


def write_cmd(device_handle:object, cmd, is_return_value=False, check_keyWord=None, max_line=4):
    logger.print_warning("cmd:%s" %cmd)
    ret = device_handle.write(cmd)
    try_cnt = 0
    data = None
    while is_return_value:
        ret,data = device_handle.read()
        if check_keyWord is not None and  bool(ret) and check_keyWord in data:
            print("ret: %s value:%s" %(ret,data))
            break
        elif check_keyWord is None and bool(ret) and data is not None and data.strip().isdigit():
            print("ret: %s value:%s" %(ret,data))
            break
        if try_cnt > max_line:
            logger.print_error("no found return value!")
            ret = False
            break
        try_cnt += 1
    return ret,data

def write_return_ret(device_handle:object, cmd, line=1, max_line=10):
    logger.print_warning("cmd:%s" %cmd)
    device_handle.write(cmd)
    device_handle.write("echo $?")
    try_cnt = 0
    while True:
        try_cnt += 1
        ret,data = device_handle.read(line)
        if bool(ret) and data is not None and data.strip().isdigit():
            print("ret: %s value:%s" %(ret,data))
            break
        if try_cnt > max_line:
            logger.print_error("no found return value!")
            ret = False
            break
    return ret,data

def wait_keyword_write_cmd(device_handle:object, cmd, check_keyWord=None, max_readline=4):
    try_cnt = 0
    while try_cnt < max_readline:
        ret,data = device_handle.read()
        if check_keyWord is not None and bool(ret) and check_keyWord in data:
            device_handle.write(cmd)
            break
        try_cnt += 1

def get_borad_cur_state(device_handle:object):
    board_state_in_kernel_str = '/ #'
    board_state_in_uboot_str  = 'SigmaStar #'
    borad_cur_state           = 'Unknow'
    #ret = device_handle.write('\n')
    ret,data = write_cmd(device_handle,'\n')
    if not bool(ret):
        logger.print_error("write fail")
        borad_cur_state = 'Unknow'
        return  borad_cur_state
    ret,data = device_handle.read(2)
    borad_cur_state = 'Unknow'
    if bool(ret) and data is not None:
        if bool(ret) and data is not None:
            logger.print_warning("data:{}".format(data))
        if board_state_in_uboot_str in data:
            borad_cur_state = 'at uboot'
        elif board_state_in_kernel_str in data:
            borad_cur_state = 'at kernel'
    return borad_cur_state



def get_json_content(json_path) -> dict:
    json_content = None
    json_content_dict = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                json_content = json.load(f)
                json_content_dict = dict(json_content)
        except json.JSONDecodeError:
            return None
    return json_content_dict

# show timestamp of printk log
@logger.print_line_info
def enable_printk_time(device_handle):
    cmd_printk_time_on        = "echo y > /sys/module/printk/parameters/time"
    device_handle.write(cmd_printk_time_on)

# hide timestamp of printk log
@logger.print_line_info
def disable_printk_time(device_handle):
    cmd_printk_time_off       = "echo n > /sys/module/printk/parameters/time"
    device_handle.write(cmd_printk_time_off)

def retry_burning_partition(device_handle:object, burning_tyte='all_partition'):
    result = goto_uboot()
    if result != 0:
        return result
    if burning_tyte == 'all_partition':
        write_cmd(device_handle,'\n')
    elif burning_tyte == 'uboot_partition':
        pass
    elif burning_tyte == 'kernel_partition':
        pass

def cold_reboot() -> bool:
    """
    继电器下电再上电，继电器设备不能长时间占用，使用完毕里面释放

    Args:
        None

    Returns:
        bool: result
    """
    rs232_contrl_handle = rs232_contrl(relay=int(platform.relay_port), com=platform.dev_uart)
    logger.print_info(f"init rs232_contrl_handle {platform.dev_uart}:{platform.relay_port}")
    rs232_contrl_handle.power_off()
    time.sleep(2)
    rs232_contrl_handle.power_on()
    rs232_contrl_handle.close()
    logger.print_info("closed rs232_contrl_handle.")
    return True

def ensure_file_exists(file_path) -> None:
    """
    保证传入的文件存在，不存在则创建

    Args:
        file_path: 文件路径

    Returns:
        NA
    """
    dir_path = os.path.dirname(file_path)

    if not dir_path:
        dir_path = os.getcwd()

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'a'):
            pass
        logger.print_info(f"Create file: {file_path}")
    else:
        logger.print_info(f"File existed: {file_path}")

def are_files_equal_line_by_line(file1, file2) -> int:
    """
    逐行对比两个文件

    Args:
        file1 (str): 文件1路径
        file2 (str): 文件2路径

    Returns:
        NA
    """
    with open(file1, 'r', encoding='utf-8') as f1, \
            open(file2, 'r', encoding='utf-8') as f2:
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                print(f"{line1} not equal {line2}")
                return 255
        if len(f1.readline()) == 0 and len(f2.readline()) == 0:
            result = 0
        else:
            result = 255
        return result

# def goto_uboot(device_handle:object, reboot_type="soft_reboot"):
#     cmd_uboot_reset           = "reset"
#     result = 255
#     borad_cur_state = get_borad_cur_state(device_handle)
#     if borad_cur_state == 'at uboot':
#         return 0
#     if reboot_type == 'soft_reboot':
#         write_cmd(device_handle, cmd_uboot_reset)
#     else:
#         cold_reboot()
#     for i in range(1,20):
#         write_cmd(device_handle,'\n')
#         borad_cur_state = get_borad_cur_state(device_handle)
#         if borad_cur_state == 'at uboot':
#             result = 0
#             break
#     return result

def set_board_kernel_ip(uart) -> None:
    """
    设置kernel ip

    Args:
        uart (class): 仅支持uart

    Returns:
        bool: result
    """
    set_mac = f"ifconfig eth0 hw ether {platform.mac};"
    eth0_up = "ifconfig eth0 up;"
    set_lo = "ifconfig lo 127.0.0.1;"
    set_ip = f"ifconfig eth0 {platform.board_ip} netmask {platform.mount_netmask};"
    set_gw = f"route add default gw {platform.gw};"
    uart.write(set_mac)
    uart.write(eth0_up)
    uart.write(set_lo)
    uart.write(set_ip)
    uart.write(set_gw)

def set_board_uboot_ip(uart) -> None:
    """
    设置uboot ip

    Args:
        uart (class): 仅支持uart

    Returns:
        bool: result
    """
    set_ethaddr = f"set -f ethaddr  {platform.mac};"
    set_gw = f"set -f gatewayip {platform.gw};"
    set_ip = f"set -f ipaddr {platform.board_ip};"
    set_serverip = f"set -f serverip {platform.server_ip};"
    saveenv = "saveenv"
    pri = "pri"
    uart.write(set_ethaddr)
    uart.write(set_gw)
    uart.write(set_ip)
    uart.write(set_serverip)
    uart.write(saveenv)
    uart.write(pri)

def mount_to_server(device_handle, sub_path='') -> bool:
    """
    mount到指定位置

    Args:
        device_handle (class): device

    Returns:
        bool: result
    """
    umount_cmd = "umount /mnt/"
    mount_cmd = f"mount -t nfs -o nolock {platform.mount_ip}:{platform.mount_path}/{sub_path} /mnt/"
    check_cmd = "echo $?"
    returnvalue = 255
    loopcnt = 0
    device_handle.write(umount_cmd)
    time.sleep(1)
    while returnvalue == 255 and loopcnt <= 4:
        device_handle.write(mount_cmd)
        time.sleep(5)
        device_handle.write(check_cmd)
        result, data = device_handle.read()
        if result is True and int(data) == 0:
            return True
        loopcnt += 1
    return False

def goto_uboot(uart):
    """
    在kernel进入uboot

    Args:
        uart (class): 仅支持uart

    Returns:
        bool: result
    """
    input = ""
    keyword = "SigmaStar #"
    wait_line = 2
    result, data = write_and_match_keyword(uart, input, keyword, wait_line)
    if result == True:
        logger.print_info("I'm in the uboot.")
        return True

    input = "reboot"
    keyword = "Loading Environment"
    lines = 200
    result, data = write_and_match_keyword(uart, input, keyword, lines)
    if result == True:
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
    else:
        logger.print_error(f"Not match : {keyword}")
        return False

    input = ""
    keyword = 'SigmaStar #'
    wait_line = 2
    result, data = write_and_match_keyword(uart, input, keyword, wait_line)
    if result == True:
        logger.print_info("I'm in the uboot.")
        return True
    else:
        logger.print_warning("Go to uboot fail.")
        return False

def goto_kernel(device, reset_wait_time = 20, retry = 3):
    """
    判断是否在kernel,如果在uboot则切换到kernel

    Args:
        device (class): 仅支持uart
        reset_wait_time (int): reset后等待时间
        retry (int): 尝试次数

    Returns:
        bool: result
    """
    while retry > 0:
        cmd = "cd /"
        wait_keyword = "/ #"
        wait_line = 2
        status, data = write_and_match_keyword(device, cmd, wait_keyword, wait_line)
        if status is True:
            logger.print_info("I'm in the kernel.")
            return True

        cmd = ""
        wait_keyword = 'SigmaStar #'
        wait_line = 2
        status, data = write_and_match_keyword(device, cmd, wait_keyword, wait_line)
        if status is True:
            logger.print_info("I'm in the uboot.")
            device.write("reset")
            time.sleep(reset_wait_time)
        retry -= 1
    logger.print_error("Go to kernel fail.")
    return False

def write_and_match_keyword(device_handle, input, keyword, lines = 100):
    """
    发送命令获取关键字所在的行,read的默认超时时间为5S,如果5S未获取到任何一行数据则退出

    Args:
        input (str): 命令
        keyword (str): 匹配的关键字
        lines (int): 查找的最大行数

    Returns:
        bool,data: result和匹配到的行
    """
    result = device_handle.write(input)
    if result is True:
        result,data = match_keyword(device_handle, keyword, lines)
        return result,data
    else:
        logger.print_warning(f"Write {input} fail.")
        return False,''

def match_keyword(device_handle, keyword, lines = 100):
    """
    获取关键字所在的行,read的默认超时时间为5S,如果5S未获取到任何一行数据则退出

    Args:
        keyword (str): 匹配的关键字
        lines (int): 查找的最大行数

    Returns:
        bool,data: result和匹配到的行
    """
    curr_line = 0
    while curr_line < lines:
        result,data = device_handle.read()
        if result is True:
            if keyword in data:
                return True,data
            else:
                curr_line += 1
        else:
            logger.print_warning("Read timeout: 5S")
            break
    return False,''

def nothing():
    pass

def burning_image() -> None:
    case_name = "burning_image"
    uart = Client(case_name)
    cold_reboot()
    keyword = 'Loading Environment'
    result, data = match_keyword(uart, keyword)
    if result is True:
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
    else:
        logger.print_error(f"Not match : {keyword}")
        return False
    input = ""
    keyword = 'SigmaStar #'
    wait_line = 2
    result, data = write_and_match_keyword(uart, input, keyword, wait_line)
    if result == True:
        logger.print_info("I'm in the uboot.")
    else:
        logger.print_warning("Go to uboot fail.")
        return False

    set_board_uboot_ip(uart)
    estar_cmd = f"estar {platform.image_path}"
    uart.write(estar_cmd)

    uart.close()

def read_register(device, bank, offset, is_kernel=True):
    result = 255
    str_regVal = ""
    read_line_cnt = 0
    max_read_lines = 10
    is_register_value_ready = 0
    cmd_read_register = ""
    if is_kernel == True:
        cmd_read_register = "/customer/riu_r {} {}".format(bank, offset)
    else:
        cmd_read_register = "riu_r {} {}".format(bank, offset)
    device.write(cmd_read_register)

    while True:
        if read_line_cnt > max_read_lines:
            logger.print_error("read lines exceed max_read_lines:%d" %(max_read_lines))
            break

        status, line = device.read()
        if status  == True:
            read_line_cnt += 1
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if "BANK" in line:
                is_register_value_ready = 1
                continue

            if is_register_value_ready == 1 :
                pattern = re.compile(r'0x([A-Fa-f0-9]{4})')
                match = pattern.search(line)
                if match:
                    str_regVal = match.group(0)
                    result = 0
                    logger.print_info(f"bank:{bank} offset:{offset} register value is {str_regVal}")
                    break
        else:
            logger.print_error("read line:%d fail" %(read_line_cnt))
            break
    return result, str_regVal

def get_bit_value(str_hex, position):
        num = int(str_hex, 16)
        bit = (num >> position) & 1
        return bit