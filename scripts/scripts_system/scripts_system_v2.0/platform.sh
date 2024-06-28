#!/bin/sh
CHIP_NAME=iford
APP=/customer
LOG=/home/auto_test/it--stable_i6dw.D3.demo.aov.random--Daily/output/testcaselog/uart.log

# Check_Register   : Whether to determine by the register,1 yes ,0 no
# DEBUG_LEVEL      : Print grade, 0: juset error; 1: error + warn; 2: error + warn + info
# Network_Ping_Operation : Whether to enable network fluctuation measures,All shell commands on the runboard trigger this condition 1:enable ,0:disable

#DEBUG_LEVEL=2
#Check_Register=0
#Network_Ping_Operation=1

#################### mount ####################
# PLATFORM_mount_ip: ip of the mount server
# PLATFORM_board_ip: ip of the board
# PLATFORM_mount_mac: mac address of the board
# PLATFORM_mount_gw: gateway of the board
# PLATFORM_mount_netmask: netmask of the board
# PLATFORM_mount_user: the user name(just for cifs)
# PLATFORM_mount_user_password: the password of user's PC(just for cifs)
# PLATFORM_mount_path: the mount path
# PLATFORM_mount_mode: mount mode, nfs or cifs

PLATFORM_mount_ip=xxx
PLATFORM_board_ip=xxx
PLATFORM_mount_mac=xxx
PLATFORM_mount_gw=xxx
PLATFORM_mount_netmask=xxx
PLATFORM_mount_user=xxx
PLATFORM_mount_user_password=xxx
PLATFORM_mount_path=/nfs
PLATFORM_mount_mode=cifs

#################### DEVICE ####################
# PLATFORM_UART: the device of uart, for Windows,it's COM, and for Linux,it's /dev/ttyUSB
# PLATFORM_RELAY: the device of relay in Linux, such as /dev/ttyUSB1
# PLATFORM_RELAY_PORT: the port number of relay, such as 1
PLATFORM_UART=/dev/i6dw_nand_uart_4
PLATFORM_RELAY=/dev/relay_uart
PLATFORM_RELAY_PORT=4
PLATFORM_NET_CONNECT_PORT=8804

################## CASE TTFF/TTCL ###############
# PLATFORM_TTFF: the target of TTFF
# PLATFORM_TTCL: the target of TTCL
PLATFORM_TTFF=20000
PLATFORM_TTCL=350000
PLATFORM_TIME_FILE=./out/ttff_ttcl/time.txt

##################### CASE STR ##################
# PLATFORM_STR: the target of STR
# PLATFORM_REDIRECT_KMSG: the tmp file to save STR kmsg
PLATFORM_STR=120000
PLATFORM_REDIRECT_KMSG=/tmp/.str_kmsg
PLATFORM_SUSPEND_ENTRY="PM: suspend entry"
PLATFORM_SUSPEND_EXIT="PM: suspend exit"
PLATFORM_APP_RESUME="PM: app resume"
PLATFORM_BOOTING_TOTAL_COST="Total cost:"

################### CASE STR_CRC ################
# PLATFORM_STR_CRC: success flag of STR_CRC
# PLATFORM_STR_CRC_FAIL: fail flag of STR_CRC
PLATFORM_STR_CRC_OK="CRC check success"
PLATFORM_STR_CRC_FAIL="CRC check fail"
PLATFORM_UBOOT_PROMPT="SigmaStar"
PLATFORM_KERNEL_PROMPT="mi_sys"
PLATFORM_SUSPEND_CRC_START_ADDR=0x20008000
PLATFORM_SUSPEND_CRC_END_ADDR=0x30000000

################## CASE STRESS ###############
# PLATFORM_TTFF_TTCL_COUNTS: the number of TTFF_TTCL case
# PLATFORM_REBOOT_COUNTS: the number of REBOOT case
# PLATFORM_STR_COUNTS: the number of STR case
# PLATFORM_STR_CRC_COUNTS: the number of STR_CRC case
# PLATFORM_STR_CRC_COUNTS: the number of OS_switch case
# PLATFORM_CHANGE_FPS_COUNTS: the number of CHANGE_FPS case
PLATFORM_TTFF_TTCL_COUNTS=5
PLATFORM_REBOOT_COUNTS=5
PLATFORM_STR_COUNTS=5
PLATFORM_STR_CRC_COUNTS=5
PLATFORM_OS_SWITCH_COUNTS=5
PLATFORM_CHANGE_FPS_COUNTS=5