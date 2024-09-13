import sys
import time
import re
import os
import json
from PythonScripts.logger import logger
from PythonScripts.variables import debug_mode, chip, log_path
import Common.system_common as sys_common

class CaseBase():

    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        self.case_name                 = case_name
        self.chip                      = chip
        self.case_run_cnt              = int(case_run_cnt)
        self.uart_log_path             = log_path
        self.module_path_name          = module_path_name
        self.module_path               = "/".join(self.module_path_name.split("/")[:-1])
        self.config_name_path          = ''
        self.mount_path                = f"scripts_system/Suite/AOV/{self.case_name}/resources"

        if self.case_name[len(self.case_name)-1:].isdigit() and '_stress_' in self.case_name:
            parase_list = self.case_name.split('_stress_')
            if len(parase_list) != 2:
                return 255
            self.case_run_cnt = int(parase_list[1])
            self.case_name = parase_list[0]
        self.error_code_dict = {
                                0:"pass", 1:"fail", 2: "reboot_dev_fail", \
                                3: "burning_fail",4:"unknow error",5:"network_exception",\
                                6:"board_system_exception",7:"board_image_exception"
                               }

    def is_stress(self):
        is_stress = False
        if self.case_name[len(self.case_name)-1:].isdigit() and '_stress_' in self.case_name:
          parase_list = self.case_name.split('_stress_')
          if len(parase_list) != 2:
              return 255
          self.case_run_cnt = int(parase_list[1])
          self.case_name = parase_list[0]
          is_stress = True
        return is_stress

    def get_cfg_file(self):
        self.config_name_path = self.module_path  + '/' + chip + '_' + self.case_name + "_config.json"
        return self.config_name_path

    def get_case_json_key_value(self, key_str, json_file_path = ''):
        result = 'no_find_key'
        if json_file_path == '':
            json_file_path = self.config_name_path
        json_content_dict = sys_common.get_json_content(json_file_path)
        if json_content_dict is not None:
           if self.case_name in json_content_dict:
                if key_str in json_content_dict[self.case_name]:
                    result = json_content_dict[self.case_name].get(key_str, "no_find_key")
                    #logger.print_warning("{}:{}".format(key_str,result))
           else:
               logger.print_warning("no find {} key, will use default value".format(key_str))
               #logger.print_warning("json_content_dict:{} ".format(json_content_dict[self.case_name][key_str]))
        return result

    def case_is_support(self):
        config_name = self.get_cfg_file()
        if not os.path.exists(config_name):
            return True
        result = int(self.get_case_json_key_value("is_support_run"))
        if self.get_debug_mode() == "MemLeak":
            result |= int(self.get_case_json_key_value("is_support_debug_mode_memleak"))
        elif self.get_debug_mode() == "Asan":
            result |= int(self.get_case_json_key_value("is_support_debug_mode_asan"))

        if not result:
            return False
        return True

    def cfg_param_parse(self):
        pass
        return 0

    def get_debug_mode(self):
        return debug_mode

    def debug_mode_script_run(self, device_handle:object):
        if self.get_debug_mode() == "MemLeak":
            result = self.get_case_json_key_value("is_support_debug_mode_memleak")
            if result != 'no_find_key' and int(result) == 1:
               device_handle.client_memleak_script_run('init')
        if self.get_debug_mode() == "Asan":
            result = self.get_case_json_key_value("is_support_debug_mode_asan")
            if result != 'no_find_key' and int(result) == 1:
               device_handle.client_asan_script_run('init')

    def debug_mode_script_end(self, device_handle:object):
        ret = 0
        if self.get_debug_mode() == "MemLeak":
            result = self.get_case_json_key_value("is_support_debug_mode_memleak")
            if result != 'no_find_key' and int(result) == 1:
               ret = device_handle.client_memleak_script_run('deinit')
        return ret

    def exception_handling(self,device_handle:object, exception_type):
        result = 255
        if exception_type == 'network_exception':
           result = sys_common.reboot_board(device_handle,'soft_reboot')

        elif exception_type == 'board_system_exception':
           result = sys_common.reboot_board(device_handle,'hw_reboot')

        elif exception_type == 'board_image_exception':
           result = sys_common.retry_burning_partition(device_handle)

        return result

    @logger.print_line_info
    def runcase(self) -> int:
        logger.print_error("base runcase!")
        return 0

    def runcase_help(self):
        pass