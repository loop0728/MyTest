#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Utils ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
import suite.common.sysapp_common_utils as SysappUtils
from suite.common.sysapp_common_types import SysappErrorCodes

class SysappUtUtils(CaseBase):
    """
    A class representing utils api test.
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

    def utils_write_read_test(self):
        """
        Write command and read result test.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        logger.warning("test cmd and return single line data ...")
        ret_read_single_line, data = SysappUtils.write_and_match_keyword(self.uart,
                                                                         "ifconfig -a",
                                                                         "TX bytes")
        if ret_read_single_line:
            logger.info(f"read data: {data}")
        else:
            logger.error("not match keyword!")

        logger.warning("test cmd and return all read data ...")
        ret_read_multi_line, data = SysappUtils.write_and_match_keyword(self.uart,
                                                                        "ifconfig -a",
                                                                        "TX bytes",
                                                                        True)
        if ret_read_multi_line:
            logger.info(f"read data: {data}")
        else:
            logger.error("not match keyword!")

        result = (ret_read_single_line and ret_read_multi_line)
        return result

    @staticmethod
    def utils_run_server_cmd_test():
        """
        Run server cmd test.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        cmd_list_files = (['ls', '-l'])
        logger.warning("create files on server ...")
        result, data = SysappUtils.run_server_cmd(cmd_list_files)
        logger.info(f"execute cmd result:{result}, data:{data}")

        cmd_create_dir = (['mkdir', '-p', 'test_run_server_cmd'])
        logger.warning("create directory on server ...")
        result, data = SysappUtils.run_server_cmd(cmd_create_dir)
        logger.info(f"execute cmd result:{result}, data:{data}")

        SysappUtils.change_server_dir('test_run_server_cmd')
        result, data = SysappUtils.run_server_cmd(cmd_list_files)

        cmd_touch_files = (['touch', 'a.c', 'b.c', 'c.c', 'd.c'])
        logger.warning("touch files on server ...")
        result, data = SysappUtils.run_server_cmd(cmd_touch_files)
        logger.info(f"execute cmd result:{result}, data:{data}")
        result, data = SysappUtils.run_server_cmd(cmd_list_files)

        cmd_tar_czf = (['tar', '-czvf', 'test.tar.gz', 'a.c', 'b.c', 'c.c', 'd.c'])
        result, data = SysappUtils.run_server_cmd(cmd_tar_czf)
        logger.info(f"execute cmd result:{result}, data:{data}")
        result, data = SysappUtils.run_server_cmd(cmd_list_files)

        cmd_create_dir = (['mkdir', '-p', 'out'])
        result, data = SysappUtils.run_server_cmd(cmd_create_dir)

        cmd_tar_xzf = (['tar', '-xzvf', 'test.tar.gz', '-C', 'out'])
        result, data = SysappUtils.run_server_cmd(cmd_tar_xzf)
        logger.info(f"execute cmd result:{result}, data:{data}")

        SysappUtils.change_server_dir('out')
        result, data = SysappUtils.run_server_cmd(cmd_list_files)

        cmd_show_ip_link = (['ip', 'link', 'show'])
        result, data = SysappUtils.run_server_cmd(cmd_show_ip_link)
        logger.info(f"execute cmd result:{result}, data:{data}")

        cmd_show_ip_link_in_shell = "ip link show | grep 'brd'"
        result, data = SysappUtils.run_server_cmd(cmd_show_ip_link_in_shell, True)
        logger.info(f"execute cmd result:{result}, data:{data}")

        return result

    def utils_test_insmod_ko(self):
        """
        Insmod/rmmod driver and check the driver loading status.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        ko_path = "/config/modules/5.10/sc4336p_mipi.ko"
        ko_param = "chmap=1 mclk=27M sleep_mode=2"
        result = False
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if not result:
            return result

        result = SysappUtils.check_ko_insmod_status(self.uart, ko_path)
        if result:
            result = SysappUtils.rmmod_ko(self.uart, ko_path)
            if not result:
                return result
        result = SysappUtils.insmod_ko(self.uart, ko_path, ko_param)
        print(f"insmod {ko_path}, result:{result}")

        ko_path = "/config/modules/5.10/usb-common.ko"
        result = SysappUtils.insmod_ko(self.uart, ko_path, "")
        print(f"insmod {ko_path}, result:{result}")

        ko_path = "/config/modules/5.10/usbcore.ko"
        result = SysappUtils.insmod_ko(self.uart, ko_path, "")
        print(f"insmod {ko_path}, result:{result}")

        ko_path = "/config/modules/5.10/sstar-usb2-phy.ko"
        result = SysappUtils.insmod_ko(self.uart, ko_path, "")
        print(f"insmod {ko_path}, result:{result}")

        ko_path = "/config/modules/5.10/ehci-hcd.ko"
        result = SysappUtils.insmod_ko(self.uart, ko_path, "")
        print(f"insmod {ko_path}, result:{result}")

        return result

    def utils_test_file_exist(self):
        """
        Test if the file on server and the file on device exist.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        device_file_path = "/customer/sample_code/bin"
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if not result:
            return result
        result = SysappUtils.check_device_file_exist(self.uart, device_file_path)
        if not result:
            logger.error(f"device_file: {device_file_path} is not exist")
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
        #result = self.utils_write_read_test()
        #result = self.utils_run_server_cmd_test()
        result = self.utils_test_insmod_ko()
        #result &= self.utils_test_file_exist()
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
        logger.warning("test utils api")
