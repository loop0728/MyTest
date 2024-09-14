import os
import shutil
import time
import re
import subprocess
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common
import Suite.IDAC.reboot_opts as reboot_opts


""" case import start """
from enum import Enum
from idac_var import overdrive_type, package_type, corner_ic_type, idac_power_type, dvfs_state
from idac_var import iford_idac_volt_core_table, iford_idac_volt_cpu_table, iford_ipl_overdrive_cpufreq_map, iford_idac_qfn_dvfs_vcore_table

""" case import end """


class idac(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.reboot_opt = reboot_opts.RebootOpts(self.uart)

        """ case internal params start """
        self.borad_cur_state = ''
        self.reboot_timeout            = 30
        self.max_read_lines            = 10240
        self.dvfs_on                   = False
        self.package_type              = package_type.PACKAGE_TYPE_MAX
        self.base_vcore_check             = 900    # get from hw & IPL macro define(IDAC_BASE_VOLT)
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
        self.dtc_tool                  = "dtc"
        self.cmd_uboot_reset           = "reset"
        self.cmd_cpufreq_avaliable     = f"cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies"
        self.cmd_cur_cpufreq           = f"cat /sys/devices/system/cpu/cpufreq/cpufreq_testout"
        self.cmd_governor              = "/sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors"
        self.cmd_scaling_min_freq      = "/sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq"
        self.cmd_scaling_max_freq      = "/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq"
        self.cmd_qfn_dvfs              = "/sys/devices/system/voltage/core_power/voltage_current"

        self.case_env_param = {
            'borad_cur_state': '',
            'reboot_timeout': 30,
            'max_read_lines': 10240
        }
        self.case_target_param = {
            'base_vcore_check': 900,
            'base_vcpu_check': 900,
            'overdrive_vcore_check_list': [],
            'overdrive_vcpu_check_list': [],
            'overdrive_cpufreq_check_list': [],
            'cpufreq_vcore_check_list': [],
            'cpufreq_vcpu_check_list': []
        }
        self.case_cmd_param = {
            'cmd_uboot_reset': 'reset',
            'cmd_cpufreq_avaliable': 'cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies',
            'cmd_cur_cpufreq': 'cat /sys/devices/system/cpu/cpufreq/cpufreq_testout',
            'cmd_governor': '/sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors',
            'cmd_scaling_min_freq': '/sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq',
            'cmd_scaling_max_freq': '/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq',
            'cmd_qfn_dvfs': '/sys/devices/system/voltage/core_power/voltage_current'
        }
        self.case_test_param = {
            'kernel_prompt': '/ #',
            'dtc_tool': 'dtc',
            'dump_dts_name': 'fdt.dts',
            'dvfs_on': False,
            'package_type': package_type.PACKAGE_TYPE_MAX,
            'kernel_base_vcore': 0,
            'kernel_base_vcpu': 0,
            'kernel_opp_table': []
        }

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

    def _calc_volt_offset(self, str_hex) -> int:
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
        value = (bit3 << 3) + (bit2 << 2) + (bit1 << 1) + bit0

        if bit4 == 0:
            sign = -1
        else:
            sign = 1
        if bit5 == 0:
            unit = 20
        else:
            unit = 10
        offset = value * sign * unit
        print(f"bit5~0:{bit5}{bit4}{bit3}{bit2}{bit1}{bit0}, value:{value}, sign:{sign}, unit:{unit}, offset:{offset}")
        test_bit3 = bit3 << 3
        test_bit2 = bit2 << 2
        test_bit1 = bit1 << 1
        test_bit0 = bit0
        print(f"test_bit3:{test_bit3}, test_bit2:{test_bit2}, test_bit1:{test_bit1}, test_bit0:{test_bit0},")
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
        print(f"vcore_offset:{offset}")
        return result, offset

    # get cpu_power offseet
    def get_vcpu_offset(self, is_kernel=True):
        offset = 0
        result = 255
        result,str_regVal = sys_common.read_register(self.uart, "15", "11", is_kernel)
        if result == 0:
            offset = self._calc_volt_offset(str_regVal)
        else:
            logger.print_error("get cpu_power offset fail!")
        print(f"vcpu_offset:{offset}")
        return result, offset

    # get the min/max volt under the specified overdrive
    def _get_ipl_overdrive_voltage_map(self, package, overdrive, table):
        minVolt = maxVolt = 0
        curFreq = iford_ipl_overdrive_cpufreq_map[overdrive.value]
        for overdrive_volt_map in table[package.value][overdrive.value]:
            if curFreq == overdrive_volt_map[0]:
                minVolt = overdrive_volt_map[1]
                maxVolt = overdrive_volt_map[2]
                break
        return minVolt, maxVolt

    # get ipl core_power/cpu_power check list
    # self.overdrive_vcore_check_list = [
    #   [minVolt, maxVolt],     #LD
    #   [minVolt, maxVolt],     #NOD
    #   [minVolt, maxVolt]      #OD
    # ]
    # self.overdrive_vcpu_check_list = [
    #   [minVolt, maxVolt],     #LD
    #   [minVolt, maxVolt],     #NOD
    #   [minVolt, maxVolt]      #OD
    # ]
    def get_ipl_volt_check_list(self, package):
        #for overdrive in overdrive_type[:(len(overdrive_type) - 1)]:
        for overdrive in overdrive_type:
            if overdrive != overdrive_type.OVERDRIVE_TYPE_MAX:
                minVolt, maxVolt = self._get_ipl_overdrive_voltage_map(package, overdrive, iford_idac_volt_core_table)
                volt_map = [minVolt, maxVolt]
                self.overdrive_vcore_check_list.append(volt_map)
                minVolt, maxVolt = self._get_ipl_overdrive_voltage_map(package, overdrive, iford_idac_volt_cpu_table)
                volt_map = [minVolt, maxVolt]
                self.overdrive_vcpu_check_list.append(volt_map)

    # get the supported cpufreq list under the specified overdrive
    # return: [cpufreq_xx, cpufreq_yy, cpufreq_zz, ...]
    def _get_kernel_overdrive_cpufreq_map(self, package, overdrive):
        cpufreq_map = []
        for overdrive_vcpu_map in iford_idac_volt_cpu_table[package.value][overdrive.value]:
            cpufreq_map.append(overdrive_vcpu_map[0])
        return cpufreq_map

    # get cpufreq support list
    # self.overdrive_cpufreq_check_list = [
    #       [cpufreq_xx, cpufreq_yy],                       # LD
    #       [cpufreq_xx, cpufreq_yy, cpufreq_zz],           # NOD
    #       [cpufreq_xx, cpufreq_yy, cpufreq_zz, ...]       # OD
    #   ]
    def get_kernel_cpufreq_check_list(self, package):
        for overdrive in overdrive_type:
            if overdrive != overdrive_type.OVERDRIVE_TYPE_MAX:
                cpufreq_map = self._get_kernel_overdrive_cpufreq_map(package, overdrive)
                self.overdrive_cpufreq_check_list.append(cpufreq_map)

    # get the min/max volt under the specified cpufreq
    # self.cpufreq_vcore_check_list = [
    #   [[freq, minV, maxV], ...],      #LD
    #   [[freq, minV, maxV], ...],      #NOD
    #   [[freq, minV, maxV], ...]       #OD
    # ]
    # self.cpufreq_vcore_check_list = [
    #   [[freq, minV, maxV], ...],      #LD
    #   [[freq, minV, maxV], ...],      #NOD
    #   [[freq, minV, maxV], ...]       #OD
    # ]
    def get_kernel_cpufreq_voltage_check_list(self, package):
        if package == package_type.PACKAGE_TYPE_QFN128:
            if self.dvfs_on == False:
                self.cpufreq_vcore_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_OFF.value]
                self.cpufreq_vcpu_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_OFF.value]
            else:
                self.cpufreq_vcore_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_ON.value]
                self.cpufreq_vcpu_check_list = iford_idac_qfn_dvfs_vcore_table[dvfs_state.DVFS_STATE_ON.value]
        else:
            self.cpufreq_vcore_check_list = iford_idac_volt_core_table[package.value]
            self.cpufreq_vcpu_check_list = iford_idac_volt_cpu_table[package.value]

    def _check_emac_ko_insmod_status(self):
        result = 255
        net_interface = "eth0"
        cmd_check_insmod_status = f"ifconfig -a | grep {net_interface};echo $?"
        self.uart.write(cmd_check_insmod_status)
        status,line = self.uart.read(1, 30)
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if net_interface in line:
                logger.print_info("ko has insmoded already")
                result = 0
        else:
            logger.print_error(f"read line fail, {line}")
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
        logger.print_info(f"set board ip and mount server path ...")
        sys_common.set_board_kernel_ip(self.uart)
        status = sys_common.mount_to_server(self.uart, path)
        if status == True:
            logger.print_info(f"mount {path} success")
            result = 0
        else:
            logger.print_error(f"mount {path} fail")
            result = 255
        return result

    def _delete_dump_files(self):
        result = 255
        # check dump file exist
        cmd_stat_dump_file = "stat /mnt/base"
        self.uart.write(cmd_stat_dump_file)
        status,line = self.uart.read()
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if "No such file or directory" in line:
                logger.print_info("dump file is not exist, no need to delete")
                result = 0
                return result
        else:
            logger.print_error(f"stat dump file fail")
            result = 255
            return result

        cmd_rm_dump_file = "rm /mnt/base -r;echo $?"
        self.uart.write(cmd_rm_dump_file)
        status,line = self.uart.read(1, 120)
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if "0" in line:
                logger.print_info("rm old dump file ok")
                result = 0
        else:
            logger.print_error(f"rm old dump file fail")
            result = 255
        logger.print_info(f"{line}")
        return result

    def _dump_devicetree(self):
        result = 255
        result = self._delete_dump_files()
        if result != 0:
            return result
        cmd_dump_devicetree = f"cp /sys/firmware/devicetree/base /mnt -r;echo $?"
        self.uart.write(cmd_dump_devicetree)
        status,line = self.uart.read(1, 120)
        if status == True:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            if "0" in line:
                logger.print_info("dump devicetree ok")
                result = 0
            else:
                logger.print_error(f"dump devicetree fail")
                result = 255
        else:
            logger.print_error(f"read line fail after cmd:{cmd_dump_devicetree}")
            result = 255
        return result

    def _run_server_cmd(self, cmd):
        result = 255
        logger.print_info(f"server run {cmd}")
        try:
            ret = subprocess.run(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.print_info(f"Command output: {ret.stdout}")
        except subprocess.CalledProcessError as e:
            logger.print_error('Command failed with return code:', e.returncode)
            logger.print_error('Output:', e.output)
            logger.print_error('Error:', e.stderr)

        if ret.returncode == 0:
            logger.print_info(f"run {cmd} ok")
            result = 0
        else:
            logger.print_error(f"run {cmd} fail, errorcode: {ret.returncode}")
            result = 255
        return result

    def _convert_devicetree_to_dts(self, path):  # need ATP server support mount this dir
        result = 255
        tool = f'./{self.dtc_tool}'
        cmd_convert_dts = [tool, '-I', 'fs', '-O', 'dts', 'base', '-o', self.dump_dts_name]

        # cd mount path
        #old_dir = os.getcwd()
        try:
            os.chdir(path)
            logger.print_info(f"Changed directory to {path}")
        except OSError as e:
            logger.print_error(f"Error changing directory: {e.strerror}")
            return result

        # convert to dts
        result = self._run_server_cmd(cmd_convert_dts)
        return result

    # get actual voltage
    # self.kernel_base_vcore: xxx mv
    # self.kernel_base_vcpu : xxx mv
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
                    logger.print_info("core_power node exist")
                    continue

                if "cpu_power" in line:
                    cpu_base_volt_ready = 1
                    is_cpu_power_exist = 1
                    logger.print_info("cpu_power node exist")

                if core_base_volt_ready == 1 and "base_voltage" in line:
                    bast_voltage_attr = line.strip().split('=')
                    base_vcore = bast_voltage_attr[1].strip().strip('<>;')
                    self.kernel_base_vcore = int(base_vcore, 16)
                    logger.print_info(f"get core_power:base voltage {self.kernel_base_vcore} mv")
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
                    logger.print_info(f"get cpu_power:base voltage {self.kernel_base_vcpu} mv")
                    cpu_base_volt_ready = 0
                    if is_core_power_exist == 1 and is_cpu_power_exist == 1:
                        result = 0
                        break

        if result != 0:
            logger.print_error("get base voltage fail")

        return result

    # get opp table from dts
    # freq_volt_list = [
    #   [freq, cur_volt, fast_volt, slow_volt],
    #   [freq, cur_volt, fast_volt, slow_volt],
    #   ...
    # ]
    def _get_opp_table_from_dts(self, dts_file):
        freq = 0
        cur_volt = 0
        fast_volt = 0
        slow_volt = 0
        parse_opp_node_ready = 0
        parse_cpufreq_done = 0
        parse_volt_done = 0
        freq_volt_list = []

        with open(dts_file, 'r') as file:
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                pattern = re.compile(r'opp[\d]{2} {')
                match = pattern.search(line)
                if match:
                    parse_opp_node_ready = 1
                    continue

                if parse_opp_node_ready == 1 and "opp-hz" in line:
                    opp_hz = line.strip().split('=')
                    freq = int(opp_hz[1].strip().strip('<>;').split()[1], 16)
                    parse_cpufreq_done = 1
                    continue

                if parse_opp_node_ready == 1 and "opp-microvolt" in line:
                    opp_microvolt = line.strip().split('=')
                    volts = opp_microvolt[1].strip().strip('<>;').split()
                    cur_volt = int(volts[0], 16)
                    fast_volt = int(volts[1], 16)
                    slow_volt = int(volts[2], 16)
                    parse_volt_done = 1
                    continue

                if parse_cpufreq_done == 1 and parse_volt_done == 1:
                    freq_volt_map = [freq, cur_volt, fast_volt, slow_volt]
                    freq_volt_list.append(freq_volt_map)
                    parse_cpufreq_done = 0
                    parse_volt_done = 0
                    parse_opp_node_ready = 0

        freq_volt_list.sort(key=lambda x: x[0])
        return freq_volt_list

    # dump idac info from devicetree
    def get_kernel_idac_info(self):
        result = 255
        print(f"local_mount_path:{self.local_mount_path}")
        dts_path = f"{self.local_mount_path}/{self.dump_dts_name}"

        logger.print_info(f"begin to dump devicetree ...")
        result = self._dump_devicetree()
        if result != 0:
            return result

        logger.print_info(f"begin to convert devicetree blob to dts ...")
        result = self._convert_devicetree_to_dts(self.local_mount_path)
        if result != 0:
            return result


        logger.print_info(f"get kernel base voltage from dts ...")
        result = self._get_base_volt_from_dts(dts_path)
        if result != 0:
            return result

        logger.print_info(f"get kernel opp table from dts ...")
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
        if self.dvfs_on == False and self.package_type == package_type.PACKAGE_TYPE_QFN128:
            result = 0
        else:
            opp_check_table = iford_idac_volt_cpu_table[self.package_type.value][overdrive_type.OVERDRIVE_TYPE_OD.value]
            kernel_opp_table = [sublist[:1] + sublist[2:] for sublist in self.kernel_opp_table]
            print(f"{opp_check_table}")
            print(f"{kernel_opp_table}")
            # check if kernel_opp_table contains opp_check_table
            is_subset = all(item in kernel_opp_table for item in opp_check_table)
            if is_subset == True:
                result = 0

        if result == 0:
            logger.print_info(f"check kernel opp table ok")
        else:
            logger.print_error("kernel opp table is not match with check opp table!")
        return result

    def check_avaliable_cpufreq(self, overdrive):
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

            if cpufreq_list == self.overdrive_cpufreq_check_list[overdrive.value]:
                logger.print_info(f"check avaliable cpufreq pass")
                result = 0
        else:
            logger.print_error(f"check avaliable cpufreq fail")
            result = 255
        return result

    def check_uboot_voltage(self, overdrive):
        result = 255
        uboot_vcore = 0
        uboot_vcpu = 0
        vcore_check_item = []
        vcpu_check_item = []

        result,vcore_offset = self.get_vcore_offset(False)
        if result != 0:
            return result
        result,vcpu_offset = self.get_vcpu_offset(False)
        if result != 0:
            return result
        uboot_vcore = self.base_vcore_check + vcore_offset
        if self.package_type == package_type.PACKAGE_TYPE_QFN128:
            uboot_vcpu = uboot_vcore
        else:
            uboot_vcpu = self.base_vcpu_check + vcpu_offset

        vcore_check_item = self.overdrive_vcore_check_list[overdrive.value]
        vcpu_check_item = self.overdrive_vcpu_check_list[overdrive.value]

        uboot_vcore_uv = uboot_vcore * 1000
        uboot_vcpu_uv = uboot_vcpu * 1000
        logger.print_info(f"uboot_vcore:{uboot_vcore_uv}, "
                          f"target:[{vcore_check_item[0]}, {vcore_check_item[1]}]")
        logger.print_info(f"uboot_vcpu:{uboot_vcpu_uv}, "
                          f"target:[{vcpu_check_item[0]}, {vcpu_check_item[1]}]")

        if uboot_vcore_uv >= self.overdrive_vcore_check_list[overdrive.value][0] and \
            uboot_vcore_uv <= self.overdrive_vcore_check_list[overdrive.value][1] and \
            uboot_vcpu_uv >= self.overdrive_vcpu_check_list[overdrive.value][0] and \
            uboot_vcpu_uv <= self.overdrive_vcpu_check_list[overdrive.value][1]:
            result = 0
        else:
            result = 255
        return result

    def check_kernel_voltage(self, overdrive, cpufreq):
        result = 255
        kernel_vcore = 0
        kernel_vcpu = 0
        vcore_check_item = []
        vcpu_check_item = []

        result,vcore_offset = self.get_vcore_offset(True)
        if result != 0:
            return result
        result,vcpu_offset = self.get_vcpu_offset(True)
        if result != 0:
            return result
        kernel_vcore = self.base_vcore_check + vcore_offset
        if self.package_type == package_type.PACKAGE_TYPE_QFN128:
            kernel_vcpu = kernel_vcore
        else:
            kernel_vcpu = self.base_vcpu_check + vcpu_offset

        for item in self.cpufreq_vcore_check_list[overdrive.value]:
            if item[0] == cpufreq:
                vcore_check_item = item
                break
        for item in self.cpufreq_vcpu_check_list[overdrive.value]:
            if item[0] == cpufreq:
                vcpu_check_item = item
                break

        kernel_vcore_uv = kernel_vcore * 1000
        kernel_vcpu_uv = kernel_vcpu * 1000
        logger.print_info(f"kernel_vcore:{kernel_vcore_uv}, freq:{vcore_check_item[0]} "
                          f"target:[{vcore_check_item[1]}, {vcore_check_item[2]}]")
        logger.print_info(f"kernel_vcpu:{kernel_vcpu_uv}, freq:{vcpu_check_item[0]} "
                          f"target:[{vcpu_check_item[1]}, {vcpu_check_item[2]}]")

        if kernel_vcore_uv >= vcore_check_item[1] and kernel_vcore_uv <= vcore_check_item[2] and \
            kernel_vcpu_uv >= vcpu_check_item[1] and kernel_vcpu_uv <= vcpu_check_item[2]:
            result = 0
        return result

    def set_userspace_governor(self):
        cmd_userspace_governor = f"echo userspace > {self.cmd_governor}"
        self.uart.write(cmd_userspace_governor)

    def set_cpufreq(self, cpufreq_khz):
        cmd_set_scaling_min_freq = f"echo {cpufreq_khz} > {self.cmd_scaling_min_freq}"
        cmd_set_scaling_max_freq = f"echo {cpufreq_khz} > {self.cmd_scaling_max_freq}"
        self.uart.write(cmd_set_scaling_min_freq)
        self.uart.write(cmd_set_scaling_max_freq)

    def enable_qfn_dvfs(self):
        cmd_enable_qfn_dvfs = f"echo 0 > {self.cmd_qfn_dvfs}"
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

        # get overdrive-volt check table
        self.get_ipl_volt_check_list(self.package_type)

        # get overdrive-cpufreq check table
        self.get_kernel_cpufreq_check_list(self.package_type)

        # get cpufreq-volt_range check table
        self.get_kernel_cpufreq_voltage_check_list(self.package_type)

        # mount res path to the board
        result = self.mount_server_path(self.case_res_path)
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
        for overdrive in overdrive_type:
            if overdrive != overdrive_type.OVERDRIVE_TYPE_MAX:
                logger.print_info(f"reboot to set overdrive to {overdrive.name}")
                result = self.reboot_opt.kernel_to_uboot()
                if result != 0:
                    return result
                cmd_set_overdrive = f"setenv overdrive {overdrive.value};saveenv"
                self.uart.write(cmd_set_overdrive)
                logger.print_info("reset to uboot for testing ...")
                result = self.reboot_opt.uboot_to_uboot()
                if result != 0:
                    return result

                # 5. 读取寄存器值，判断读取的电压寄存器是否和case保存的table匹配，如果不匹配，记录LD测试失败，进行下一次的NOD测试。
                logger.print_info(f"{overdrive.name}: check uboot voltage")
                ret_overdrive[overdrive.value] = self.check_uboot_voltage(overdrive)

                # 6. 执行reset，进到kernel
                logger.print_info("reset to kernel for testing ...")
                result = self.reboot_opt.uboot_to_kernel()
                if result != 0:
                    return result

                if ret_overdrive[overdrive.value] != 0:
                    logger.print_error(f"{overdrive.name} check uboot voltage fail")
                    continue

                # 7. 获取支持的cpu频率，对比统计的列表看是否一致，如果不一致，记录LD测试失败，进行下一次的NOD测试
                logger.print_info(f"{overdrive.name}: check kernel avaliable cpufreq")
                ret_overdrive[overdrive.value] = self.check_avaliable_cpufreq(overdrive)
                if ret_overdrive[overdrive.value] != 0:
                    logger.print_error(f"{overdrive.name} check avaliable cpufreq fail")
                    continue

                # 8. 依次设置到各个支持的频率档位，并读取电压寄存器值，先全部读取完毕再观察对应频率读取到的寄存器值是否和统计列表中的一致，如果不一致，记录LD测试失败，进行下一次的NOD测试
                logger.print_info(f"{overdrive.name}: check kernel voltage at different cpufreq")
                self.set_userspace_governor()
                for cpufreq in self.overdrive_cpufreq_check_list[overdrive.value]:
                    cpufreq_khz = cpufreq / 1000
                    self.set_cpufreq(cpufreq_khz)
                    ret_overdrive[overdrive.value] = self.check_kernel_voltage(overdrive, cpufreq)
                    if ret_overdrive[overdrive.value] != 0:
                        logger.print_error(f"{overdrive.name} check voltage fail at cpufreq:{cpufreq}, dvfs:{self.dvfs_on}")
                        break

                if self.package_type == package_type.PACKAGE_TYPE_QFN128:
                    self.enable_qfn_dvfs()
                    self.dvfs_on = True
                    self.get_kernel_cpufreq_voltage_check_list(self.package_type)
                    for cpufreq in self.overdrive_cpufreq_check_list[overdrive.value]:
                        cpufreq_khz = cpufreq / 1000
                        self.set_cpufreq(cpufreq_khz)
                        ret_overdrive[overdrive.value] = self.check_kernel_voltage(overdrive, cpufreq)
                        if ret_overdrive[overdrive.value] != 0:
                            logger.print_error(f"{overdrive.name} check voltage fail at cpufreq:{cpufreq}, dvfs:{self.dvfs_on}")
                            break

        # 10. 汇总LD/NOD/OD的测量结果，返回最后的测试结果，都ok返回成功，否则返回失败
        for overdrive in overdrive_type:
            if overdrive != overdrive_type.OVERDRIVE_TYPE_MAX:
                if ret_overdrive[overdrive.value] != 0:
                    result = 255
                    break

        if result == 0:
            logger.print_warning("idac test pass!")
        else:
            logger.print_error("idac test fail!")

        return result
    """ case internal functions end """

    def reboot_test(self):
        result = 255
        result = self.check_kernel_env()
        if result != 0:
            return result

        logger.print_info(f"reboot to uboot")
        result = self.reboot_opt.kernel_to_uboot()
        if result != 0:
            return result
        cmd_set_overdrive = f"setenv overdrive 2;saveenv"
        self.uart.write(cmd_set_overdrive)
        logger.print_info("reset to uboot for testing ...")
        result = self.reboot_opt.uboot_to_uboot()
        if result != 0:
            return result
        logger.print_info("reset to kernel for testing ...")
        result = self.reboot_opt.uboot_to_kernel()
        if result != 0:
            return result
        return result

    @logger.print_line_info
    def runcase(self):
        result = 255
        """ case body start """
        result = self.idac_test()
        #result = self.reboot_test()
        """ case body end """

        return result

    @logger.print_line_info
    def system_help(args):
        logger.print_warning("check idac voltage ctrl")
        logger.print_warning("cmd: idac")

