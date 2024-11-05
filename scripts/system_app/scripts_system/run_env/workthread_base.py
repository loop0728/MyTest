""" SysappWorkThreadBase version 0.0.1 """
import os
import time
import threading
from suite.common.sysapp_common_logger import logger
from run_env.thread_waitlock import SysappThreadWaitLock
from cases.platform.casemaper_platform import SysappCaseMaperPlatform

class SysappWorkThreadBase(threading.Thread):
    """ thread which can auto run sync thread case one by one """
    def __init__(self):
        threading.Thread.__init__(self)
        self.waitlock = SysappThreadWaitLock("waitlock")
        self.selfwaitlock = SysappThreadWaitLock("selfwaitlock")
        self.waitlock.lock()
        self.selfwaitlock.release()
        self.current_casename = ""
        self.cleaned_lines = []
        self.caselist_path = ""

    def __pollwaitlock(self, lock):
        """ __pollwaitlock """
        if lock.poll_waitlock_timeout(50) is False:
            logger.warning(f"case:{self.current_casename} poll"
                            " not return!")

    def __poll_selfwaitlock(self):
        """ __poll_selfwaitlock """
        self.__pollwaitlock(self.selfwaitlock)

    def poll_waitlock(self):
        """ poll_waitlock """
        self.__pollwaitlock(self.waitlock)

    def release_waitlock(self):
        """ release_waitlock """
        self.selfwaitlock.release()

    def get_current_casename(self):
        """ get_current_casename """
        return self.current_casename

    def solve_caselist(self):
        """ solve_caselist """
        return self.solve_caselist_by_stage(0xff)

    def solve_caselist_by_stage(self, stage):
        """
        read castlist.txt, record every case to list, return list length
        """
        try:
            with open(self.caselist_path, "r") as file:
                lines = file.readlines()
                tmplines = [line.strip() for line in lines]
                if stage == 0xff:
                    self.cleaned_lines = tmplines
                else:
                    casemaper = SysappCaseMaperPlatform()
                    stagesupportcases = casemaper.get_cases_from_stage(stage)
                    self.cleaned_lines = casemaper.find_matching_files(tmplines, stagesupportcases)
                logger.warning(f"total case:{self.cleaned_lines}")
                return len(self.cleaned_lines)
        except FileNotFoundError:
            logger.warning(f"file:{self.caselist_path} not exist!")
            return 0
        except Exception as exce:
            logger.warning(f"something error:{exce}")
            return 0

    def loop_run_command_sync(self, device_handle, cmd):
        """
        loop_run_command_sync
        device_handle (obj):   uart handle or
                               must be diff from self.telnet_handle
        cmd (str):              shell cmd

        """
        if device_handle is None:
            logger.warning("device_handle is null !")
            return -1
        if cmd == "":
            logger.warning("cmd is empty !")
            return -1
        casecnt = len(self.cleaned_lines)
        while casecnt >= 0:
            self.poll_waitlock()
            casename = self.get_current_casename()
            logger.warning(f"casename:{casename} !")
            runcmd = cmd + " " + casename
            logger.warning(f"runcmd:{runcmd} !")
            device_handle.write(runcmd)
            loopcnt = 0
            while loopcnt <= 30:
                time.sleep(1)
                # readresult, data = telnet0.read()
                loopcnt += 1
                # print(f"telnet read data:{data}")
            logger.warning(f"read {casename} result")
            casecnt -= 1
            self.release_waitlock()
            time.sleep(1)
        self.join()

    def dealwith_threadloop_job_first(self, casename, loopcnt):
        """
        dealwith_threadloop_job_first
        return 0 if success
        """
        pass
        return 0

    def dealwith_threadloop_job_end(self, casename, loopcnt):
        """ dealwith_threadloop_job_end """
        pass

    def run(self):
        """ run """
        cnt = 0
        for casename in self.cleaned_lines:
            self.current_casename = os.path.basename(f"{casename}")
            self.selfwaitlock.lock()
            result = self.dealwith_threadloop_job_first(casename, cnt)
            if result != 255:
                for i in range(1, 15):
                    logger.warning(f"cnt={i}")
                    time.sleep(1)
            self.waitlock.release()
            self.__poll_selfwaitlock()
            self.waitlock.lock()
            self.dealwith_threadloop_job_end(casename, cnt)
            time.sleep(5)
