""" SysappMixerThread version 0.0.1 """
import time
import sysapp_platform as platform
from suite.common.sysapp_common_logger import logger
from run_env.workthread_base import SysappWorkThreadBase

class SysappMixerThread(SysappWorkThreadBase):
    """ thread which can auto run mixer one by one """
    def __init__(self, telnet_handle):
        SysappWorkThreadBase.__init__(self)
        self.telnet_handle = telnet_handle
        self.caselist_path = (f"{platform.PLATFORM_LOCAL_MOUNT_PATH}"
                              "/out/caselist.txt")
        cmd = ("find /mnt/scripts/pipeline_iford/ -path */external "
               "-prune -o  -name \"*.json\" -not -path \"*dualos*\" -not"
               " -name \"*earlyinit*\" -print "
               "> /mnt/out/caselist.txt")
        self.telnet_handle.write(cmd)

    def dealwith_threadloop_job_first(self, casename, loopcnt):
        """ dealwith_threadloop_job_first """
        logger.warning(f"we will run {casename}{loopcnt}")
        cmd = f"cd /mnt/scripts/pipeline_iford; ./preview -r {casename}"
        time.sleep(1)
        logger.warning(f"run {cmd}")
        self.telnet_handle.write(cmd)
        return 0

    def dealwith_threadloop_job_end(self, casename, loopcnt):
        """ dealwith_threadloop_job_end """
        logger.warning(f"q case:{casename}{loopcnt}")
        cmd = "q"
        self.telnet_handle.write(cmd)
