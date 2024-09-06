import sys
import time
import re
import os
import json
from PythonScripts.logger import logger
import threading
import inspect
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common
import timeit

""" case import start """
from enum import Enum
from idac_var import overdrive_type, package_type, corner_ic_type, idac_power_type
from idac_var import iford_idac_volt_core_table, iford_idac_volt_cpu_table, iford_ipl_overdrive_cpufreq_map
from Common.aov_common import AOVCase
""" case import end """

class idac(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

        """ case internal params start """
        self.borad_cur_state = ''
        self.reboot_timeout            = 180
        self.max_read_lines            = 10240
        self.package_type = package_type.PACKAGE_TYPE_MAX


        self.cmd_uboot_reset           = "reset"


        """ case internal params end """


    """ case internal functions start """
    # check current status of the dev, ensure enter into kernel
    @logger.print_line_info
    def check_kernel_env(self):
        trywait_time = 0
        result = 255
        #logger.print_info("reboot dev ...")
        self.uart.write('')
        self.borad_cur_state = self.uart.get_borad_cur_state()[1]
        if self.borad_cur_state == 'Unknow':
            for i in range(1,20):
                self.uart.write('')
                self.borad_cur_state = self.uart.get_borad_cur_state()[1]
                if self.borad_cur_state != 'Unknow':
                    break
                time.sleep(1)
        if self.borad_cur_state == 'Unknow':
            logger.print_info("dev enter to kernel fail")
            return result
        if self.borad_cur_state == 'at uboot':
            self.uart.clear_borad_cur_state()
            self.uart.write(self.cmd_uboot_reset)

        while True:
            self.borad_cur_state = self.uart.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                result = 0
                logger.print_info("borad_cur_state:%s " % self.borad_cur_state)
                break
            else:
                time.sleep(1)
                trywait_time = trywait_time + 1
                if trywait_time > self.reboot_timeout:
                    break
        return result

    # get register val
    @logger.print_line_info
    def _read_register(self, bank, offset):
        result = 255
        regVal = 0
        read_line_cnt = 0
        is_register_value_ready = 0
        cmd_get_package_type = "/customer/riu_r {} {}".format(bank, offset)
        self.uart.write(cmd_get_package_type)

        while True:
            if read_line_cnt > self.max_read_lines:
                logger.print_error("read lines exceed max_read_lines:%d" %(self.max_read_lines))
                break

            status, line = self.uart.read()
            if status  == True:
                read_line_cnt += 1
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "BANK" in line:
                    is_register_value_ready = 1
                    continue

                if is_register_value_ready == 1 :
                    pattern = re.compile(r'0x([A-Fa-f0-9]{4})')
                    match = pattern.search(line)
                    if match:
                        str_regVal = match.group(1)
                        logger.print_info("kernel_resume_time is %s" %(str_regVal))
                        if str_regVal.startswith("0x"):
                            str_regVal = str_regVal[2:]
                        regVal = int(str_regVal, 16)
                        break
            else:
                logger.print_error("read line:%d fail" %(read_line_cnt))
                break
        return result, regVal

    def _get_bit_value(self, str_hex, position):
        num = int(str_hex, 16)
        bit = (num >> position) & 1
        return bit

    # get dev package type
    @logger.print_line_info
    def get_package_type(self):
        result = 255
        result, str_regVal = sys_common.read_register(self.uart, "101e", "48")
        if result == 0:
            bit4 = self._get_bit_value(str_regVal, 4)
            bit5 = self._get_bit_value(str_regVal, 5)
            if bit4 == 0 and bit5 == 0:
                return package_type.PACKAGE_TYPE_QFN128
            elif bit4 == 0 and bit5 == 1:
                return package_type.PACKAGE_TYPE_BGA12
            else:
                return package_type.PACKAGE_TYPE_BGA11
        else
            return package_type.PACKAGE_TYPE_MAX





    # run flow: highfps->lowfps->lowfps, get test cost between highfps & lowfps and between lowfps & lowfps.
    @logger.print_line_info
    def fps_switch_squence(self):
        result = 255

        # 1. 判断当前设备状态，确保进入kernel
        result = self.check_kernel_env()
        if result != 0:
            logger.print_error("idac test fail!")
        # 2. 获取封装类型，确定使用的cpu的overdrive-电压映射表，频率-电压映射表；执行mount操作





        
        

        if result == 0:
            self.enable_printk_time()                           # open kernel timestamp
            self.run_aov_demo_test()                            # run aov app in test mode
            self.redirect_kmsg()                                # redirect kmsg to memory file
            self.cat_kmsg()                                     # cat kmsg
            self.cat_booting_time()                             # cat booting time
            result = self.judge_test_result()                   # judge test result
            self.disable_printk_time()                          # close kernel timestamp
        else:
            logger.print_error("reboot timeout!")

        if result == 0:
            logger.print_warning("str test pass!")
        else:
            logger.print_error("str test fail!")

        return result

    """ case internal functions end """

    @logger.print_line_info
    def runcase(self):
        result = 255
        """ case body start """
        result = self.fps_switch_squence()
        """ case body end """

        return result

    @logger.print_line_info
    def system_help(args):
        logger.print_warning("check idac voltage ctrl")
        logger.print_warning("cmd: idac")

