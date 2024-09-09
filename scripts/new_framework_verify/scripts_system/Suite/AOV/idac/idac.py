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
from idac_var import overdrive_type, package_type, corner_ic_type, idac_power_type, dvfs_state
from idac_var import iford_idac_volt_core_table, iford_idac_volt_cpu_table, iford_ipl_overdrive_cpufreq_map, iford_idac_qfn_dvfs_vcore_table
from Common.aov_common import AOVCase
""" case import end """

class reboot_opts():
    def __init__(self, device):
        self.borad_cur_state = ''
        self.device = device
    
    def get_cur_boot_state(self):
        result = 255
        self.device.write('')
        self.borad_cur_state = self.device.get_borad_cur_state()[1]
        if self.borad_cur_state == 'Unknow':
            for i in range(1,20):
                self.device.write('')
                self.borad_cur_state = self.device.get_borad_cur_state()[1]
                if self.borad_cur_state != 'Unknow':
                    result = 0
                    break
                time.sleep(1)

        if self.borad_cur_state == 'Unknow':
            logger.print_error("dev is not at kernel or at uboot")
        return result

    def kernel_to_uboot(self):
        result = 255
        try_time = 0
        if self.borad_cur_state != 'at kernel':
            logger.print_error("dev is not at kernel now")
            return result
        
        self.device.write('reboot')
        time.sleep(2)
        self.device.clear_borad_cur_state()

        # wait uboot keyword
        while True:
            status,line = self.device.read()
            if status == True:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                return result

        # enter to uboot
        while True:
            if try_time >= 30:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at uboot':
                logger.print_error("enter to uboot success")
                result = 0
                break
            elif self.borad_cur_state == 'at kernel':
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result

    def uboot_to_kernel(self):
        result = 255
        try_time = 0
        if self.borad_cur_state != 'at uboot':
            logger.print_error("dev is not at uboot now")
            return result

        self.device.write('reset')
        self.device.clear_borad_cur_state()

        while True:
            if try_time >= 30:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                logger.print_error("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def kernel_to_kernel(self):
        result = 255
        try_time = 0
        if self.borad_cur_state != 'at kernel':
            logger.print_error("dev is not at kernel now")
            return result
        
        self.device.write('reboot')
        time.sleep(2)
        self.device.clear_borad_cur_state()

        while True:
            if try_time >= 30:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                logger.print_error("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def uboot_to_uboot(self):
        result = 255
        try_time = 0
        if self.borad_cur_state != 'at uboot':
            logger.print_error("dev is not at uboot now")
            return result

        self.device.write('reset')
        self.device.clear_borad_cur_state()

        # wait uboot keyword
        while True:
            status,line = self.device.read()
            if status == True:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                return result

        # enter to uboot
        while True:
            if try_time >= 30:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at uboot':
                logger.print_error("enter to uboot success")
                result = 0
                break
            elif self.borad_cur_state == 'at kernel':
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result

class idac(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.reboot_opt = reboot_opts(self.uart)

        """ case internal params start """
        self.borad_cur_state = ''
        self.reboot_timeout            = 30
        self.max_read_lines            = 10240
        self.dvfs_on                   = False
        self.package_type              = package_type.PACKAGE_TYPE_MAX
        self.base_vcore_check              = 900    # get from hw & IPL macro define(IDAC_BASE_VOLT)
        self.base_vcpu_check              = 900
        self.overdrive_vcore_check_list      = []     # for ipl core_power check 
        self.overdrive_vcpu_check_list       = []     # for ipl cpu_power check
        self.overdrive_cpufreq_check_list    = []     # for kernel cpufreq check
        self.cpufreq_vcore_check_list        = []     # for kernel core_power check
        self.cpufreq_vcpu_check_list         = []     # for kernel cpu_power check

        self.dump_dts_name             = "fdt.dts"
        self.kernel_base_vcore         = 0      # parse from dts
        self.kernel_base_vcpu          = 0
        self.kernel_opp_table          = []

        self.kernel_prompt             = '/ #'
        self.subpath                   = "idac/resources"
        self.dtc_tool                  = "dtc"
        self.cmd_uboot_reset           = "reset"
        self.cmd_cpufreq_avaliable     = f"cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies"
        self.cmd_cur_cpufreq           = f"cat /sys/devices/system/cpu/cpufreq/cpufreq_testout"


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
    def get_vcore_offset(self, is_kernel=True):
        offset = 0
        result = 255
        result,str_regVal = sys_common.read_register(self.uart, "14", "71", is_kernel)
        if result == 0:
            offset = self._calc_volt_offset(str_regVal)
        else:
            logger.print_error("get core_power offset fail!")
        return offset

    # get cpu_power offseet
    def get_vcpu_offset(self, is_kernel=True):
        offset = 0
        result = 255
        result,str_regVal = sys_common.read_register(self.uart, "15", "11", is_kernel)
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
            self.overdrive_vcore_check_list.append(volt_map)
            minVolt, maxVolt = self._get_ipl_overdrive_voltage_map(package, overdrive, iford_idac_volt_cpu_table)
            volt_map = [minVolt, maxVolt]
            self.overdrive_vcpu_check_list.append(volt_map)

    # get the supported cpufreq list under the specified overdrive
    def _get_kernel_overdrive_cpufreq_map(self, package, overdrive):
        cpufreq_map = []
        for overdrive_vcpu_map in iford_idac_volt_cpu_table[package][overdrive]:
            cpufreq_map.append(overdrive_vcpu_map[0])
        return cpufreq_map

    # get cpufreq support list
    def get_kernel_cpufreq_check_list(self, package):
        for overdrive in overdrive_type[:(len(overdrive_type) - 1)]:
            cpufreq_map = self._get_kernel_overdrive_cpufreq_map(package, iford_idac_volt_cpu_table)
            self.overdrive_cpufreq_check_list.append(cpufreq_map)

    # get the min/max volt under the specified cpufreq
    def get_kernel_cpufreq_voltage_check_list(self, package):
        if package == package_type.PACKAGE_TYPE_QFN128:
            if self.dvfs_on == False:
                self.cpufreq_vcore_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_OFF]
                self.cpufreq_vcpu_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_OFF]
            else:
                self.cpufreq_vcore_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_ON]
                self.cpufreq_vcpu_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_ON]
        else:
            self.cpufreq_vcore_check_list = iford_idac_volt_core_table[package]
            self.cpufreq_vcpu_check_list = iford_idac_volt_cpu_table[package]

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
        tool = f'./{self.dtc_tool}'
        command = [tool, '-I', 'fs', '-O', 'dts', 'base', '-o', self.dump_dts_name]
        #command = [tool, '-I', 'dtb', '-O', 'dts', 'fdt', '-o', self.dump_dts_name]
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

    def _get_base_volt_from_dts(self, dts_file):
        result = 255
        core_base_volt_ready = 0
        cpu_base_volt_ready = 0
        is_core_power_exist = 0
        is_cpu_power_exist = 0

        with open(dts_file, 'r') as file:
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "core_power" in line:
                    core_base_volt_ready = 1
                    is_core_power_exist = 1
                    continue

                if "cpu_power" in line:
                    cpu_base_volt_ready = 1
                    is_cpu_power_exist = 1

                if core_base_volt_ready == 1 and "base_voltage" in line:
                    bast_voltage_attr = line.strip().split('=')
                    base_vcore = bast_voltage_attr[1].strip().strip('<>;')
                    self.kernel_base_vcore = int(base_vcore, 16)
                    logger.print_info(f"get core_power:base voltage {self.kernel_base_vcore}")
                    core_base_volt_ready = 0
                    if self.package_type == package_type.PACKAGE_TYPE_QFN128:
                        result = 0
                        break
                    elif is_core_power_exist == 1 and is_cpu_power_exist == 1:
                        result = 0
                        break

                if cpu_base_volt_ready == 1 and "base_voltage" in line:
                    bast_voltage_attr = line.strip().split('=')
                    base_vcpu = bast_voltage_attr[1].strip().strip('<>;')
                    self.kernel_base_vcpu = int(base_vcpu, 16)
                    logger.print_info(f"get cpu_power:base voltage {self.kernel_base_vcpu}")
                    cpu_base_volt_ready = 0
                    if is_core_power_exist == 1 and is_cpu_power_exist == 1:
                        result = 0
                        break

        if result != 0:
            logger.print_error("get base voltage fail")

        return result
        # bga: get core_power/base_voltage; cpu_power/base_voltage
        # qfn: get core_power/base_voltage
        
    def _get_opp_table_from_dts(self, dts_file):
        freq = 0
        parse_cpufreq_ready = 0
        parse_volt_ready = 0
        freq_volt_list = []

        with open(dts_file, 'r') as file:
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                pattern = re.compile(r'opp[\d]{2}')
                match = pattern.search(line)
                if match:
                    parse_cpufreq_ready = 1
                    #parse_volt_ready = 1
                    continue

                if parse_cpufreq_ready == 1 and "opp-hz" in line:
                    opp_hz = line.strip().split('=')
                    freq = int(opp_hz[1].strip().strip('<>;').split()[1], 16)
                    parse_cpufreq_ready = 0
                    parse_volt_ready = 1

                if parse_volt_ready == 1 and "opp-microvolt" in line:
                    opp_microvolt = line.strip().split('=')
                    volts = opp_microvolt[1].strip().strip('<>;').split()
                    cur_volt = int(volts[0], 16)
                    fast_volt = int(volts[1], 16)
                    slow_volt = int(volts[2], 16)
                    freq_volt_map = [freq, cur_volt, slow_volt, fast_volt]
                    freq_volt_list.append(freq_volt_map)
                    freq_volt_list.sort(key=lambda x: x[0])
                    parse_volt_ready = 0
                    break

        return freq_volt_list

    # dump idac info from devicetree
    def get_kernel_idac_info(self):
        result = 255
        result = self._dump_devicetree()
        if result != 0:
            return result
        
        result = self._convert_devicetree_to_dts()
        if result != 0:
            return result

        dts_path = f"{platform.mount_path}/{self.subpath}/{self.dump_dts_name}"
        result = self._get_base_volt_from_dts(dts_path)
        if result != 0:
            return result
        
        self.kernel_opp_table = self._get_opp_table_from_dts(dts_path)
        return result

    def check_base_voltage(self):
        result = 255
        if self.package_type == package_type.PACKAGE_TYPE_QFN128:
            if self.kernel_base_vcore == self.base_vcore_check:
                result = 0
        else:
            if self.kernel_base_vcore == self.base_vcore_check and self.base_vcpu_check == self.base_vcpu_check:
                result = 0
        if result != 0:
            logger.print_error("kernel base voltage is not match with hw base vcore!")
        return result

    def check_opp_table(self):
        result = 255
        opp_check_table = iford_idac_volt_cpu_table[self.package_type][0]
        kernel_opp_table = [sublist[:1] + sublist[2:] for sublist in self.kernel_opp_table]
        is_subset = all(item in kernel_opp_table for item in opp_check_table)

        if is_subset == True:
            result = 0
        return result

    def check_avaliable_cpufreq(self):
        result = 255
        cpufreq_list = []
        self.uart.write(self.cmd_cpufreq_avaliable)
        status,line = self.uart.read()
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            cpufreq_map = line.strip().split()
            for cpufreq_khz in cpufreq_map:
                cpufreq_hz = int(cpufreq_khz) * 1000
                cpufreq_list.append(cpufreq_hz)

            if cpufreq_list == self.overdrive_cpufreq_check_list:
                logger.print_info(f"check avaliable cpufreq pass")
                result = 0
        else:
            logger.print_error(f"check avaliable cpufreq fail")
            result = 255
        return result

    def check_uboot_voltage(self, overdrive):
        result = 255
        uboot_vcore = self.base_vcore_check + self.get_vcore_offset(False)
        uboot_vcpu = self.base_vcpu_check + self.get_vcpu_offset(False)

        if uboot_vcore >= self.overdrive_vcore_check_list[overdrive][0] and \
            uboot_vcpu <= self.overdrive_vcore_check_list[overdrive][1] and \
            uboot_vcpu >= self.overdrive_vpu_check_list[overdrive][0] and \
            uboot_vcpu <= self.overdrive_vpu_check_list[overdrive][1]:
            result = 0
        return result

    def check_kernel_voltage(self, overdrive, cpufreq):
        result = 255
        kernel_vcore = self.base_vcore_check + self.get_vcore_offset(False)
        kernel_vcpu = self.base_vcpu_check + self.get_vcpu_offset(False)
        vcore_check_item = []
        vcpu_check_item = []

        for item in self.cpufreq_vcore_check_list[overdrive]:
            if item[0] == cpufreq:
                vcore_check_item = item
                break
        for item in self.cpufreq_vcpu_check_list[overdrive]:
            if item[0] == cpufreq:
                vcpu_check_item = item
                break
        if kernel_vcore >= vcore_check_item[1] and kernel_vcore <= vcore_check_item[2] and \
            kernel_vcpu >= vcpu_check_item[1] and kernel_vcpu <= vcpu_check_item[2]:
            result = 0
        return result

    def set_userspace_governor(self):
        cmd_userspace_governor = f"echo userspace > /sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors"
        self.uart.write(cmd_userspace_governor)

    def set_cpufreq(self, cpufreq_khz):
        cmd_scaling_min_freq = f"echo {cpufreq_khz} > /sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq"
        cmd_scaling_max_freq = f"echo {cpufreq_khz} > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq"
        self.uart.write(cmd_scaling_min_freq)
        self.uart.write(cmd_scaling_max_freq)

    def enable_qfn_dvfs(self):
        cmd_enable_qfn_dvfs = f""
        self.uart.write(cmd_enable_qfn_dvfs)


    # run idac test flow
    @logger.print_line_info
    def idac_test(self):
        result = 255
        ret_overdrive = [255, 255, 255]

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
        self.get_kernel_cpufreq_check_list(self.package_type)
        self.get_kernel_cpufreq_voltage_check_list(self.package_type)

        result = self.mount_server_path(self.subpath)
        if result != 0:
            return result
        
        # 3. dump devicetree, 转换成dts，解析base voltage，opp_table信息，保存到case 本地。若解析失败，case结束返回失败。
        result = self.get_kernel_idac_info()
        if result != 0:
            return result

        # cmp base voltage        
        result = self.check_base_voltage()
        if result != 0:
            return result

        # cmp cpufreq list and volts
        result = self.check_opp_table()
        if result != 0:
            return result

        # 4. 重启设备，等待设备进到uboot，设置 LD 环境，保存再重启。若此阶段出现卡住问题，case结束返回失败。
        for overdrive in overdrive_type[:(len(overdrive_type) - 1)]:
            result = self.reboot_opt.kernel_to_uboot()
            if result != 0:
                return result
            cmd_set_overdrive = f"setenv overdrive {overdrive.value};saveenv"
            self.uart.write(cmd_set_overdrive)
            result = self.reboot_opt.uboot_to_uboot()
            if result != 0:
                return result

            # 5. 读取寄存器值，判断读取的电压寄存器是否和case保存的table匹配，如果不匹配，记录LD测试失败，进行下一次的NOD测试。
            ret_overdrive[overdrive] = self.check_uboot_voltage(overdrive)
            if ret_overdrive[overdrive] != 0:
                logger.print_error("{overdrive.name}  check uboot voltage fail")
                continue

            # 6. 执行reset，进到kernel
            result = self.reboot_opt.uboot_to_kernel()
            if result != 0:
                return result
            
            # 7. 获取支持的cpu频率，对比统计的列表看是否一致，如果不一致，记录LD测试失败，进行下一次的NOD测试
            ret_overdrive[overdrive] = self.check_avaliable_cpufreq()
            if ret_overdrive[overdrive] != 0:
                logger.print_error("{overdrive.name}  check avaliable cpufreq fail")
                continue

            # 8. 依次设置到各个支持的频率档位，并读取电压寄存器值，先全部读取完毕再观察对应频率读取到的寄存器值是否和统计列表中的一致，如果不一致，记录LD测试失败，进行下一次的NOD测试
            self.set_userspace_governor()
            for cpufreq in self.overdrive_cpufreq_check_list:
                cpufreq_khz = cpufreq / 1000
                self.set_cpufreq(cpufreq_khz)
                ret_overdrive[overdrive] = self.check_kernel_voltage(overdrive, cpufreq)
                if ret_overdrive[overdrive] != 0:
                    logger.print_error("{overdrive.name}  check voltage fail at cpufreq:{cpufreq}, dvfs:{self.dvfs_on}")
                    break

            if self.package == package_type.PACKAGE_TYPE_QFN128:
                self.enable_qfn_dvfs()
                self.dvfs_on = True
                self.get_kernel_cpufreq_voltage_check_list(self.package_type)
                for cpufreq in self.overdrive_cpufreq_check_list:
                    cpufreq_khz = cpufreq / 1000
                    self.set_cpufreq(cpufreq_khz)
                    ret_overdrive[overdrive] = self.check_kernel_voltage(overdrive, cpufreq)
                    if ret_overdrive[overdrive] != 0:
                        logger.print_error("{overdrive.name}  check voltage fail at cpufreq:{cpufreq}, dvfs:{self.dvfs_on}")
                        break

        # 10. 汇总LD/NOD/OD的测量结果，返回最后的测试结果，都ok返回成功，否则返回失败
        for overdrive in overdrive_type[:(len(overdrive_type) - 1)]:
            if ret_overdrive[overdrive] != 0:
                result = 255
                break

        if result == 0:
            logger.print_warning("idac test pass!")
        else:
            logger.print_error("idac test fail!")

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

