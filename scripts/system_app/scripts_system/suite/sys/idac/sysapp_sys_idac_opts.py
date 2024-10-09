#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""IDAC test scenarios"""

import re
import subprocess
from cases.platform.sys.idac.idac_var import IFORD_IDAC_VOLT_CPU_TABLE
from cases.platform.sys.idac.idac_var import IFORD_IPL_OVERDRIVE_CPUFREQ_MAP
from suite.common.sysapp_common_logger import logger
import suite.common.sysapp_common as sys_common


class SysappIdacOpts():
    """A class representing idac options
    Attributes:
        None
    """
    def __init__(self):
        """Class constructor.
        Args:
            None
        Returns:
            None
        """

    @staticmethod
    def calc_volt_offset(str_hex) -> int:
        """calculate voltage offset from idac register value
        Args:
            str_hex (str): idac register value
        Returns:
            offset (int): return voltage offset
        """
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
        #print(f'bit5~0:{bit5}{bit4}{bit3}{bit2}{bit1}{bit0}, value:{value}, '
        #       'sign:{sign}, unit:{unit}, offset:{offset}')
        return offset

    @staticmethod
    def get_ipl_overdrive_voltage_map(package, overdrive, table):
        """get the min/max volt under the specified overdrive
        Args:
            package (SysappPackageType): package type
            overdrive (SysappOverdriveType): overdrive type
            table (list): overdrive & voltage mapping list
        Returns:
            min_volt (int): min volt under the specified overdrive
            max_volt (int): max volt under the specified overdrive
        """
        min_volt = max_volt = 0
        cur_freq = IFORD_IPL_OVERDRIVE_CPUFREQ_MAP[overdrive.value]
        for overdrive_volt_map in table[package.value][overdrive.value]:
            if cur_freq == overdrive_volt_map[0]:
                min_volt = overdrive_volt_map[1]
                max_volt = overdrive_volt_map[2]
                break
        return min_volt, max_volt

    @staticmethod
    def get_kernel_overdrive_cpufreq_map(package, overdrive):
        """get the supported cpufreq list of the specified package type under
            the specified overdrive
        Args:
            package (SysappPackageType): package type
            overdrive (SysappOverdriveType): overdrive type
        Returns:
            cpufreq_map (list): cpufreq list under the specified overdrive
            list format is [cpufreq_xx, cpufreq_yy, cpufreq_zz, ...]
        """
        cpufreq_map = []
        for overdrive_vcpu_map in IFORD_IDAC_VOLT_CPU_TABLE[package.value][overdrive.value]:
            cpufreq_map.append(overdrive_vcpu_map[0])
        return cpufreq_map

    @staticmethod
    def run_server_cmd(cmd):
        """run cmd on server
        Args:
            cmd (str): command string
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False
        logger.print_info(f"server run {cmd}")
        try:
            ret = subprocess.run(cmd, universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=True)
            logger.print_info(f"Command output: {ret.stdout}")
        except subprocess.CalledProcessError as error:
            logger.print_error('Command failed with return code:', error.returncode)
            logger.print_error('Output:', error.output)
            logger.print_error('Error:', error.stderr)

        if ret.returncode == 0:
            logger.print_info(f"run {cmd} ok")
            result = True
        else:
            logger.print_error(f"run {cmd} fail, errorcode: {ret.returncode}")
            result = False
        return result

    @staticmethod
    def get_opp_table_from_dts(dts_file):
        """get opp table from dts
        Args:
            dts_file (str): the path of dts file
        Returns:
            freq_volt_list (list): freq-cur_vol-min_vol-max_vol mapping list

            freq_volt_list format is :
            [
                [freq, cur_volt, fast_volt, slow_volt],
                [freq, cur_volt, fast_volt, slow_volt],
                ...
            ]
        """
        parse_opp_node_ready = 0
        parse_cpufreq_done = 0
        parse_volt_done = 0
        freq_volt_list = []
        opp_item = {
            'freq': 0,
            'cur_volt': 0,
            'fast_volt': 0,
            'slow_volt': 0
        }

        with open(dts_file, 'r', encoding='utf-8') as file:
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                pattern = re.compile(r'opp[\d]{2} {')
                match = pattern.search(line)
                if match:
                    parse_opp_node_ready = 1
                    continue

                if parse_opp_node_ready == 1 and "opp-hz" in line:
                    opp_hz = line.strip().split('=')
                    opp_item['freq'] = int(opp_hz[1].strip().strip('<>;').split()[1], 16)
                    parse_cpufreq_done = 1
                    continue

                if parse_opp_node_ready == 1 and "opp-microvolt" in line:
                    opp_microvolt = line.strip().split('=')
                    volts = opp_microvolt[1].strip().strip('<>;').split()
                    opp_item['cur_volt'] = int(volts[0], 16)
                    opp_item['fast_volt'] = int(volts[1], 16)
                    opp_item['slow_volt'] = int(volts[2], 16)
                    parse_volt_done = 1
                    continue

                if parse_cpufreq_done == 1 and parse_volt_done == 1:
                    freq_volt_list.append(list(opp_item.values()))
                    parse_cpufreq_done = 0
                    parse_volt_done = 0
                    parse_opp_node_ready = 0

        freq_volt_list.sort(key=lambda x: x[0])
        return freq_volt_list
