#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""burning interfaces"""

from suite.common.sysapp_common_logger import logger
import suite.common.sysapp_common_utils as sys_common_utils
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
import sysapp_platform as platform
from sysapp_client import SysappClient

def burning_image():
    """Burning image."""
    case_name = "burning_image"
    uart = SysappClient(case_name)
    SysappRebootOpts.cold_reboot()
    keyword = "Loading Environment"
    result, _ = sys_common_utils.match_keyword(uart, keyword)
    if result is True:
        uart.write("")
        uart.write("")
        uart.write("")
        uart.write("")
    else:
        logger.error(f"Not match : {keyword}")
        return False
    ss_input = ""
    keyword = "SigmaStar #"
    wait_line = 2
    result, _ = sys_common_utils.write_and_match_keyword(uart, ss_input, keyword, wait_line)
    if result is True:
        logger.info("I'm in the uboot.")
    else:
        logger.warning("Go to uboot fail.")
        return False

    SysappNetOpts.setup_network(uart)
    estar_cmd = f"estar {platform.PLATFORM_IMAGE_PATH}"
    uart.write(estar_cmd)

    return True

def retry_burning_partition(device: object, burning_tyte="all_partition"):
    """
    pass

    Args:
        pass (str): pass

    Returns:
        bool: result
    """
    result = SysappRebootOpts.reboot_to_uboot(device)
    if result != 0:
        return result
    if burning_tyte == "all_partition":
        sys_common_utils.write_cmd(device, "\n")
    elif burning_tyte == "uboot_partition":
        pass
    elif burning_tyte == "kernel_partition":
        pass
    return result
