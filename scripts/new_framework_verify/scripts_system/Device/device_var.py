#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/02 12:15:05
# @file        : device_var.py
# @description : 兼容设备参数

CHIP = 'I6DW'
OS = 'purelinux'


if OS == 'purelinux':
    telnet_login = True
else:
    telnet_login = False
