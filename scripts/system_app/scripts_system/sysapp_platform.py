"""sysapp config file"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

CHIP_NAME = "iford"
APP = "/customer"
LOG_PATH = "./out/uart.log"

#################### mount ####################
# PLATFORM_mount_ip: ip of the mount server
# PLATFORM_board_ip: ip of the board
# PLATFORM_board_mac: mac address of the board
# PLATFORM_board_mac_type: emac or gmac
# PLATFORM_mount_gw: gateway of the board
# PLATFORM_mount_netmask: netmask of the board
# PLATFORM_mount_user: the user name(just for cifs)
# PLATFORM_mount_user_password: the password of user's PC(just for cifs)
# PLATFORM_mount_path: the mount path
# PLATFORM_mount_mode: mount mode, nfs or cifs

PLATFORM_MOUNT_IP = "172.19.30.183"
PLATFORM_BOARD_IP = "172.19.26.93"
PLATFORM_BOARD_MAC = "00:70:42:00:00:23"
PLATFORM_BOARD_MAC_TYPE = "emac"
PLATFORM_MOUNT_GW = "172.19.26.254"
PLATFORM_MOUNT_NETMASK = "255.255.255.0"
PLATFORM_MOUNT_USER = ""
PLATFORM_MOUNT_USER_PASSWORD = ""
PLATFORM_MOUNT_PATH = "atstream/IT/I6DW/iford_systemapp_testcase"
PLATFORM_MOUNT_MODE = "nfs"
PLATFORM_SERVER_IP = "172.19.26.53"
PLATFORM_IMAGE_PATH = ""
PLATFORM_LOCAL_MOUNT_PATH = "/stream/IT/I6DW/iford_systemapp_testcase"

#################### DEVICE ####################
# PLATFORM_UART: the device of uart, for Windows,it's COM, and for Linux,it's /dev/ttyUSB
# PLATFORM_RELAY: the device of relay in Linux, such as /dev/ttyUSB1
# PLATFORM_RELAY_PORT: the port number of relay, such as 1
PLATFORM_UART = "/dev/i6dw_nand_uart_8"
PLATFORM_RELAY = "/dev/relay_uart"
PLATFORM_RELAY_PORT = 8
PLATFORM_NET_CONNECT_PORT = 8800 + PLATFORM_RELAY_PORT

#################### COMMON ####################
PLATFORM_DEBUG_MODE = ""
