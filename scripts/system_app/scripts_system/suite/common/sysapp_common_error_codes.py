"""Error Codes and its corresponding event"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
import suite.common.sysapp_common_utils as SysappUtils
#import suite.common.sysapp_common_burning_opts as sys_common_burning

EVENT_HANDLERS = {
    SysappErrorCodes.SUCCESS    : SysappUtils.nothing,
    SysappErrorCodes.FAIL       : SysappUtils.nothing,
    SysappErrorCodes.REBOOT     : SysappRebootOpts.cold_reboot,
    SysappErrorCodes.ESTAR      : SysappUtils.nothing,
    SysappErrorCodes.TOLINUX    : SysappUtils.nothing,
}
