#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/23 14:55:51
# @file        : str_crc_var.py
# @description :


################### CASE STR_CRC ################
# PLATFORM_STR_CRC: success flag of STR_CRC
# PLATFORM_STR_CRC_FAIL: fail flag of STR_CRC

str_crc_ok = "CRC check success"
str_crc_fail = "CRC check fail"
suspend_crc_start_addr = 0x20008000
suspend_crc_end_addr = 0x30000000