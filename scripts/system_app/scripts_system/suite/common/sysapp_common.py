"""Common func"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import time
import json
from suite.common.sysapp_common_logger import logger
from device.sysapp_dev_relay import SysappDevRelay
import sysapp_platform as platform
from sysapp_client import SysappClient


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
                # logger.print_warning("{}:{}".format(key_str,result))
        else:
            logger.print_warning(
                f"no find {key_str} key, will use default value"
            )
    return result


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
        logger.print_error(f"modfiy_dev_json_file:json_name[{file_name}] is vaild!")
        return result
    cat_file_cmd_grep_key = f"cat {file_name} | grep {key} | wc -l"
    logger.print_warning(cat_file_cmd_grep_key)
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
    logger.print_warning(modfiy_key_value_cmd)

    write_cmd(device_handle, modfiy_key_value_cmd)
    result, data = get_write_cmd_ret(device_handle)
    if not bool(result):
        if data is not None:
            logger.print_error(data)
        return 255
    cat_file_cmd_grep_key = f"cat {file_name} | grep {key} | wc -l"

    result, data = write_cmd(device_handle, cat_file_cmd_grep_key, True)
    if not bool(result):
        if data is not None:
            logger.print_error(data)
    result, data = get_write_cmd_ret(device_handle)
    if not bool(result):
        if data is not None:
            logger.print_error(data)
        return 255
    if data.strip().isdigit():
        result = int(data)
    else:
        result = 255
        if data is not None:
            logger.print_error(f"data:{data}")
    return result


# check current status of the dev, if the dev is at uboot of at kernel, then reboot the dev
@logger.print_line_info
def reboot_dev(device_handle: object, reboot_type="soft_reboot"):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    reboot_timeout = 180
    cmd_uboot_reset = "reset"
    cmd_kernel_reboot = "reboot"
    trywait_time = 0
    result = 255
    if reboot_type == "soft_reboot":
        for _ in range(1, 20):
            borad_cur_state = get_borad_cur_state(device_handle)
            if borad_cur_state != "Unknow":
                break
        if borad_cur_state == "Unknow":
            logger.print_error("get cur state is unknow")
            return result

        if borad_cur_state == "at uboot":
            borad_cur_state = "Unknow"
            write_cmd(device_handle, cmd_uboot_reset)
            time.sleep(6)  # wait uboot run finnish. for prevent goto uboot cmdline
        elif borad_cur_state == "at kernel":
            borad_cur_state = "Unknow"
            write_cmd(device_handle, cmd_kernel_reboot)
            ret, data = device_handle.read()
            if bool(ret) and data is not None:
                ret, data = device_handle.read()
                if bool(ret) and data is not None:
                    logger.print_warning(data)
                    if "sh: can't execute" in data:
                        return result
                time.sleep(6)  # wait uboot run finnish. for prevent goto uboot cmdline
            else:
                return result

    elif reboot_type != "soft_reboot":
        cold_reboot()
        time.sleep(6)  # wait uboot run finnish. for prevent goto uboot cmdline
    logger.print_error("reboot_dev")
    while True:
        borad_cur_state = get_borad_cur_state(device_handle)
        if borad_cur_state == "at kernel":
            result = 0
            logger.print_info(f"borad_cur_state:{borad_cur_state}")
            break
        elif borad_cur_state == "at uboot":
            write_cmd(device_handle, cmd_uboot_reset)
            borad_cur_state = "Unknow"
            time.sleep(6)  # wait uboot run finnish. for prevent goto uboot cmdline
        else:
            time.sleep(1)
            trywait_time = trywait_time + 1
            if trywait_time > reboot_timeout:
                break
    return result


def reboot_board(device_handle: object, reboot_type="soft_reboot"):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    logger.print_error("reboot_board")
    result = 255
    if reboot_type == "soft_reboot":
        result = reboot_dev(device_handle, reboot_type)
    elif reboot_type == "cold_reboot":
        result = cold_reboot()
    return result


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
            logger.print_error(f"ret: {ret} value:{data}")
            logger.print_error("no found return value!")
            ret = False
            break
    return ret, data


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
    logger.print_warning(f"cmd:{cmd}")
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
            logger.print_error("no found return value!")
            ret = False
            break
        try_cnt += 1
    return ret, data


def write_return_ret(device_handle: object, cmd, line=1, max_line=10):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    logger.print_warning(f"cmd:{cmd}")
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
            logger.print_error("no found return value!")
            ret = False
            break
    return ret, data


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


def get_borad_cur_state(device_handle: object):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    board_state_in_kernel_str = "/ #"
    board_state_in_uboot_str = "SigmaStar #"
    borad_cur_state = "Unknow"
    # ret = device_handle.write('\n')
    ret, data = write_cmd(device_handle, "\n")
    if not bool(ret):
        logger.print_error("write fail")
        borad_cur_state = "Unknow"
        return borad_cur_state
    ret, data = device_handle.read(2)
    borad_cur_state = "Unknow"
    if bool(ret) and data is not None:
        if bool(ret) and data is not None:
            logger.print_warning(f"data:{data}")
        if board_state_in_uboot_str in data:
            borad_cur_state = "at uboot"
        elif board_state_in_kernel_str in data:
            borad_cur_state = "at kernel"
    return borad_cur_state


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


# show timestamp of printk log
@logger.print_line_info
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
@logger.print_line_info
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


def retry_burning_partition(device_handle: object, burning_tyte="all_partition"):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    result = goto_uboot(device_handle)
    if result != 0:
        return result
    if burning_tyte == "all_partition":
        write_cmd(device_handle, "\n")
    elif burning_tyte == "uboot_partition":
        pass
    elif burning_tyte == "kernel_partition":
        pass
    return result


def cold_reboot():
    """
    Relay powered off and then powered on again.

    Returns:
        bool: result
    """
    relay_name= platform.PLATFORM_RELAY
    relay_no = platform.PLATFORM_RELAY_PORT
    rs232_contrl_handle = SysappDevRelay(relay=relay_no, port=relay_name)
    logger.print_info(f"init rs232_contrl_handle {relay_name}:{relay_no}")
    rs232_contrl_handle.power_off()
    time.sleep(2)
    rs232_contrl_handle.power_on()
    rs232_contrl_handle.disconnect()
    logger.print_info("closed rs232_contrl_handle.")
    return True


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
        logger.print_info(f"Create file: {file_path}")
    else:
        logger.print_info(f"File existed: {file_path}")


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


def set_board_kernel_ip(uart) -> None:
    """
    Set board kernel ip.

    Args:
        uart (class): only support uart.

    Returns:
        bool: result
    """
    set_mac = f"ifconfig eth0 hw ether {platform.PLATFORM_BOARD_MAC};"
    eth0_up = "ifconfig eth0 up;"
    set_lo = "ifconfig lo 127.0.0.1;"
    set_ip = (f"ifconfig eth0 {platform.PLATFORM_BOARD_IP} "
              f"netmask {platform.PLATFORM_MOUNT_NETMASK};")
    set_gw = f"route add default gw {platform.PLATFORM_MOUNT_GW};"
    uart.write(set_mac)
    uart.write(eth0_up)
    uart.write(set_lo)
    uart.write(set_ip)
    uart.write(set_gw)


def set_board_uboot_ip(uart) -> None:
    """
    Set board uboot ip.

    Args:
        uart (class): only support uart.

    Returns:
        bool: result
    """
    set_ethaddr = f"set -f ethaddr  {platform.PLATFORM_BOARD_MAC};"
    set_gw = f"set -f gatewayip {platform.PLATFORM_MOUNT_GW};"
    set_ip = f"set -f ipaddr {platform.PLATFORM_BOARD_IP};"
    set_serverip = f"set -f serverip {platform.PLATFORM_SERVER_IP};"
    saveenv = "saveenv"
    pri = "pri"
    uart.write(set_ethaddr)
    uart.write(set_gw)
    uart.write(set_ip)
    uart.write(set_serverip)
    uart.write(saveenv)
    uart.write(pri)


def mount_to_server(device_handle, sub_path="") -> bool:
    """
    mount to server path

    Args:
        device_handle (class): device

    Returns:
        bool: result
    """
    umount_cmd = "umount /mnt/"
    mount_cmd = (f"mount -t nfs -o nolock {platform.PLATFORM_MOUNT_IP}:"
                 f"{platform.PLATFORM_MOUNT_PATH}/{sub_path} /mnt/")
    check_cmd = "echo $?"
    returnvalue = 255
    returncode = 0
    loopcnt = 0
    device_handle.write(umount_cmd)
    time.sleep(1)
    while returnvalue == 255 and loopcnt <= 4:
        if returncode != -1:
            device_handle.write(mount_cmd)
        time.sleep(5)
        device_handle.write(check_cmd)
        result, data = device_handle.read()
        try:
            returncode = int(data)
        except Exception as exce:
            logger.print_info(f"{data} cause {exce}")
            returncode = -1
        if result is True and returncode == 0:
            return True
        loopcnt += 1
    return False


def goto_uboot(uart):
    """
    kernel to uboot.

    Args:
        uart (object): only support uart

    Returns:
        bool: result
    """
    ss_input = ""
    keyword = "SigmaStar #"
    wait_line = 2
    result, _ = write_and_match_keyword(uart, ss_input, keyword, wait_line)
    if result is True:
        logger.print_info("I'm in the uboot.")
        return True

    ss_input = "reboot"
    keyword = "Loading Environment"
    lines = 200
    result, _ = write_and_match_keyword(uart, ss_input, keyword, lines)
    if result is True:
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
    else:
        logger.print_error(f"Not match : {keyword}")
        return False

    ss_input = ""
    keyword = "SigmaStar #"
    wait_line = 2
    result, _ = write_and_match_keyword(uart, ss_input, keyword, wait_line)
    if result is True:
        logger.print_info("I'm in the uboot.")
        return True
    else:
        logger.print_warning("Go to uboot fail.")
        return False


def goto_kernel(device, reset_wait_time=20, retry=3):
    """
    go to kernel.

    Args:
        device (object): only support uart
        reset_wait_time (int): reset wait time
        retry (int): retry cnt

    Returns:
        bool: result
    """
    while retry > 0:
        cmd = "cd /"
        wait_keyword = "/ #"
        wait_line = 2
        status, _ = write_and_match_keyword(device, cmd, wait_keyword, wait_line)
        if status is True:
            logger.print_info("I'm in the kernel.")
            return True

        cmd = ""
        wait_keyword = "SigmaStar #"
        wait_line = 2
        status, _ = write_and_match_keyword(device, cmd, wait_keyword, wait_line)
        if status is True:
            logger.print_info("I'm in the uboot.")
            device.write("reset")
            time.sleep(reset_wait_time)
        retry -= 1
    logger.print_error("Go to kernel fail.")
    return False


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
        logger.print_warning(f"Write {ss_input} fail.")
        return False, ""


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
            logger.print_warning("Read timeout: 5S")
            break
    return False, ""


def nothing():
    """Nothing"""
    pass


def burning_image():
    """Burning image."""
    case_name = "burning_image"
    uart = SysappClient(case_name)
    cold_reboot()
    keyword = "Loading Environment"
    result, _ = match_keyword(uart, keyword)
    if result is True:
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
    else:
        logger.print_error(f"Not match : {keyword}")
        return False
    ss_input = ""
    keyword = "SigmaStar #"
    wait_line = 2
    result, _ = write_and_match_keyword(uart, ss_input, keyword, wait_line)
    if result is True:
        logger.print_info("I'm in the uboot.")
    else:
        logger.print_warning("Go to uboot fail.")
        return False

    set_board_uboot_ip(uart)
    estar_cmd = f"estar {platform.PLATFORM_IMAGE_PATH}"
    uart.write(estar_cmd)

def get_ko_insmod_state(uart:object, koname=''):
    """ get_ko_insmod_state
        uart (object): 仅支持uart
        koname (str): mi_sys
    """
    result = ""
    cmd = f"lsmod | grep {koname} | wc -l"
    # 检查串口信息
    res = uart.write(cmd)
    if res is False:
        logger.print_error(f"{uart} is disconnected.")
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

def get_current_os(uart:object):
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

def check_insmod_ko(uart:object, koname=''):
    """ check_insmod_ko
        uart (object): 仅支持uart
        koname (str): mi_sys
    """
    wait_keyword = "none"
    ko_path = f"/config/modules/5.10/{koname}.ko"
    data = get_ko_insmod_state(uart, f"{koname}")
    if wait_keyword in data:
        cmd = f"insmod {ko_path}"
        logger.print_warning(f"we will {cmd}")
        uart.write(cmd)
        result = "true"
    else:
        logger.print_warning(f"we no need insmod {koname}")
        result = "false"
    return result

def switch_os_aov(uart:object, target_os=''):
    """ switch_os by aov pipe case
        uart (object): 仅支持uart
        target_os (str): purelinux or dualos
    """
    result = 0
    cur_os = get_current_os(uart)
    if cur_os == target_os:
        logger.print_warning(f"current os is match {target_os}")
        return 0

    logger.print_warning(f"will switch to OS({target_os})!")
    if target_os == "dualos":
        cmd = "cd /customer/sample_code/bin/"
        uart.write(cmd)
        wait_keyword = "/customer/sample_code/bin #"
        status, data = uart.read()
        if status is True:
            if wait_keyword not in data:
                return 255
        else:
            logger.print_error(f"Read fail,no keyword: {wait_keyword}")
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

def read_register(device:object, bank, offset, is_kernel=True):
    """run cmd on server
    Args:
        cmd (device): device handle
        bank (str): register bank address
        offset (str): register offset
        is_kernel (bool): if executed at kernel phase
    Returns:
        result (int): execute success, return 0; else, return 255
    """
    result = 255
    str_reg_value = ""
    read_line_cnt = 0
    max_read_lines = 10
    is_register_value_ready = 0
    cmd_read_register = ""
    if is_kernel:
        cmd_read_register = f"/customer/riu_r {bank} {offset}"
    else:
        cmd_read_register = f"riu_r {bank} {offset}"
    device.write(cmd_read_register)

    while True:
        if read_line_cnt > max_read_lines:
            logger.print_error(f"read lines exceed max_read_lines:{max_read_lines}")
            break

        status, line = device.read()
        if status:
            read_line_cnt += 1
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if "BANK" in line:
                is_register_value_ready = 1
                continue

            if is_register_value_ready == 1:
                pattern = re.compile(r'0x([A-Fa-f0-9]{4})')
                match = pattern.search(line)
                if match:
                    str_reg_value = match.group(0)
                    result = 0
                    logger.print_info(f"bank:{bank} offset:{offset} "
                                      f"register value is {str_reg_value}")
                    break
        else:
            logger.print_error(f"read line:{read_line_cnt} fail")
            break
    return result, str_reg_value

def get_bit_value(str_hex, position):
    """run cmd on server
    Args:
        str_hex (str): register value
        position (int): bit offset
    Returns:
        result (int): bit value, 0 or 1
    """
    num = int(str_hex, 16)
    bit = (num >> position) & 1
    return bit
