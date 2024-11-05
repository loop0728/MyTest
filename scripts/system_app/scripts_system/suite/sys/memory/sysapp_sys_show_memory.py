""" show_memory case version 0.0.1 """
import time
import sysapp_platform as platform
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.sys.aov.common.sysapp_aov_common import SysappAovCommon
from run_env.mixer_thread import SysappMixerThread as MixerThread
from run_env.ptree_thread import SysappPtreeThread as PtreeThread
from sysapp_client import SysappClient as Client

class SysappSysShowMemory(CaseBase):
    """ show_memory main thread """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        index = case_name.find('_')
        if index != -1:
            casename = case_name[:index]
            self.target_os = case_name[index+1:]
        else:
            casename = case_name
            self.target_os = "purelinux"
        super().__init__(casename, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def check_currentos(self, target_os):
        """ check_currentos """
        if target_os == "dualos" or target_os == "purelinux":
            result = SysappAovCommon.switch_os_common(self.uart, target_os)
            if result == 255:
                logger.warning(f"fail to switch {target_os}"
                                " caseName[{self.case_name}] run done!")
                return 255
        else:
            logger.warning(f"unkown target:{target_os} !!!")
        return 0

    def runcase(self):
        """ runcase """
        # step1 判断是否在kernel下
        logger.warning(f"caseName[{self.case_name}] target_os[{self.target_os}]")
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if result is not True:
            logger.warning(f"caseName[{self.case_name}] not in kernel!")
            return 255
        # step2 切换到dualos/purelinux
        self.check_currentos(self.target_os)
        # step3 挂载网络
        logger.warning("config network")
        SysappNetOpts.setup_network(self.uart)
        # step4 mount nfs
        logger.warning(f"mount[{platform.PLATFORM_MOUNT_PATH}]")
        SysappNetOpts.mount_server_path_to_board(self.uart, "")
        # step5 串口运行mixer pipeline
        if self.target_os != "dualos":
            logger.warning("run mixer case")
            telnetmixer = Client(self.case_name, "telnet", "telnetmixer")
            workthread = MixerThread(telnetmixer)
        else:
            workthread = PtreeThread(self.uart)
        time.sleep(3)
        casecnt = workthread.solve_caselist_by_stage(self.case_stage)
        time.sleep(3)
        if casecnt == 0:
            logger.warning("workthread case error!")
            return -1
        workthread.start()
        # step6 telnet cd 到mount目录，并运行show_interrupts.sh脚本
        logger.warning("connect telent && run case")
        telnet0 = Client(self.case_name, "telnet", "telnet0")
        device_handle = self.uart
        cmd = ("cd /mnt/scripts_system/suite/sys/memory/resource/;"
               "./show_memory.sh ")
        if self.target_os != "dualos":
            time.sleep(2)
            cmd = cmd + "purelinux"
            device_handle = telnet0
        else:
            cmd = cmd + "dualos"
        workthread.loop_run_command_sync(device_handle, cmd)
        time.sleep(3)
        # step7 从mount 目录将原始数据和最终结果保存至指定目录，为了后续自动化展示结果
        logger.warning("handle result")
        telnet0.close()
        self.uart.close()
        # step8 切换到purelinux
        result = self.check_currentos("purelinux")
        return result
