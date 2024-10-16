""" SysappPtreeThread version 0.0.1 """
import os
import time
import sysapp_platform as platform
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
from run_env.workthread_base import SysappWorkThreadBase

class SysappPtreeThread(SysappWorkThreadBase):
    """ thread which can auto run ptree case one by one """
    def __init__(self, uart_handle):
        SysappWorkThreadBase.__init__(self)
        self.uart_handle = uart_handle
        self.caselist_path = (f"{platform.PLATFORM_LOCAL_MOUNT_PATH}/out/caselist.txt")
        cmd = ("if [ -d /customer/ptree/preload ]; then find /customer/ptree/preload"
                " -name \"*.json\"; fi > /mnt/out/caselist.txt")
        self.uart_handle.write(cmd)

    def dealwith_threadloop_job_first(self, casename, loopcnt):
        """ dealwith_threadloop_job_first """
        logger.warning(f"we will run {casename} lopcnt:${loopcnt}")
        case_single_name = os.path.basename(casename).split(".")[0]
        cmd = "sed -i '/\"APP_0_0\": {/,/}/ s/\"NAME\": \".*\"/\"NAME\": \""
        cmd = cmd +  f"{case_single_name}" + "\"/' /misc/earlyinit_setting.json"
        time.sleep(1)
        logger.warning(f"run {cmd}")
        self.uart_handle.write(cmd)
        result = SysappRebootOpts.reboot_to_kernel(self.uart_handle)
        if result is not True:
            logger.warning(f"caseName[{casename}] not in kernel!")
            return 255
        logger.warning(f"[{casename}]config network")
        SysappNetOpts.setup_network(self.uart_handle)
        # step4 mount nfs
        SysappNetOpts.mount_server_path_to_board(self.uart_handle, "")
        return 0
