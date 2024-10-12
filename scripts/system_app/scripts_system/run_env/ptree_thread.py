""" SysappPtreeThread version 0.0.1 """
import os
import time
import threading
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
from run_env.thread_waitlock import Sysapp_ThreadWaitLock

class Sysapp_PtreeThread(threading.Thread):
    """ thread which can auto run mixer one by one """
    def __init__(self, uart_handle):
        threading.Thread.__init__(self)
        self.uart_handle = uart_handle
        self.waitlock = Sysapp_ThreadWaitLock("waitlock")
        self.selfwaitlock = Sysapp_ThreadWaitLock("selfwaitlock")
        self.cleaned_lines = []
        self.current_casename = ""
        """ /stream/IT/I6DW/ and pipeline_iford need platform cover,
            iford_systemapp_interrupt_testcase need param to this
        """
        self.caselist_path = ("/stream/IT/I6DW/iford_systemapp_interrupt_testcase/"
                              "out/caselist.txt")
        cmd = ("if [ -d /customer/ptree/preload ]; then find /customer/ptree/preload"
                " -name \"*.json\"; fi "
               "> /mnt/out/caselist.txt")
        self.uart_handle.write(cmd)
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
        casecnttotal = len(self.cleaned_lines) + 1
        casecnt = casecnttotal
        while casecnt >= 0:
            self.poll_waitlock()
            if casecnt != casecnttotal:
                casename = self.get_current_casename()
                runcmd = cmd + " " + casename
                telnet1_handle.write(runcmd)
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

    def dealwith_threadloop_job_first(self, uart_handle, casename, isfirstloop):
        """ dealwith_threadloop_job_first """
        subpath = "iford_systemapp_interrupt_testcase"
        if isfirstloop is False:
            logger.print_warning(f"[{casename}]config network")
            #sys_common.check_insmod_ko(self.uart_handle, "sstar_emac")
            #sys_common.set_board_kernel_ip(self.uart_handle)
            SysappNetOpts.setup_network(self.uart_handle)
            # step4 mount nfs
            logger.print_warning(f"mount[{subpath}]")
            #sys_common.mount_to_server(self.uart_handle, f"{subpath}")
            SysappNetOpts.mount_server_path_to_board(self.uart_handle, f"{subpath}")
        logger.print_warning(f"we will run {casename}")
        case_single_name = os.path.basename(casename).split(".")[0]
        cmd = "sed -i '/\"APP_0_0\": {/,/}/ s/\"NAME\": \".*\"/\"NAME\": \""
        cmd = cmd +  f"{case_single_name}" + "\"/' /misc/earlyinit_setting.json"
        time.sleep(1)
        logger.print_warning(f"run {cmd}")
        uart_handle.write(cmd)
        #sys_common.reboot_board(self.uart_handle, "soft_reboot")
        SysappRebootOpts.reboot_to_kernel(self.uart_handle)

    def dealwith_threadloop_job_end(self, uart_handle, casename, islastloop):
        """ dealwith_threadloop_job_end """
        pass

    def run(self):
        """ run """
        cnt = 0
        for casename in self.cleaned_lines:
            self.current_casename = os.path.basename(f"{casename}")
            self.selfwaitlock.lock()
            self.dealwith_threadloop_job_first(self.uart_handle, casename,
                    cnt == 0)
            for i in range(1, 15):
                logger.print_warning(f"cnt={i}")
                time.sleep(1)
            self.waitlock.release()
            self.__poll_selfwaitlock()
            self.waitlock.lock()
            self.dealwith_threadloop_job_end(self.uart_handle, casename,
                    cnt == (len(self.cleaned_lines) - 1))
            time.sleep(5)
