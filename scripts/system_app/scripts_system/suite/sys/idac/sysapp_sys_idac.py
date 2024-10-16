#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""IDAC test scenarios"""
from cases.platform.sys.idac.idac_var import (IFORD_IDAC_VOLT_CORE_TABLE,
                                              IFORD_IDAC_VOLT_CPU_TABLE,
                                              IFORD_IDAC_QFN_DVFS_VCORE_TABLE)
from suite.common.sysapp_common_types import (SysappOverdriveType,
                                              SysappPackageType,
                                              SysappDvfsState)
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_register_opts import SysappRegisterOpts
from suite.common.sysapp_common_device_opts import SysappDeviceOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
from suite.common.sysapp_common_dts_opts import SysappDtsOpts
from suite.common.sysapp_common_types import SysappErrorCodes
from suite.sys.idac.sysapp_sys_idac_opts import SysappIdacOpts as IdacOpts
from sysapp_client import SysappClient as Client

class SysappSysIdac(CaseBase):
    """A class representing IDAC test flow
    Attributes:
        uart (Device): device handle
        case_res_path (str): case resource file path on mount server
        local_mount_path (str): case resource mount path on host
        case_target_param (dict): targets parameters
        case_cmd_param (dict): test commands
        case_test_param (dict): internal parameters for test
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
        self.case_res_path += "/resources"
        self.local_mount_path += "/resources"
        self.case_target_param = {
            'base_vcore_check': 900,    # get from hw & IPL macro define(IDAC_BASE_VOLT)
            'base_vcpu_check': 900,
            'overdrive_vcore_check_list': [],   # for ipl core_power check
            'overdrive_vcpu_check_list': [],    # for ipl cpu_power check
            'overdrive_cpufreq_check_list': [], # for kernel cpufreq check
            'cpufreq_vcore_check_list': [],     # for kernel core_power check
            'cpufreq_vcpu_check_list': []       # for kernel cpu_power check
        }
        self.case_cmd_param = {
            'cmd_cpufreq_available': ('cat /sys/devices/system/cpu/cpufreq/policy0/'
                                      'scaling_available_frequencies'),
            'cmd_governor': '/sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors',
            'cmd_scaling_min_freq': '/sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq',
            'cmd_scaling_max_freq': '/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq',
            'cmd_qfn_dvfs': '/sys/devices/system/voltage/core_power/voltage_current'
        }
        self.case_test_param = {
            'dump_dts_name': 'fdt.dts',
            'dvfs_on': False,
            'SysappPackageType': SysappPackageType.PACKAGE_TYPE_MAX,
            # parse from dts
            'kernel_base_vcore': 0,
            'kernel_base_vcpu': 0,
            'kernel_opp_table': []
        }

    def get_vcore_offset(self):
        """read register of core_power offset
        Args:
            None:
        Returns:
            result (bool): option executes success or fail
            offset (int): return register value
        """
        offset = 0
        result = False
        result, str_reg_value = SysappRegisterOpts.read_register(self.uart, "14", "71")
        if result:
            offset = IdacOpts.calc_volt_offset(str_reg_value)
        else:
            logger.error("get core_power offset fail!")
        print(f"vcore_offset:{offset}")
        return result, offset

    def get_vcpu_offset(self):
        """read register of cpu_power offset
        Args:
            None:
        Returns:
            result (bool): option executes success or fail
            offset (int): return register value
        """
        offset = 0
        result = False
        result, str_reg_value = SysappRegisterOpts.read_register(self.uart, "15", "11")
        if result:
            offset = IdacOpts.calc_volt_offset(str_reg_value)
        else:
            logger.error("get cpu_power offset fail!")
        print(f"vcpu_offset:{offset}")
        return result, offset

    def get_ipl_volt_check_list(self, package):
        """get ipl core_power/cpu_power check list refer to the specified package type
        Args:
            package (SysappPackageType): package type
        Returns:
            None

            volt_check_list format is:
            [
                [minVolt, maxVolt],     #LD
                [minVolt, maxVolt],     #NOD
                [minVolt, maxVolt]      #OD
            ]
        """
        for overdrive in SysappOverdriveType:
            if overdrive != SysappOverdriveType.OVERDRIVE_TYPE_MAX:
                # min_volt, max_volt = self._get_ipl_overdrive_voltage_map(package, overdrive,\
                #                                                      IFORD_IDAC_VOLT_CORE_TABLE)
                min_volt, max_volt = IdacOpts.get_ipl_overdrive_voltage_map(package, overdrive,\
                                                                     IFORD_IDAC_VOLT_CORE_TABLE)
                volt_map = [min_volt, max_volt]
                self.case_target_param['overdrive_vcore_check_list'].append(volt_map)
                # min_volt, max_volt = self._get_ipl_overdrive_voltage_map(package, overdrive,\
                #                                                      IFORD_IDAC_VOLT_CPU_TABLE)
                min_volt, max_volt = IdacOpts.get_ipl_overdrive_voltage_map(package, overdrive,\
                                                                     IFORD_IDAC_VOLT_CPU_TABLE)
                volt_map = [min_volt, max_volt]
                self.case_target_param['overdrive_vcpu_check_list'].append(volt_map)

    def get_kernel_cpufreq_check_list(self, package):
        """get the whole cpufreq support list
        Args:
            package (SysappPackageType): package type
        Returns:
            None:

            overdrive_cpufreq_check_list format is:
            [
                [cpufreq_xx, cpufreq_yy],                       # LD
                [cpufreq_xx, cpufreq_yy, cpufreq_zz],           # NOD
                [cpufreq_xx, cpufreq_yy, cpufreq_zz, ...]       # OD
            ]
        """
        for overdrive in SysappOverdriveType:
            if overdrive != SysappOverdriveType.OVERDRIVE_TYPE_MAX:
                #cpufreq_map = self._get_kernel_overdrive_cpufreq_map(package, overdrive)
                cpufreq_map = IdacOpts.get_kernel_overdrive_cpufreq_map(package, overdrive)
                self.case_target_param['overdrive_cpufreq_check_list'].append(cpufreq_map)

    def get_kernel_cpufreq_voltage_check_list(self, package):
        """get kernel opp table check list
        Args:
            package (SysappPackageType): package type
        Returns:
            None:

            cpufreq_vcore_check_list format is:
            [
                [[freq, minV, maxV], ...],      #LD
                [[freq, minV, maxV], ...],      #NOD
                [[freq, minV, maxV], ...]       #OD
            ]
        """
        if package == SysappPackageType.PACKAGE_TYPE_QFN128:
            if not self.case_test_param['dvfs_on']:
                self.case_target_param['cpufreq_vcore_check_list'] = (
                    IFORD_IDAC_QFN_DVFS_VCORE_TABLE[SysappDvfsState.DVFS_STATE_OFF.value])
                self.case_target_param['cpufreq_vcpu_check_list'] = (
                    IFORD_IDAC_QFN_DVFS_VCORE_TABLE[SysappDvfsState.DVFS_STATE_OFF.value])
            else:
                self.case_target_param['cpufreq_vcore_check_list'] = (
                    IFORD_IDAC_QFN_DVFS_VCORE_TABLE[SysappDvfsState.DVFS_STATE_ON.value])
                self.case_target_param['cpufreq_vcpu_check_list'] = (
                    IFORD_IDAC_QFN_DVFS_VCORE_TABLE[SysappDvfsState.DVFS_STATE_ON.value])
        else:
            self.case_target_param['cpufreq_vcore_check_list'] = (
                IFORD_IDAC_VOLT_CORE_TABLE[package.value])
            self.case_target_param['cpufreq_vcpu_check_list'] = (
                IFORD_IDAC_VOLT_CPU_TABLE[package.value])

    def mount_server_path(self):
        """check insmod emac ko, set board ip, mount server path to board
        Args:
            None:
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False

        logger.warning("set board ip and mount server path ...")
        result = SysappNetOpts.setup_network(self.uart)
        if result:
            result = SysappNetOpts.mount_server_path_to_board(self.uart)

        if result:
            logger.info("mount server path success")
        else:
            logger.error("mount server path fail")

        return result

    def _get_base_volt_from_dts(self, dts_file):
        """get base voltage from dts
        Args:
            dts_file (str): the path of dts file
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False
        core_base_volt_ready = 0
        cpu_base_volt_ready = 0
        is_core_power_exist = 0
        is_cpu_power_exist = 0

        with open(dts_file, 'r', encoding='utf-8') as file:
            for line in file:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                line = line.strip()
                if "core_power" in line:
                    core_base_volt_ready = 1
                    is_core_power_exist = 1
                    logger.info("core_power node exist")
                    continue

                if "cpu_power" in line:
                    cpu_base_volt_ready = 1
                    is_cpu_power_exist = 1
                    logger.info("cpu_power node exist")

                if core_base_volt_ready == 1 and "base_voltage" in line:
                    bast_voltage_attr = line.strip().split('=')
                    base_vcore = bast_voltage_attr[1].strip().strip('<>;')
                    self.case_test_param['kernel_base_vcore'] = int(base_vcore, 16)
                    logger.info(f"get core_power:base voltage "
                                      f"{self.case_test_param['kernel_base_vcore']} mv")
                    core_base_volt_ready = 0
                    if (self.case_test_param['package_type'] ==
                            SysappPackageType.PACKAGE_TYPE_QFN128):
                        result = True
                        break
                    if is_core_power_exist == 1 and is_cpu_power_exist == 1:
                        result = True
                        break

                if cpu_base_volt_ready == 1 and "base_voltage" in line:
                    bast_voltage_attr = line.strip().split('=')
                    base_vcpu = bast_voltage_attr[1].strip().strip('<>;')
                    self.case_test_param['kernel_base_vcpu'] = int(base_vcpu, 16)
                    logger.info(f"get cpu_power:base voltage "
                                      f"{self.case_test_param['kernel_base_vcpu']} mv")
                    cpu_base_volt_ready = 0
                    if is_core_power_exist == 1 and is_cpu_power_exist == 1:
                        result = True
                        break

        if not result:
            logger.error("get base voltage fail")

        return result

    def get_kernel_idac_info(self):
        """dump idac info from device
        Args:
            None
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False
        print(f"local_mount_path:{self.local_mount_path}")
        dts_path = f"{self.local_mount_path}/{self.case_test_param['dump_dts_name']}"

        result = SysappDtsOpts.dump_dts_from_memory(self.uart,
                                                    self.case_res_path,
                                                    self.local_mount_path)
        if not result:
            return result

        logger.warning("get kernel base voltage from dts ...")
        result = self._get_base_volt_from_dts(dts_path)
        if not result:
            return result

        logger.warning("get kernel opp table from dts ...")
        self.case_test_param['kernel_opp_table'] = IdacOpts.get_opp_table_from_dts(dts_path)
        return result

    def check_base_voltage(self):
        """check kernel base voltage of vcore & vcpu
        Args:
            None
        Returns:
            result (bool): check success, return True; else, return False.
        """
        result = False
        if self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_QFN128:
            if (self.case_test_param['kernel_base_vcore'] ==
                    self.case_target_param['base_vcore_check']):
                result = True
        else:
            if ((self.case_test_param['kernel_base_vcore'] ==
                 self.case_target_param['base_vcore_check'])
                    and (self.case_target_param['base_vcpu_check'] ==
                         self.case_target_param['base_vcpu_check'])):
                result = True
        if not result:
            logger.error("kernel base voltage is not match with hw base vcore!")
        return result

    def check_opp_table(self):
        """check kernel opp table
        Args:
            None
        Returns:
            result (bool): check success, return True; else, return False
        """
        result = False
        if (not self.case_test_param['dvfs_on']
                and self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_QFN128):
            result = True
        else:
            opp_check_table = (
                IFORD_IDAC_VOLT_CPU_TABLE[self.case_test_param['package_type'].value][
                    SysappOverdriveType.OVERDRIVE_TYPE_OD.value])
            kernel_opp_table = ([sublist[:1] + sublist[2:]
                                 for sublist in self.case_test_param['kernel_opp_table']])
            print(f"{opp_check_table}")
            print(f"{kernel_opp_table}")
            # check if kernel_opp_table contains opp_check_table
            is_subset = all(item in kernel_opp_table for item in opp_check_table)
            if is_subset:
                result = True

        if result:
            logger.info("check kernel opp table ok")
        else:
            logger.error("kernel opp table is not match with check opp table!")
        return result

    def check_avaliable_cpufreq(self, overdrive):
        """check kernel avaliable cpufreq
        Args:
            overdrive (SysappOverdriveType): overdrive type
        Returns:
            result (bool): check success, return True; else, return False
        """
        result = False
        cpufreq_list = []
        self.uart.write(self.case_cmd_param['cmd_cpufreq_available'])
        status, line = self.uart.read()
        if status:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace')
            line = line.strip()
            cpufreq_map = line.strip().split()
            for cpufreq_khz in cpufreq_map:
                cpufreq_hz = int(cpufreq_khz) * 1000
                cpufreq_list.append(cpufreq_hz)

            if cpufreq_list == self.case_target_param[
                    'overdrive_cpufreq_check_list'][
                        overdrive.value]:
                logger.info("check avaliable cpufreq pass")
                result = True
        else:
            logger.error("check avaliable cpufreq fail")
            result = False
        return result

    def check_uboot_voltage(self, overdrive):
        """check uboot voltage under the specified overdrive
        Args:
            overdrive (SysappOverdriveType): overdrive type
        Returns:
            result (bool): check success, return True; else, return False
        """
        result = False
        uboot_volt = {
            'core_power': 0,
            'cpu_power': 0
        }
        uboot_volt_offset = {
            'core_power': 0,
            'cpu_power': 0
        }
        vcore_check_item = []
        vcpu_check_item = []

        result, uboot_volt_offset['core_power'] = self.get_vcore_offset()
        if not result:
            return result
        if self.case_test_param['package_type'] != SysappPackageType.PACKAGE_TYPE_QFN128:
            result, uboot_volt_offset['cpu_power'] = self.get_vcpu_offset()
            if not result:
                return result
        uboot_volt['core_power'] = (self.case_target_param['base_vcore_check']
                                    + uboot_volt_offset['core_power'])
        if self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_QFN128:
            uboot_volt['cpu_power'] = uboot_volt['core_power']
        else:
            uboot_volt['cpu_power'] = (self.case_target_param['base_vcpu_check']
                                       + uboot_volt_offset['cpu_power'])

        vcore_check_item = self.case_target_param['overdrive_vcore_check_list'][overdrive.value]
        vcpu_check_item = self.case_target_param['overdrive_vcpu_check_list'][overdrive.value]

        uboot_vcore_uv = uboot_volt['core_power'] * 1000
        uboot_vcpu_uv = uboot_volt['cpu_power'] * 1000
        logger.info(f"uboot_vcore:{uboot_vcore_uv}, "
                          f"target:[{vcore_check_item[0]}, {vcore_check_item[1]}]")
        logger.info(f"uboot_vcpu:{uboot_vcpu_uv}, "
                          f"target:[{vcpu_check_item[0]}, {vcpu_check_item[1]}]")

        if (self.case_target_param['overdrive_vcore_check_list'][
                overdrive.value][0] <= uboot_vcore_uv <= self.case_target_param[
                    'overdrive_vcore_check_list'][overdrive.value][1]
                        and self.case_target_param['overdrive_vcpu_check_list'][
                            overdrive.value][0] <= uboot_vcpu_uv <= self.case_target_param[
                                'overdrive_vcpu_check_list'][overdrive.value][1]):
            result = True
        else:
            result = False
        return result

    def check_kernel_voltage(self, overdrive, cpufreq):
        """check kernel voltage under the specified overdrive & cpufreq
        Args:
            overdrive (SysappOverdriveType): overdrive type
            cpufreq (int): current cpufreq
        Returns:
            result (bool): check success, return True; else, return False
        """
        result = False
        kernel_volt = {
            'core_power': 0,
            'cpu_power': 0
        }
        kernel_volt_offset = {
            'core_power': 0,
            'cpu_power': 0
        }
        vcore_check_item = []
        vcpu_check_item = []

        result, kernel_volt_offset['core_power'] = self.get_vcore_offset()
        if not result:
            return result
        if self.case_test_param['package_type'] != SysappPackageType.PACKAGE_TYPE_QFN128:
            result, kernel_volt_offset['cpu_power'] = self.get_vcpu_offset()
            if not result:
                return result
        kernel_volt['core_power'] = (self.case_target_param['base_vcore_check']
                                     + kernel_volt_offset['core_power'])
        if self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_QFN128:
            kernel_volt['cpu_power'] = kernel_volt['core_power']
        else:
            kernel_volt['cpu_power'] = (self.case_target_param['base_vcpu_check']
                                        + kernel_volt_offset['cpu_power'])

        for item in self.case_target_param['cpufreq_vcore_check_list'][overdrive.value]:
            if item[0] == cpufreq:
                vcore_check_item = item
                break
        for item in self.case_target_param['cpufreq_vcpu_check_list'][overdrive.value]:
            if item[0] == cpufreq:
                vcpu_check_item = item
                break

        kernel_vcore_uv = kernel_volt['core_power'] * 1000
        kernel_vcpu_uv = kernel_volt['cpu_power'] * 1000
        logger.info(f"kernel_vcore:{kernel_vcore_uv}, freq:{vcore_check_item[0]} "
                          f"target:[{vcore_check_item[1]}, {vcore_check_item[2]}]")
        logger.info(f"kernel_vcpu:{kernel_vcpu_uv}, freq:{vcpu_check_item[0]} "
                          f"target:[{vcpu_check_item[1]}, {vcpu_check_item[2]}]")

        if (vcore_check_item[1] <= kernel_vcore_uv <= vcore_check_item[2] and
                vcpu_check_item[1] <= kernel_vcpu_uv <= vcpu_check_item[2]):
            result = True
        else:
            result = False

        return result

    def set_userspace_governor(self):
        """set power governot to userspace
        Args:
            None
        Returns:
            None
        """
        cmd_userspace_governor = f"echo userspace > {self.case_cmd_param['cmd_governor']}"
        self.uart.write(cmd_userspace_governor)

    def set_cpufreq(self, cpufreq_khz):
        """set current cpufreq to the specified cpufreq
        Args:
            cpufreq_khz (int): the specified cpufreq
        Returns:
            None
        """
        cmd_set_scaling_min_freq = (f"echo {cpufreq_khz} > "
                                    f"{self.case_cmd_param['cmd_scaling_min_freq']}")
        cmd_set_scaling_max_freq = (f"echo {cpufreq_khz} > "
                                    f"{self.case_cmd_param['cmd_scaling_max_freq']}")
        self.uart.write(cmd_set_scaling_min_freq)
        self.uart.write(cmd_set_scaling_max_freq)

    def enable_qfn_dvfs(self):
        """enable dvfs on qfn board
        Args:
            None
        Returns:
            None
        """
        cmd_enable_qfn_dvfs = f"echo 0 > {self.case_cmd_param['cmd_qfn_dvfs']}"
        self.uart.write(cmd_enable_qfn_dvfs)

    def _idac_prepare(self):
        result = False
        # 1. 判断当前设备状态，确保进入kernel
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if not result:
            return result

        # 2. 获取封装类型，确定使用的cpu的overdrive-电压映射表，频率-电压映射表；执行mount操作
        self.case_test_param['package_type'] = SysappDeviceOpts.get_package_type(self.uart)
        logger.warning(f"dev package type is {self.case_test_param['package_type'].name}")
        if self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_MAX:
            logger.error("Unknown package type!")
            result = False
            return result

        # get overdrive-volt check table
        self.get_ipl_volt_check_list(self.case_test_param['package_type'])

        # get overdrive-cpufreq check table
        self.get_kernel_cpufreq_check_list(self.case_test_param['package_type'])

        # get cpufreq-volt_range check table
        self.get_kernel_cpufreq_voltage_check_list(self.case_test_param['package_type'])

        # mount res path to the board
        result = self.mount_server_path()
        if not result:
            return result

        # 3. dump devicetree, 转换成dts，解析base voltage，opp_table信息，保存到case 本地。若解析失败，case结束返回失败。
        result = self.get_kernel_idac_info()
        if not result:
            return result

        # cmp base voltage
        result = self.check_base_voltage()
        if not result:
            return result

        # cmp cpufreq list and volts
        result = self.check_opp_table()
        return result

    def _idac_check_uboot(self, overdrive):
        result = False
        ret = False
        logger.warning(f"reboot to set overdrive to {overdrive.name}")
        result = SysappRebootOpts.reboot_to_uboot(self.uart)
        if not result:
            return result, ret
        cmd_set_overdrive = f"setenv overdrive {overdrive.value};saveenv"
        self.uart.write(cmd_set_overdrive)
        logger.info("reset to uboot for testing ...")
        result = SysappRebootOpts.reboot_to_uboot(self.uart)
        if not result:
            return result, ret

        # 5. 读取寄存器值，判断读取的电压寄存器是否和case保存的table匹配，如果不匹配，
        # 记录LD测试失败，进行下一次的NOD测试。
        logger.warning(f"{overdrive.name}: check uboot voltage")
        ret = self.check_uboot_voltage(overdrive)

        # 6. 执行reset，进到kernel
        logger.info("reset to kernel for testing ...")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        return result, ret

    def _idac_check_kernel(self, overdrive):
        result = False
        ret = False
        ret_dvfs_off = True
        ret_dvfs_on = True
        # 7. 获取支持的cpu频率，对比统计的列表看是否一致，如果不一致，记录LD测试失败，进行下一次的NOD测试
        logger.warning(f"{overdrive.name}: check kernel avaliable cpufreq")
        ret = self.check_avaliable_cpufreq(overdrive)
        if not ret:
            logger.error(f"{overdrive.name} check avaliable cpufreq fail")
            return result, ret

        # 8. 依次设置到各个支持的频率档位，并读取电压寄存器值，先全部读取完毕再观察对应频率读取到的寄存器值
        #    是否和统计列表中的一致，如果不一致，记录LD测试失败，进行下一次的NOD测试
        if self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_QFN128:
            logger.warning(f'{overdrive.name} dvfs_off: check kernel'
                                 ' voltage at different cpufreq')
            self.case_test_param['dvfs_on'] = False
            self.get_kernel_cpufreq_voltage_check_list(self.case_test_param['package_type'])
        else:
            logger.warning(f'{overdrive.name}: check kernel voltage '
                                 'at different cpufreq')
        self.set_userspace_governor()
        for cpufreq in self.case_target_param['overdrive_cpufreq_check_list'][
                overdrive.value]:
            cpufreq_khz = int(cpufreq / 1000)
            self.set_cpufreq(cpufreq_khz)
            ret_dvfs_off = self.check_kernel_voltage(overdrive, cpufreq)
            if not ret_dvfs_off:
                logger.error(f"{overdrive.name} check voltage fail at "
                                   f"cpufreq:{cpufreq}, "
                                   f"dvfs:{self.case_test_param['dvfs_on']}")
                break

        if self.case_test_param['package_type'] == SysappPackageType.PACKAGE_TYPE_QFN128:
            logger.warning(f'{overdrive.name} dvfs_on: check kernel '
                                 'voltage at different cpufreq')
            self.enable_qfn_dvfs()
            self.case_test_param['dvfs_on'] = True
            self.get_kernel_cpufreq_voltage_check_list(self.case_test_param['package_type'])
            for cpufreq in self.case_target_param['overdrive_cpufreq_check_list'][
                    overdrive.value]:
                cpufreq_khz = int(cpufreq / 1000)
                self.set_cpufreq(cpufreq_khz)
                ret_dvfs_on = self.check_kernel_voltage(overdrive, cpufreq)
                if not ret_dvfs_on:
                    logger.error(f"{overdrive.name} check voltage fail at "
                                       f"cpufreq:{cpufreq}, "
                                       f"dvfs:{self.case_test_param['dvfs_on']}")
                    break

        ret = ret_dvfs_off & ret_dvfs_on
        if ret:
            result = True
        return result, ret

    @sysapp_print.print_line_info
    def idac_test(self):
        """run idac test flow
        Args:
            None
        Returns:
            result (bool): test success, return True; else, return False
        """
        result = False
        ret_overdrive = [False, False, False]

        # idac prepare
        result = self._idac_prepare()
        if not result:
            return result

        # 4. 重启设备，等待设备进到uboot，设置 LD 环境，保存再重启。若此阶段出现卡住问题，case结束返回失败。
        for overdrive in SysappOverdriveType:
            if overdrive != SysappOverdriveType.OVERDRIVE_TYPE_MAX:
                result, ret_overdrive[overdrive.value] = self._idac_check_uboot(overdrive)
                if not result:
                    return result

                if not ret_overdrive[overdrive.value]:
                    logger.error(f"{overdrive.name} check uboot voltage fail")
                    continue

                result, ret_overdrive[overdrive.value] = self._idac_check_kernel(overdrive)

        # 9. 汇总LD/NOD/OD的测量结果，返回最后的测试结果，都ok返回成功，否则返回失败
        for overdrive in SysappOverdriveType:
            if overdrive != SysappOverdriveType.OVERDRIVE_TYPE_MAX:
                if not ret_overdrive[overdrive.value]:
                    result = False
                    break

        if result:
            logger.warning("idac test pass!")
        else:
            logger.error("idac test fail!")

        return result

    @sysapp_print.print_line_info
    def runcase(self):
        """test function body
        Args:
            None
        Returns:
            error_code (SysappErrorCodes): result of test
        """
        error_code = SysappErrorCodes.FAIL
        result = False
        result = self.idac_test()

        if result:
            error_code = SysappErrorCodes.SUCCESS

        return error_code

    @sysapp_print.print_line_info
    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("check idac voltage ctrl")
        logger.warning("cmd: idac")
