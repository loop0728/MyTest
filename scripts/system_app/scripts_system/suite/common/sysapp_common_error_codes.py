"""Error Codes and its corresponding event"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
import suite.common.sysapp_common_utils as sys_common_utils
import suite.common.sysapp_common_burning_opts as sys_common_burning

event_handlers = {
    SysappErrorCodes.SUCCESS    : sys_common_utils.nothing,
    SysappErrorCodes.FAIL       : sys_common_utils.nothing,
    SysappErrorCodes.REBOOT     : SysappRebootOpts.cold_reboot,
    SysappErrorCodes.ESTAR      : sys_common_burning.burning_image,
    SysappErrorCodes.TOLINUX    : sys_common_burning.burning_image,
}
