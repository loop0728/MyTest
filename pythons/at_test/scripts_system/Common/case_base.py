from PythonScripts.logger import logger
from PythonScripts.variables import debug_mode, chip, log_path, local_mount_path
import Common.system_common as sys_common

class CaseBase:
    """Case base class."""

    def __init__(self, case_name, case_run_cnt=1, module_path_name="./"):
        self.case_name = case_name
        self.chip = chip
        self.case_run_cnt = int(case_run_cnt)
        self.uart_log_path = log_path
        #self.module_path_name = module_path_name
        self.module_path = "/".join(module_path_name.split("/")[:-1])
        self.case_res_path = f"scripts_system/{self.module_path}/resources"
        self.local_mount_path = f"{local_mount_path}/{self.case_res_path}"

        print(f"module_path_name:{module_path_name}")
        print(f"module_path:{self.module_path}")
        print(f"local_mount_path:{self.local_mount_path}")

    def is_stress(self):
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
        if debug_mode == "MemLeak":
            result = sys_common.get_case_json_key_value(
                self.case_name, "is_support_debug_mode_memleak"
            )
            if result != "no_find_key" and int(result) == 1:
                device_handle.client_memleak_script_run("init")
        if debug_mode == "Asan":
            result = sys_common.get_case_json_key_value(
                self.case_name, "is_support_debug_mode_asan"
            )
            if result != "no_find_key" and int(result) == 1:
                device_handle.client_asan_script_run("init")

    def check_debug_mode_result(self, device_handle: object):
        ret = 0
        if debug_mode == "MemLeak":
            result = sys_common.get_case_json_key_value(
                self.case_name, "is_support_debug_mode_memleak"
            )
            if result != "no_find_key" and int(result) == 1:
                ret = device_handle.client_memleak_script_run("deinit")
        return ret

    def recovery_environment(self, device_handle: object, exception_type):
        result = 255
        if exception_type == "network_exception":
            result = sys_common.reboot_board(device_handle, "soft_reboot")

        elif exception_type == "board_system_exception":
            result = sys_common.reboot_board(device_handle, "hw_reboot")

        elif exception_type == "board_image_exception":
            result = sys_common.retry_burning_partition(device_handle)

        return result

    @logger.print_line_info
    def runcase(self) -> int:
        logger.print_error("base runcase!")
        return 0

    def runcase_help(self):
        pass