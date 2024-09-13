#!/bin/sh
CHIP_NAME=iford
APP=/customer
LOG=./out/uart.log

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

PLATFORM_mount_ip=172.19.30.183
PLATFORM_board_ip=172.19.26.93
PLATFORM_mount_mac=00:70:42:00:00:23
PLATFORM_mount_gw=172.19.26.254
PLATFORM_mount_netmask=255.255.255.0
PLATFORM_mount_user=xxx
PLATFORM_mount_user_password=xxx
PLATFORM_mount_path=atstream/IT/I6DW/iford_systemapp_testcase
PLATFORM_mount_mode=nfs
PLATFORM_server_ip=172.19.26.53
PLATFORM_image_path=xxx
PLATFORM_local_mount_path=/stream/IT/I6DW/iford_systemapp_testcase

#################### DEVICE ####################
# PLATFORM_UART: the device of uart, for Windows,it's COM, and for Linux,it's /dev/ttyUSB
# PLATFORM_RELAY: the device of relay in Linux, such as /dev/ttyUSB1
# PLATFORM_RELAY_PORT: the port number of relay, such as 1
PLATFORM_UART=/dev/i6dw_nand_uart_7
PLATFORM_RELAY=/dev/relay_uart
PLATFORM_RELAY_PORT=7
PLATFORM_NET_CONNECT_PORT=8807

PLATFORM_DEBUG_MODE=xxx