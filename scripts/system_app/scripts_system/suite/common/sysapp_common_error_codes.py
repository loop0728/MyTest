"""Error Codes and its corresponding event"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum
import suite.common.sysapp_common as sys_common


# pylint: disable=C0103
class ErrorCodes(Enum):
    """Error Codes Enum"""
    SUCCESS = 0
    FAIL = 1
    REBOOT = 2
    ESTAR = 3
    TOLINUX = 4


event_handlers = {
    ErrorCodes.SUCCESS    : sys_common.nothing,
    ErrorCodes.FAIL       : sys_common.nothing,
    ErrorCodes.REBOOT     : sys_common.cold_reboot,
    ErrorCodes.ESTAR      : sys_common.burning_image,
    ErrorCodes.TOLINUX    : sys_common.burning_image,
}
