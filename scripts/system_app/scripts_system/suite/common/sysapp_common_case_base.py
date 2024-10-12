"""Common operations in cases"""
from sysapp_platform import PLATFORM_DEBUG_MODE, LOG_PATH, PLATFORM_LOCAL_MOUNT_PATH
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
import suite.common.sysapp_common_utils as SysappUtils

class SysappCaseBase:
    """Case base class."""

    def __init__(self, case_name, case_run_cnt=1, script_path="./", case_stage='0x1'):
        """
        Case Base param.

        Args:
            case_name (str): case name
            case_run_cnt (int): case run cnt
            script_path (str): module path
            case_stage (str): case stage
        """
        self.case_name = case_name
        self.case_run_cnt = case_run_cnt
        # self.script_path = script_path
        self.case_stage = case_stage
        self.uart_log_path = LOG_PATH
        self.module_path = "/".join(script_path.split("/")[:-1])
        self.case_res_path = f"scripts_system/{self.module_path}/resources"
        self.local_mount_path = f"{PLATFORM_LOCAL_MOUNT_PATH}/{self.case_res_path}"

    def is_stress(self):
        """
        Determine if it is stress.

        Returns:
            bool: result
        """
        is_stress = False
        if (
                self.case_name[len(self.case_name) - 1 :].isdigit()
                and "_stress_" in self.case_name
        ):
            parase_list = self.case_name.split("_stress_")
            if len(parase_list) != 2:
                return 255
            self.case_run_cnt = int(parase_list[1])
            self.case_name = parase_list[0]
            is_stress = True
        return is_stress

    def enter_debug_mode(self, device_handle: object):
        """If debug mode existed, run corresponding events."""
        if PLATFORM_DEBUG_MODE == "MemLeak":
            result = SysappUtils.get_case_json_key_value(
                self.case_name, "is_support_debug_mode_memleak"
            )
            if result != "no_find_key" and int(result) == 1:
                device_handle.client_memleak_script_run("init")
        if PLATFORM_DEBUG_MODE == "Asan":
            result = SysappUtils.get_case_json_key_value(
                self.case_name, "is_support_debug_mode_asan"
            )
            if result != "no_find_key" and int(result) == 1:
                device_handle.client_asan_script_run("init")

    def check_debug_mode_result(self, device_handle: object):
        """If debug mode existed, run corresponding events."""
        ret = 0
        if PLATFORM_DEBUG_MODE == "MemLeak":
            result = SysappUtils.get_case_json_key_value(
                self.case_name, "is_support_debug_mode_memleak"
            )
            if result != "no_find_key" and int(result) == 1:
                ret = device_handle.client_memleak_script_run("deinit")
        return ret

    @staticmethod
    def recovery_environment(device_handle: object, exception_type):
        """Run case end, recovery environment."""
        result = 255
        if exception_type == "network_exception":
            result = SysappRebootOpts.reboot_to_kernel(device_handle)

        elif exception_type == "board_system_exception":
            result = SysappRebootOpts.cold_reboot_to_kernel(device_handle)

        return result

    @sysapp_print.print_line_info
    def runcase(self) -> int:
        """Run case entry."""
        logger.error("base runcase!")
        logger.info(f"case stage {self.case_stage}")
        return 0

    def runcase_help(self):
        """Run case help info entry."""
        logger.info(f"case stage {self.case_stage}")
