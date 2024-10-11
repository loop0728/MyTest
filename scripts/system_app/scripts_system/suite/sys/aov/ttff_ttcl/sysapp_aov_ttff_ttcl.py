"""Get AOV TTFF TTCL case."""
import re
import os
import time
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_error_codes import SysappErrorCodes
import suite.common.sysapp_common_utils as sys_common_utils
from sysapp_client import SysappClient
from cases.platform.sys.aov.ttff_ttcl_var import TTFF_TARGET, TTCL_TARGET


class SysappAovTtffTtcl(SysappCaseBase):
    """Case for get AOV TTFF TTCL."""

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

    @staticmethod
    def save_time_info(name, info):
        """
        Save time to file.

        Args:
            name (str): case name
            info (str): time info

        Returns:
            bool: result
        """
        file = None
        result = 0
        file_path = f"out/{name}/time.txt"
        try:
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(info)
        except FileNotFoundError:
            result = 255
        except PermissionError:
            result = 255
        return result

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

    def get_ttff_ttcl(self):
        """
        Get TTFF TTCL.

        Returns:
            int: result
        """
        result = 0
        ttff_time_value = 0
        ttcl_time_value = 0

        cmd = "cat /sys/class/sstar/msys/booting_time"
        wait_keyword = "VIF ch0 int 0"
        result, ret_match_buffer = sys_common_utils.write_and_match_keyword(
            self.uart, cmd, wait_keyword
        )
        if result is False:
            result = 255
            return result
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode(
                "utf-8", errors="replace"
            ).strip()
        if "diff" in ret_match_buffer and "VIF" in ret_match_buffer:
            logger.info(f"ret_match_buffer:{ret_match_buffer}")
            pattern = re.compile(r"time:\s+(\d+),.*int*")
            match = pattern.search(ret_match_buffer)
            if match:
                ttff_time_value = match.group(1)
                if ttff_time_value != "int":
                    ttff_time_value = int(ttff_time_value)
                logger.info(
                    f"TTFF Time value:{ttff_time_value}; target:{TTFF_TARGET}"
                )

        cmd = "cat /sys/class/sstar/msys/booting_time"
        wait_keyword = "ramdisk_execute_command"
        result, ret_match_buffer = sys_common_utils.write_and_match_keyword(
            self.uart, cmd, wait_keyword
        )
        if result is False:
            result = 255
            return result
        if isinstance(ret_match_buffer, bytes):
            ret_match_buffer = ret_match_buffer.decode(
                "utf-8", errors="replace"
            ).strip()
        if "diff" in ret_match_buffer and "ramdisk_execute_command" in ret_match_buffer:
            logger.info(f"ret_match_buffer:{ret_match_buffer}")
            pattern = re.compile(r"time:\s+(\d+),.*ramdisk_execute_command\+")
            match = pattern.search(ret_match_buffer)
            if match:
                ttcl_time_value = match.group(1)
                if not isinstance(ttcl_time_value, int):
                    ttcl_time_value = int(ttcl_time_value)
                logger.info(
                    f"TTCL Time value:{ttcl_time_value}; target:{TTCL_TARGET}"
                )

        time_info = (f"TTFF_TARGET:{TTFF_TARGET};TTFF:{ttff_time_value};"
                     f"TTCL_TARGET:{TTCL_TARGET};TTCL:{ttcl_time_value}")
        self.save_time_info(self.case_name, time_info)
        if ttff_time_value == 0 or ttff_time_value > TTFF_TARGET:
            logger.warning(
                f"ttff time [{ttff_time_value}] is error target[{TTFF_TARGET}]!"
            )
            result = 255
        if ttcl_time_value == 0 or ttcl_time_value > TTCL_TARGET:
            logger.warning(
                f"ttcl time [{ttcl_time_value}] is error, target[{TTCL_TARGET}]!"
            )
            result = 255

        return result

    def ttff_ttcl_test(self):
        """
        Run ttff/ttcl test flow.

        Args:
            None:

        Returns:
            int: result
        """
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if result is not True:
            logger.warning(f"caseName[{self.case_name}] not in kernel!")
            return 0
        # step2 switch to dualOS
        result = self.switch_os("dualos")
        if result == 255:
            logger.warning(f"caseName[{self.case_name}] run done!")
            return 0
        # step3 cat booting time
        result = self.get_ttff_ttcl()
        # step4 switch to purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.warning(f"caseName[{self.case_name}] run done!")
            return 0

        self.uart.close()
        return 0

    def runcase(self):
        """
        Run case entry.

        Returns:
            SysappErrorCodes: Error code
        """
        error_code = SysappErrorCodes.FAIL
        result = self.ttff_ttcl_test()
        if result == 0:
            error_code = SysappErrorCodes.SUCCESS

        return error_code
