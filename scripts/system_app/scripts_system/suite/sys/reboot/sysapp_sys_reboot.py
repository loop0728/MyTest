#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""reboot test scenarios"""
import os
import json
from enum import Enum
from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_error_codes import ErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts


class SysappCheckResultWay(Enum):
    """Class constructor.
        Args:
          Enum
    """
    E_CHECK_KEY_WORD   = 1 #check uart or kmsg log keyword num
    E_CHECK_PING  = 2 #check board network is ok
    E_CHECK_UART  = 3 #check board uart status is ok
    E_CHECK_KMSG_KEY_WORD = 4 ##check kmsg log keyword num
    E_CHECK_ALL = 255


class SysappSysRebootCase(CaseBase):
    """A class representing  reboot pipe options
    Attributes:
        None
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name
            case_run_cnt (int): the number of times the test case runs
            module_path_name (str): moudle path
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.reboot_way = "None"
        self.check_result_way = SysappCheckResultWay.E_CHECK_KEY_WORD
        self.b_fail_return = True
        self.check_keyword_list = ""
        self.goto_uboot_way = "kernel_goto_uboot"

    @staticmethod
    def write_return_ret(device_handle, cmd, line=1, max_line=10):
        """
        pass

        Args:
            pass (str): pass

        Returns:
            bool: result
        """
        logger.warning(f"cmd:{cmd}")
        device_handle.write(cmd)
        device_handle.write("echo $?")
        try_cnt = 0
        while True:
            try_cnt += 1
            ret, data = device_handle.read(line)
            if bool(ret) and data is not None and data.strip().isdigit():
                print(f"ret: {ret} value:{data}")
                break
            if try_cnt > max_line:
                logger.error("no found return value!")
                ret = False
                break
        return ret, data

    def get_keyword_json_content(self):
        """get keyword json data
        Args:
            None:
        Returns:
            None
        """
        keyword_cfg = "./cases/platform/sys/reboot/reboot_keyword.json"
        if os.path.exists(keyword_cfg):
            with open(keyword_cfg, "r") as file_fd:
                data = file_fd.read()
                self.check_keyword_list = json.loads(data)
        else:
            logger.error(f"{keyword_cfg} no exist\n")

    def sum_keyword(self, curline, check_log_type="uart.log") ->dict:
        """
        sum keyword

        Args:
            curline:curline str
            check_log_type:check log type, uart/kmsg log
        Returns:
            dict: result
        """
        keyword_record_dict = {}
        for item in self.check_keyword_list:
            if item["enable_check"] and item["check_file"] != '' \
                 and item["keyword"] in curline:
                for index, value in enumerate(item["check_file"].split()):
                    if value != check_log_type or index < 0:
                        continue
                    key = keyword_record_dict.get(item["keyword"])
                    if key is None:
                        keyword_record_dict.setdefault(item["keyword"],1)
                    else:
                        keyword_record_dict[item["keyword"]] = \
                                keyword_record_dict[item["keyword"]] + 1
        return keyword_record_dict

    def compare_keywords(self, keyword_record_dict) ->int:
        """
        compare keyword

        Args:
            curline:curline str
            check_log_type:check log type, uart/kmsg log
        Returns:
            dict: result
        """
        result = 0
        for item in self.check_keyword_list:
            if keyword_record_dict.get(item["keyword"]) is not None \
                and item["enable_check"] and item["check_file"] != '':
                logger.warning(f'keyword: {item["keyword"]}, \
                                  num: {keyword_record_dict[item["keyword"]]}')
                if keyword_record_dict[item["keyword"]] > item["happen_base_cnt"]:
                    logger.error(f'keyword: {item["keyword"]}, num: \
                                     {keyword_record_dict[item["keyword"]]} \
                                   out of range[0~{item["happen_base_cnt"]}]')
                    if item["checked_todo"] == "cold_reboot":
                        result = SysappRebootOpts.cold_reboot_to_kernel(self.uart)
                        if not result:
                            logger.error("cold reboot fail !")
                    result = 255
        return result

    @staticmethod
    def check_board_uart_status()-> int:
        """
        check board uart status.

        Args:
            None

        Returns:
            int: result
        """
        return 0

    @staticmethod
    def check_board_ping()-> int:
        """
        check board ping status.

        Args:
            None

        Returns:
            int: result
        """
        return 0

    @staticmethod
    def check_board_log_keyword()-> int:
        """
        check board log keyword status.

        Args:
            None

        Returns:
            int: result
        """
        return 0

    @staticmethod
    def check_all_flow()-> int:
        """
        check all flow status.

        Args:
            None

        Returns:
            int: result
        """
        return 0

    def goto_check_result_mode(self) ->int:
        """goto check result mode
        Args:
            None:
        Returns:
            result(int): result value,0 or 255; 0: success, 255: fail
        """
        if self.check_result_way == SysappCheckResultWay.E_CHECK_UART:
            result = self.check_board_uart_status()
            if result != 0:
                logger.error("check_board_uart_status is fail, maybe board is abnormal!\n")
        elif self.check_result_way == SysappCheckResultWay.E_CHECK_PING:
            result = self.check_board_ping()
            if result != 0:
                logger.error("check_board_ping is fail, maybe board is abnormal!\n")
        elif self.check_result_way == SysappCheckResultWay.E_CHECK_KEY_WORD:
            self.get_keyword_json_content()
            result = self.check_board_log_keyword()
            if result != 0:
                logger.error("check_board_log_keyword is fail, maybe board is abnormal!\n")
        elif self.check_result_way == SysappCheckResultWay.E_CHECK_ALL:
            result = self.check_all_flow()
            if result != 0:
                logger.error("kernel reboot is fail, maybe board is abnormal!\n")
        else:
            logger.info("kernel reboot case is not support!\n")
        return result

    def kernel_reboot(self) ->int:
        """goto kernel reboot test mode
        Args:
            None:
        Returns:
            result(int): result value,0 or 255; 0: success, 255: fail
        """
        result = 255
        logger.warning("goto kernel_reboot !\n")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            logger.error("goto kernel is fail !\n")
            return 255
        result = self.goto_check_result_mode()
        if result == 0:
            logger.info("kernel reboot case is pass!\n")
        return result

    def uboot_reboot(self) ->int:
        """goto uboot reboot test mode
        Args:
            None:
        Returns:
            result(int): result value,0 or 255; 0: success, 255: fail
        """
        result = 255
        logger.warning("goto uboot_reboot !\n")
        if self.goto_uboot_way != "kernel_goto_uboot":
            result = SysappRebootOpts.cold_reboot_to_uboot(self.uart)
        else:
            result = SysappRebootOpts.init_uboot_env(self.uart)
            if not result and self.goto_uboot_way == "kernel_goto_uboot":
                logger.error("the device is not at kernel or at uboot")
                return result
        if result:
            result = SysappRebootOpts.reboot_to_uboot(self.uart)
        else:
            logger.error("goto uboot is fail !\n")
            return 255
        result = self.goto_check_result_mode()
        if result == 0:
            logger.info("uboot reboot case is pass!\n")
        return result

    def cold_reboot(self)->int:
        """goto cold reboot test mode
        Args:
            None:
        Returns:
            result(int): result value,0 or 255; 0: success, 255: fail
        """
        result = 255
        logger.warning("goto cold_reboot \n")
        result = SysappRebootOpts.cold_reboot_to_kernel(self.uart)
        if not result:
            logger.error("goto kernel is fail")
            return 255
        result = self.goto_check_result_mode()
        if result == 0:
            logger.info("cold reboot case is pass!\n")
        return result

    def reboot_pipe(self, run_cnt) ->int:
        """ go to run reboot case flow
        Args:
            run_cnt: run cnt
        Returns:
            result: 0:pass, 255:fail
        """
        result = 255
        if  self.reboot_way == "cold_reboot":
            result = self.cold_reboot()
        elif self.reboot_way == "uboot_reboot":
            result = self.uboot_reboot()
        elif self.reboot_way == "kernel_reboot":
            result = self.kernel_reboot()
        else:
            logger.warning(f"caseName[{self.case_name}] reboot_way[{self.reboot_way}]\
                                run_cnt[{run_cnt}] is no support !")
        return result

    def runcase(self):
        """ go to runcase flow
        Args:
            None:
        Returns:
            result(enum): result value,FAIL: success, SUCCESS: fail
        """
        result = 0
        run_cnt = 0
        all_result = 0
        error_code = ErrorCodes.FAIL
        while run_cnt < self.case_run_cnt:
            run_cnt += 1
            result = self.reboot_pipe(run_cnt)
            if result != 0:
                logger.error(f"caseName[{self.case_name}] reboot_way[{self.reboot_way}] \
                             run_cnt[{run_cnt}] is fail!")
                if not self.b_stress or self.b_fail_return:
                    self.case_run_cnt = run_cnt
                    self.uart.close()
                    return ErrorCodes.FAIL
                else:
                    all_result += result
            else:
                logger.info(f"caseName[{self.case_name}] reboot_way[{self.reboot_way}]\
                             run_cnt[{run_cnt}] is pass !")
        self.uart.close()
        if self.b_stress:
            result = all_result
        if result == 0:
            error_code = ErrorCodes.SUCCESS
        return error_code

    @staticmethod
    def runcase_help():
        """ go to runcase help
        Args:
            None:
        Returns:
            None
        """
        logger.warning("only for reboot cold_reboot kernel_reboot uboot_rest_reboot!\n")
