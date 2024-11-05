#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Device ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_types import SysappPackageType, SysappBootstrapType
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_device_opts import SysappDeviceOpts
from suite.common.sysapp_common_types import SysappErrorCodes

class SysappUtDeviceOpts(CaseBase):
    """
    A class representing device test flow.
    Attributes:
        uart (Client): Clinet instance.
    """
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        """Class constructor.
        Args:
            case_name (str): case name.
            case_run_cnt (int): the number of times the test case runs.
            module_path_name (str): moudle path.
        """
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    def device_opts_test(self):
        """
        Register test.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        package_type = SysappPackageType.PACKAGE_TYPE_MAX
        bootstrap_type = SysappBootstrapType.BOOTSTRAP_TYPE_MAX
        partition_list = []
        result = SysappRebootOpts.init_uboot_env(self.uart)
        if not result:
            return result

        result = SysappDeviceOpts.is_trimed_ic(self.uart)
        logger.warning(f"uboot test:Is the chip trimed? [{result}]")

        logger.info("test get package type at uboot phase ...")
        package_type = SysappDeviceOpts.get_package_type(self.uart)
        logger.warning(f"The package type is {package_type.name}")

        logger.info("test write register at uboot phase ...")
        bootstrap_type = SysappDeviceOpts.get_bootstrap_type(self.uart)
        logger.warning(f"The bootstrap type is {bootstrap_type.name}")

        logger.info("test get partitions at uboot phase ...")
        result, partition_list = SysappDeviceOpts.get_partition_list(self.uart)
        if result:
            logger.warning(f"get partitons: {partition_list}")
        else:
            logger.error("get partitons fail at uboot phase")

        logger.info("test get package type at kernel phase ...")
        logger.info("reboot to kernel")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            return result

        result = SysappDeviceOpts.is_trimed_ic(self.uart)
        logger.warning(f"kernel test:Is the chip trimed? [{result}]")

        package_type = SysappDeviceOpts.get_package_type(self.uart)
        logger.warning(f"The package type is {package_type.name}")

        logger.info("test write register at kernel phase ...")
        bootstrap_type = SysappDeviceOpts.get_bootstrap_type(self.uart)
        logger.warning(f"The bootstrap type is {bootstrap_type.name}")

        logger.info("test get partitions at kernel phase ...")
        result, partition_list = SysappDeviceOpts.get_partition_list(self.uart)
        if result:
            logger.warning(f"get partitons: {partition_list}")
        else:
            logger.error("get partitons fail at kernel phase")

        return result

    @sysapp_print.print_line_info
    def runcase(self):
        """
        Test function body.
        Args:
            None:
        Returns:
            error_code (SysappErrorCodes): Result of test.
        """
        error_code = SysappErrorCodes.FAIL
        result = self.device_opts_test()
        if result:
            error_code = SysappErrorCodes.SUCCESS

        return error_code

    @sysapp_print.print_line_info
    @staticmethod
    def system_help():
        """
        Help info.
        Args:
            None:
        Returns:
            None:
        """
        logger.warning("test device opts")
        logger.warning("cmd: DeveiceOptsTest")
