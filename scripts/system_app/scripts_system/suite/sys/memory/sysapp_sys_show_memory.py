""" show_memory case version 0.0.1 """
import time
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
import suite.common.sysapp_common_utils as SysappUtils
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from run_env.mixer_thread import SysappMixerThread as MixerThread
from sysapp_client import SysappClient as Client

class SysappSysShowMemory(CaseBase):
    """ show_memory main thread """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.subpath = "iford_systemapp_interrupt_testcase"

    def runcase(self):
        """ runcase """
        current_os = ''
        # step1 判断是否在kernel下
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if result is not True:
            logger.warning(f"caseName[{self.case_name}] not in kernel!")
            return 255
        # step2 切换到dualos/purelinux
        current_os = SysappUtils.get_current_os(self.uart)
        if self.case_name == "show_memory_dualos" and current_os == "purelinux":
            result = SysappUtils.switch_os_aov(self.uart, "dualos")
            if result == 255:
                logger.warning(f"fail to switch dualos"
                                     " caseName[{self.case_name}] run done!")
                return 255
            time.sleep(20)
        if self.case_name == "show_memory_purelinux" and current_os == "dualos":
            result = SysappUtils.switch_os_aov(self.uart, "purelinux")
            if result == 255:
                logger.warning(f"fail to switch linux"
                                     " caseName[{self.case_name}] run done!")
                return 255
            time.sleep(20)
        # step3 挂载网络
        logger.warning("config network")
        #self.check_insmod_ko("sstar_emac")
        #sys_common.set_board_kernel_ip(self.uart)
        SysappNetOpts.setup_network(self.uart)
        # step4 mount nfs
        logger.warning(f"mount[{self.subpath}]")
        #sys_common.mount_to_server(self.uart, f"{self.subpath}")
        SysappNetOpts.mount_server_path_to_board(self.uart, f"{self.subpath}")
        # step5 串口运行mixer pipeline
        if self.case_name != "show_memory_dualos":
            logger.warning("run mixer case")
            telnetmixer = Client(self.case_name, "telnet", "telnetmixer")
            mixerthread = MixerThread(telnetmixer)
            casecnt = mixerthread.solve_caselist()
            time.sleep(3)
            if casecnt == 0:
                logger.warning("mixerthread case error!")
                return -1
            mixerthread.start()
        # step6 telnet cd 到mount目录，并运行show_interrupts.sh脚本
        logger.warning("connect telent && run case")
        telnet0 = Client(self.case_name, "telnet", "telnet0")
        time.sleep(5)
        if self.case_name != "show_memory_dualos":
            cmd = (f"cd /mnt/scripts_system/Suite/Memory/resource/;"
                   "./show_memory.sh purelinux")
            mixerthread.loop_run_command_sync(telnet0, cmd)
        else:
            cmd = (f"cd /mnt/scripts_system/Suite/Memory/resource/;"
               "./show_memory.sh purelinux {casename}")
            telnet0.write(cmd)
        loopcnt = 0
        while loopcnt <= 30:
            time.sleep(1)
            loopcnt += 1
        # step7 从mount 目录将原始数据和最终结果保存至指定目录，为了后续自动化展示结果
        logger.warning("handle result")
        telnet0.close()
        self.uart.close()
        # step8 切换到purelinux
        current_os = SysappUtils.get_current_os(self.uart)
        if current_os == "dualos":
            result = SysappUtils.switch_os_aov(self.uart, "purelinux")
        if result == 255:
            logger.warning(f"caseName[{self.case_name}] run done!")
            return 255
        return 0
