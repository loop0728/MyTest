"""OS Switch case."""
import time
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_error_codes import SysappErrorCodes
import suite.common.sysapp_common_utils as sys_common_utils
from sysapp_client import SysappClient


class SysappAovOsSwitch(SysappCaseBase):
    """OS Switch case."""

    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """
        API test Case.

        Args:
            case_name: case name
            case_run_cnt: case run cnt
            script_path: script_path
            case_stage: case stage
        """
        super().__init__(case_name, case_run_cnt, script_path)
        self.uart = SysappClient(self.case_name, "uart", "uart")

    def get_current_os(self):
        """
        Get current OS.

        Returns:
            str: current OS
        """
        result = ""
        cmd = "lsmod | grep mi_sys | wc -l"
        # check uart
        res = self.uart.write(cmd)
        if res is False:
            logger.error(f"{self.uart} is disconnected.")
            return "Unknown"
        wait_keyword = "0"
        status, data = self.uart.read()
        if status is True:
            if wait_keyword in data:
                result = "dualos"
                return result
            else:
                result = "purelinux"
                return result
        else:
            result = "Unknown"
            return result

    def switch_os(self, target_os):
        """
        Switch OS.

        Args:
            target_os (str): target OS

        Returns:
            int: result
        """
        result = 0
        cur_os = self.get_current_os()
        if cur_os == target_os:
            logger.warning(f"[{self.case_name}] current os is match {target_os}")
            return 0

        logger.warning(f"will switch to OS({target_os})!")
        if target_os == "dualos":
            cmd = "cd /customer/sample_code/bin/"
            self.uart.write(cmd)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = self.uart.read()
            if status is True:
                if wait_keyword not in data:
                    return 255
            else:
                logger.error(f"Read fail,no keyword: {wait_keyword}")
                return 255
            cmd = "./prog_aov_aov_demo -t"
            self.uart.write(cmd)
            time.sleep(10)
            cmd = "c"
            self.uart.write(cmd)

        if target_os == "purelinux":
            cmd = "cd /customer/sample_code/bin/"
            self.uart.write(cmd)
            time.sleep(1)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = self.uart.read()
            if status is True:
                if wait_keyword not in data:
                    result = 255
                    return result

            cmd = "./prog_preload_linux -t"
            wait_keyword = "press c to change mode"
            result, data = sys_common_utils.write_and_match_keyword(
                self.uart, cmd, wait_keyword
            )
            if result is False:
                return 255

            cmd = "c"
            self.uart.write(cmd)

        time.sleep(20)
        return result

    def os_switch_test(self):
        """
        Run os switch test flow.

        Args:
            None:

        Returns:
            int: result
        """
        result = 0
        # step1 go to kernel
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if result is not True:
            logger.warning(f"caseName[{self.case_name}] not in kernel!")
            return 255
        # step2 switch to dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.warning(f"caseName[{self.case_name}] run done!")
            return 255
        # step3 switch to purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.warning(f"caseName[{self.case_name}] run done!")
            return 255
        return 0

    def runcase(self):
        """
        Run case entry.

        Returns:
            SysappErrorCodes: Error code
        """
        error_code = SysappErrorCodes.FAIL
        result = self.os_switch_test()
        print(f"result:{result} <-----------")
        if result == 0:
            error_code =  SysappErrorCodes.SUCCESS

        return error_code
