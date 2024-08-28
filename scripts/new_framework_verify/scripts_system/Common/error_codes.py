#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/27 21:23:20
# @file        : error_codes.py
# @description :

from enum import Enum
import Common.system_common as sys_common

class ErrorCodes(Enum):
    SUCCESS    = 0
    FAIL       = 1
    REBOOT     = 2
    ESTAR      = 3
    TOLINUX    = 4

event_handlers = {
    ErrorCodes.SUCCESS    : sys_common.nothing,
    ErrorCodes.FAIL       : sys_common.nothing,
    ErrorCodes.REBOOT     : sys_common.cold_reboot,
    ErrorCodes.ESTAR      : sys_common.burning_image,
    ErrorCodes.TOLINUX    : sys_common.burning_image
}