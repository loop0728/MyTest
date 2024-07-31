import time
import os
import sys
import fnmatch


# Global variable definitions
############################################################
PLATFORM_VALUE={}
############################################################

"""
Function Name: server_add_value_to_global_dict
Description: add key:value in dict_para.
    - dict_para: dict you want add key:value
    - key: key to add in dict_para
    - value: value to add in dict_para
Return Value:  0 success   -1 fail.
Notes:na

Author:mengke
"""
def server_add_value_to_global_dict(dict_para,key, value):
    if key.strip() == "" or key == None:
        print(f"\033[91m[SYSTEM_ERROR] {key} is invalid \033[0m")
        return -1

    if key in dict_para:
        print(f"\033[93m[SYSTEM_WARN] {key} is in {dict_para},{key}:{dict_para[key]},now will be replaced by {key}:{value} \033[0m")
    dict_para[key] = value
    return 0

"""
Function Name: server_get_value_from_global_dict
Description: get value use key.
    - dict_para: dict you want get value from
    - key: key  in dict_para
    - result: key's value in dict_para
Return Value:  0 success   -1 fail -2 not found.
Notes:na

Author:mengke
"""
def server_get_value_from_global_dict(dict_para,key,result):
    if key.strip() == "" or key == None:
        print(f"\033[91m[SYSTEM_ERROR] {key} is invalid \033[0m")
        return -1

    if '*' in key:
        filtered_files = fnmatch.filter(dict_para.keys(), key)
        if len(filtered_files):
            for key in filtered_files:
                result.append(dict_para[key])
            return 0
        else:
            print(f"\033[93m[SYSTEM_WARN] {key} is not found in dict \033[0m")
            return -2
    else:
        if key in dict_para:
            result.append(dict_para[key])
            return 0
        else:
            print(f"\033[93m[SYSTEM_WARN] {key} is not in dict \033[0m")
            return -2

"""
Function Name: server_load_platform
Description: Parse the parameters in the platform into global variables: PLATFORM_VALUE.
Parameters:
    - na:
Return Value:  0 success   -1 fail.
Notes: na.
Author: mengke

"""
def server_load_platform():
    platform_filename = './platform.sh'
    if not os.path.exists(platform_filename):
        print(f"\033[91m[SYSTEM_ERROR] {platform_filename} is not exist\033[0m")
        return -1
    with open(platform_filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#") or line.strip() == "":
            continue

        left_value=line.split('=')[0].strip()
        right_value=line.split('=')[1].strip()
        ret = server_add_value_to_global_dict(PLATFORM_VALUE,left_value, right_value)
        if ret == -1:
            print(f"\033[91m[SYSTEM_ERROR] server_add_value_to_global_dict failed to execute\033[0m")

    return 0

"""
Function Name: server_get_platform_extract_value
Description: Get extract value from platform.sh using variable.
Parameters:
    - variable: The lvalue in platform.sh
Return Value:  value success   none fail.
Notes: You cannot replace an item with an rvalue of a string.
Author: mengke

"""
def server_get_platform_extract_value(variable):
    if not os.path.exists('./platform.sh'):
        print(f"\033[91m[SYSTEM_ERROR] ./platform.sh is not exist \033[0m")
        return None
    if len(PLATFORM_VALUE) == 0:
        ret=server_load_platform()
        if ret == -1:
            print(f"\033[91m[SYSTEM_ERROR] server_load_platform failed to execute \033[0m")
            return -1

    result=[]
    ret=server_get_value_from_global_dict(PLATFORM_VALUE,variable,result)
    if ret == 0:
        return result[0]
    else:
        with open('./platform.sh', 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith(variable):
                value = line.split('=')[1].strip()
                return value

    print(f"\033[93m[SYSTEM_WARN] {variable} is not found \033[0m")
    return None


mode = server_get_platform_extract_value("PLATFORM_mount_mode")
mac = server_get_platform_extract_value("PLATFORM_mount_mac")
gw = server_get_platform_extract_value("PLATFORM_mount_gw")
board_ip = server_get_platform_extract_value("PLATFORM_board_ip")
mount_ip = server_get_platform_extract_value("PLATFORM_mount_ip")
mount_netmask = server_get_platform_extract_value("PLATFORM_mount_netmask")
mount_user = server_get_platform_extract_value("PLATFORM_mount_user")
mount_user_password = server_get_platform_extract_value("PLATFORM_mount_user_password")
mount_path = server_get_platform_extract_value("PLATFORM_mount_path")

log_path=server_get_platform_extract_value("LOG")
appdir = server_get_platform_extract_value('APP')
uart_port = server_get_platform_extract_value("PLATFORM_UART")
dev_uart = server_get_platform_extract_value("PLATFORM_RELAY")
relay_port = server_get_platform_extract_value("PLATFORM_RELAY_PORT")
net_connect_port = server_get_platform_extract_value("PLATFORM_NET_CONNECT_PORT")

ttff_target = server_get_platform_extract_value("PLATFORM_TTFF")
ttcl_target = server_get_platform_extract_value("PLATFORM_TTCL")

str_target = server_get_platform_extract_value("PLATFORM_STR_TARGET")
str_kmsg = server_get_platform_extract_value("PLATFORM_REDIRECT_KMSG")
suspend_entry = server_get_platform_extract_value("PLATFORM_SUSPEND_ENTRY")
suspend_exit = server_get_platform_extract_value("PLATFORM_SUSPEND_EXIT")
app_resume = server_get_platform_extract_value("PLATFORM_APP_RESUME")
booting_time = server_get_platform_extract_value("PLATFORM_BOOTING_TOTAL_COST")

str_crc_ok = server_get_platform_extract_value("PLATFORM_STR_CRC_OK")
str_crc_fail = server_get_platform_extract_value("PLATFORM_STR_CRC_FAIL")
suspend_crc_start_addr = server_get_platform_extract_value("PLATFORM_SUSPEND_CRC_START_ADDR")
suspend_crc_end_addr = server_get_platform_extract_value("PLATFORM_SUSPEND_CRC_END_ADDR")

ttff_ttcl_counts = int(server_get_platform_extract_value("PLATFORM_TTFF_TTCL_COUNTS"))
reboot_counts = int(server_get_platform_extract_value("PLATFORM_REBOOT_COUNTS"))
str_counts = int(server_get_platform_extract_value("PLATFORM_STR_COUNTS"))
str_crc_counts = int(server_get_platform_extract_value("PLATFORM_STR_CRC_COUNTS"))
OS_switch_counts = int(server_get_platform_extract_value("PLATFORM_OS_SWITCH_COUNTS"))
change_fps_counts = int(server_get_platform_extract_value("PLATFORM_CHANGE_FPS_COUNTS"))