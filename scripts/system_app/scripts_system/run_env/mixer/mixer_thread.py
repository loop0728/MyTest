""" SysappMixerThread version 0.0.1 """
import os
import time
import threading
from suite.common.sysapp_common_logger import logger
from run_env.mixer.thread_waitlock import ThreadWaitLock

class SysappMixerThread(threading.Thread):
    """ thread which can auto run mixer one by one """
    def __init__(self, telnet_handle):
        threading.Thread.__init__(self)
        self.telnet_handle = telnet_handle
        self.waitlock = ThreadWaitLock("waitlock")
        self.selfwaitlock = ThreadWaitLock("selfwaitlock")
        self.cleaned_lines = []
        self.current_casename = ""
        """ /stream/IT/I6DW/ and pipeline_iford need platform cover,
            iford_systemapp_interrupt_testcase need param to this
        """
        self.caselist_path = ("/stream/IT/I6DW/iford_systemapp_interrupt_testcase/"
                              "out/Interrupts/caselist.txt")
        cmd = ("find /mnt/scripts/pipeline_iford/ -path */external "
               "-prune -o  -name \"*.json\" -not -path \"*dualos*\" -not"
               " -name \"*earlyinit*\" -print "
               "> /mnt/out/Interrupts/caselist.txt")
        self.telnet_handle.write(cmd)
        self.waitlock.lock()
        self.selfwaitlock.release()



    def __pollwaitlock(self, lock):
        """ __pollwaitlock """
        if lock.poll_waitlock_timeout(50) is False:
            logger.print_warning(f"case:{self.current_casename} poll"
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

    def solve_caselist(self):
        """
        read castlist.txt, record every case to list, return list length
        """
        try:
            with open(self.caselist_path, "r") as file:
                lines = file.readlines()
                self.cleaned_lines = [line.strip() for line in lines]
                return len(self.cleaned_lines)
        except FileNotFoundError:
            logger.print_warning(f"file:{self.caselist_path} not exist!")
            return 0
        except Exception as exce:
            logger.print_warning(f"something error:{exce}")
            return 0

    def get_current_casename(self):
        """ get_current_casename """
        return self.current_casename

    def loop_run_command_sync(self, telnet1_handle, cmd):
        """
        loop_run_command_sync
        telnet1_handle (obj):   must be diff from self.telnet_handle
        cmd (str):              shell cmd

        """
        if telnet1_handle is None:
            logger.print_warning("telent1_handle is null !")
            return -1
        if cmd == "":
            logger.print_warning("cmd is empty !")
            return -1
        casecnt = len(self.cleaned_lines)
        while casecnt >= 0:
            self.poll_waitlock()
            casename = self.get_current_casename()
            telnet1_handle.write(cmd)
            loopcnt = 0
            while loopcnt <= 30:
                time.sleep(1)
                # readresult, data = telnet0.read()
                loopcnt += 1
                # print(f"telnet read data:{data}")
            logger.print_warning(f"read {casename} result")
            casecnt -= 1
            self.release_waitlock()
            time.sleep(1)
        self.join()


    def run(self):
        """ run """
        for mixercase in self.cleaned_lines:
            self.current_casename = os.path.basename(f"{mixercase}")
            self.selfwaitlock.lock()
            logger.print_warning(f"we will run {mixercase}")
            cmd = f"cd /mnt/scripts/pipeline_iford; ./preview -r {mixercase}"
            time.sleep(1)
            logger.print_warning(f"run {cmd}")
            self.telnet_handle.write(cmd)
            for i in range(1, 15):
                logger.print_warning(f"cnt={i}")
                time.sleep(1)
            self.waitlock.release()
            self.__poll_selfwaitlock()
            self.waitlock.lock()
            cmd = "q"
            self.telnet_handle.write(cmd)
            time.sleep(5)
        try:
            self.telnet_handle.close()
        except Exception as exce:
            print(f"Exception:{exce}!")
