""" show_interrupts version 0.0.1 """
import time
import threading
from python_scripts.logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.mixer_thread import MixerThread
import suite.common.sysapp_common as sys_common
from sysapp_client import SysappClient as Client

class show_interrupts(CaseBase):
    """ case main thread """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.subpath = "iford_systemapp_interrupt_testcase"

    def runcase(self):
        result = 0
        casecnt = 0
        # step1 判断是否在kernel下
        result = sys_common.goto_kernel(self.uart)
        if result is False:
            logger.print_warning(f"caseName[{self.case_name}] not in kernel!")
            return 255
        # step2 切换到purelinux
        result = sys_common.switch_os_aov(self.uart, "purelinux")
        if result == 255:
            logger.print_warning(f"caseName[{self.case_name}] run done!")
            return 255
        # step3 挂载网络
        logger.print_warning("config network")
        sys_common.check_insmod_ko(self.uart, "sstar_emac")
        sys_common.set_board_kernel_ip(self.uart)
        # step4 mount nfs
        logger.print_warning(f"mount[{self.subpath}]")
        sys_common.mount_to_server(self.uart, f"{self.subpath}")
        # step5 串口运行mixer pipeline
        logger.print_warning("run mixer case")
        telnetmixer = Client(self.case_name, "telnet", "telnetmixer")
        mixerthread = MixerThread(telnetmixer)
        time.sleep(3)
        casecnt = mixerthread.solve_caselist()
        if casecnt == 0:
            logger.print_warning("mixerthread case error!")
            return -1
        mixerthread.start()
        # step6 telnet cd 到mount目录，并运行show_interrupts.sh脚本
        logger.print_warning("connect telent && run case")
        telnet0 = Client(self.case_name, "telnet", "telnet0")
        cmd = (f"cd /mnt/scripts_system/Suite/Interrupts/resource/;"
               "./perf_interrupt.sh {casename}")
        mixerthread.loop_run_command_sync(telnet0, cmd)
        telnet0.close()
        self.uart.close()
        return 0
