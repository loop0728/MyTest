import time
import re
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common
import PythonScripts.variables as platform
import subprocess


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
        self.reboot_timeout            = 30
        self.max_read_lines            = 10240
        self.package_type              = package_type.PACKAGE_TYPE_MAX
        self.base_voltage              = 900    # get from hw & IPL macro define(IDAC_BASE_VOLT)
        self.overdrive_vcore_list      = []     # for ipl core_power check 
        self.overdrive_vcpu_list       = []     # for ipl cpu_power check
        self.overdrive_cpufreq_list    = []     # for kernel cpufreq check
        self.cpufreq_vcore_list        = []     # for kernel core_power check
        self.cpufreq_vcpu_list         = []     # for kernel cpu_power check

        self.kernel_prompt             = '/ #'
        self.subpath                   = "idac/resources"
        self.dtc_tool                  = "dtc"
        self.cmd_uboot_reset           = "reset"


        """ case internal params end """


    """ case internal functions start """
    # check current status of the dev, ensure enter into kernel
    @logger.print_line_info
    def check_kernel_env(self):
        trywait_time = 0
        result = 255
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
            logger.print_error("dev enter to kernel fail")
            return result

        if self.borad_cur_state == 'at uboot':
            self.uart.clear_borad_cur_state()
            self.uart.write(self.cmd_uboot_reset)
            logger.print_info("borad_cur_state:%s , do reset" % self.borad_cur_state)

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
                    logger.print_error("dev reset to kernel timeout")
                    break
        return result

    # get dev package type
    @logger.print_line_info
    def get_package_type(self):
        result = 255
        result, str_regVal = sys_common.read_register(self.uart, "101e", "48")
        if result == 0:
            bit4 = sys_common.get_bit_value(str_regVal, 4)
            bit5 = sys_common.get_bit_value(str_regVal, 5)
            if bit4 == 0 and bit5 == 0:
                return package_type.PACKAGE_TYPE_QFN128
            elif bit4 == 0 and bit5 == 1:
                return package_type.PACKAGE_TYPE_BGA12
            else:
                return package_type.PACKAGE_TYPE_BGA11
        else:
            return package_type.PACKAGE_TYPE_MAX

    def _calc_volt_offset(self, str_hex):
        value = 0
        sign = 1
        unit = 10
        offset = 0
        bit0 = sys_common.get_bit_value(str_hex, 0)
        bit1 = sys_common.get_bit_value(str_hex, 1)
        bit2 = sys_common.get_bit_value(str_hex, 2)
        bit3 = sys_common.get_bit_value(str_hex, 3)
        bit4 = sys_common.get_bit_value(str_hex, 4)
        bit5 = sys_common.get_bit_value(str_hex, 5)
        value = bit3 << 3 + bit2 << 2 + bit1 << 1 + bit0
        if bit4 == 0:
            sign = -1
        else:
            sign = 1
        if bit5 == 0:
            unit = 20
        else:
            unit = 10
        offset = value * sign * unit
        return offset

    # get core_power offset
    def get_vcore_offset(self):
        offset = 0
        result = 255
        result,str_regVal = sys_common.read_register(self.uart, "14", "71")
        if result == 0:
            offset = self._calc_volt_offset(str_regVal)
        else:
            logger.print_error("get core_power offset fail!")
        return offset

    # get cpu_power offseet
    def get_vcpu_offset(self):
        offset = 0
        result = 255
        result,str_regVal = sys_common.read_register(self.uart, "15", "11")
        if result == 0:
            offset = self._calc_volt_offset(str_regVal)
        else:
            logger.print_error("get cpu_power offset fail!")
        return offset

    # get the min/max volt under the specified overdrive
    def _get_ipl_overdrive_voltage_map(self, package, overdrive, table):
        minVolt = maxVolt = 0
        curFreq = iford_ipl_overdrive_cpufreq_map[overdrive]
        for overdrive_volt_map in table[package][overdrive]:
            if curFreq == overdrive_volt_map[0]:
                maxVolt = overdrive_volt_map[1]
                minVolt = overdrive_volt_map[2]
                break
        return minVolt, maxVolt
    
    # get ipl core_power/cpu_power check list
    def get_ipl_volt_check_list(self, package):
        for overdrive in overdrive_type[:(len(overdrive_type) - 1)]:
            minVolt, maxVolt = self._get_ipl_overdrive_voltage_map(package, overdrive, iford_idac_volt_core_table)
            volt_map = [minVolt, maxVolt]
            self.overdrive_vcore_list.append(volt_map)
            minVolt, maxVolt = self._get_ipl_overdrive_voltage_map(package, overdrive, iford_idac_volt_cpu_table)
            volt_map = [minVolt, maxVolt]
            self.overdrive_vcpu_list.append(volt_map)

    # get the supported cpufreq list under the specified overdrive
    def _get_kernel_overdrive_cpufreq_map(self, package, overdrive):
        cpufreq_map = []
        for overdrive_vcpu_map in iford_idac_volt_cpu_table[package][overdrive]:
            cpufreq_map.append(overdrive_vcpu_map[0])
        return cpufreq_map

    # get cpufreq support list
    def get_kernel_cpufreq_list(self, package):
        for overdrive in overdrive_type[:(len(overdrive_type) - 1)]:
            cpufreq_map = self._get_kernel_overdrive_cpufreq_map(package, iford_idac_volt_cpu_table)
            self.overdrive_cpufreq_list.append(cpufreq_map)

    # get the min/max volt under the specified cpufreq
    def get_kernel_cpufreq_voltage_map(self, package):
        self.cpufreq_vcore_list = iford_idac_volt_core_table[package]
        self.cpufreq_vcpu_list = iford_idac_volt_cpu_table[package]

    def _check_emac_ko_insmod_status(self):
        result = 255
        net_interface = "eth0"
        cmd_check_insmod_status = f"ifconfig -a | grep {net_interface}"
        self.uart.write(cmd_check_insmod_status)
        status,line = self.uart.read()
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if net_interface in line:
                logger.print_info("ko has insmoded already")
                result = 0
        else:
            logger.print_error("read line fail")
            result = 255
        return result

    def _insmod_emac_ko(self, koname):
        result = 255
        cmd_insmod_emac_ko = f"insmod /config/modules/5.10/{koname}.ko"
        self.uart.write(cmd_insmod_emac_ko)
        result = self._check_emac_ko_insmod_status()
        if result != 0:
            logger.print_error(f"insmod {koname} fail")
        return result

    # check insmod emac ko, set board ip, mount server path to board
    def mount_server_path(self, path):
        result = 255
        result = self._check_emac_ko_insmod_status()
        if result != 0:
            result = self._insmod_emac_ko("sstar_emac")
            if result != 0:
                return result
        sys_common.set_board_kernel_ip(self.uart)
        status = sys_common.mount_to_server(self.uart, path)
        if status == False:
            logger.print_error(f"mount {path} fail")
            result = 255
        return result

    def _dump_devicetree(self):
        result = 255
        mount_path = f"{platform.mount_path}/{self.subpath}"
        cmd_dump_devicetree = f"cp /sys/firmware/devicetree/base {mount_path} -r"
        #cmd_dump_devicetree = f"cp /sys/firmware/fdt {mount_path}"
        self.uart.write(cmd_dump_devicetree)
        status,line = self.uart.read(60)
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if self.kernel_prompt in line:
                logger.print_info("dump devicetree ok")
                result = 0
        else:
            logger.print_error(f"dump devicetree fail")
            result = 255
            return result

    def _convert_devicetree_to_dts(self):
        result = 255
        dts_filename = f"fdt.dts"
        tool = f'./{self.dtc_tool}'
        command = [tool, '-I', 'fs', '-O', 'dts', 'base', '-o', dts_filename]
        #command = [tool, '-I', 'dtb', '-O', 'dts', 'fdt', '-o', dts_filename]
        ret = subprocess.run(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.print_info(f"Command output: {ret.stdout}")
        logger.print_info(f"stderr: {ret.stderr}")
        if ret.returncode == 0:
            logger.print_info(f"convert dts ok")
            result = 0
        else:
            logger.print_error(f"convert dts fail, errorcode: {ret.returncode}")
            result = 255
        return result

    def get_base_volt_from_dts(self):
        result = 255
        

    def get_opp_table_from_dts(self):
        result = 255

    # dump idac info from devicetree
    def get_kernel_idac_info(self):
        result = 255
        result = self._dump_devicetree()
        if result != 0:
            return result
        
        result = self._convert_devicetree_to_dts()
        if result != 0:
            return result
        


        


        

    # run idac test flow
    @logger.print_line_info
    def idac_test(self):
        result = 255

        # 1. 判断当前设备状态，确保进入kernel
        result = self.check_kernel_env()
        if result != 0:
            return result

        # 2. 获取封装类型，确定使用的cpu的overdrive-电压映射表，频率-电压映射表；执行mount操作
        self.package_type = self.get_package_type()
        logger.print_warning(f"dev package type is {self.package_type.name}")
        if self.package_type == package_type.PACKAGE_TYPE_MAX:
            logger.print_error("Unknown package type!")
            result = 255
            return result
        
        self.get_ipl_volt_check_list(self.package_type)
        self.get_kernel_cpufreq_list(self.package_type)
        self.get_kernel_cpufreq_voltage_map(self.package_type)

        result = self.mount_server_path(self.subpath)
        if result != 0:
            return result
        
        # 3. dump devicetree, 转换成dts，解析base voltage，opp_table信息，保存到case 本地。若解析失败，case结束返回失败。







        
        

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
        result = self.idac_test()
        """ case body end """

        return result

    @logger.print_line_info
    def system_help(args):
        logger.print_warning("check idac voltage ctrl")
        logger.print_warning("cmd: idac")

