#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Reboot ut test"""

from sysapp_client import SysappClient as Client
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_types import SysappErrorCodes

class SysappUtRebootOpts(CaseBase):
    """
    A class representing reboot test flow.
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

    def reboot_test(self):
        """
        Reboot test.
        Args:
            None:
        Returns:
            result (bool): Test success, return True; Else, return False.
        """
        result = False
        result = SysappRebootOpts.init_kernel_env(self.uart)
        if not result:
            return result

        logger.info("reboot to uboot")
        result = SysappRebootOpts.reboot_to_uboot(self.uart)
        if not result:
            return result
        cmd_set_overdrive = "setenv overdrive 2;saveenv"
        self.uart.write(cmd_set_overdrive)
        logger.info("reset to uboot for testing ...")
        result = SysappRebootOpts.reboot_to_uboot(self.uart)
        if not result:
            return result
        logger.info("reset to kernel for testing ...")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if not result:
            return result
        logger.info("reboot to kernel for testing ...")
        result = SysappRebootOpts.reboot_to_kernel(self.uart)

        return result

    def set_default_bootargs(self):
        """
        Set default bootargs.
        Args:
            None:
        Returns:
            result (bool): test success, return True; else, return False.
        """
        result = False
        bootargs = ("ubi.mtd=ubia,2048 root=/dev/ram rdinit=/linuxrc initrd=0x21800000,0x100000 "
                    "rootwait LX_MEM=0x10000000 mma_heap=mma_heap_name0,miu=0,sz=0xb000000 "
                    "mma_memblock_remove=1 cma=2M disable_rtos=1 loglevel=3 "
                    "mtdparts=nand0:1664k@1280k(BOOT),1664k(BOOT_BAK),256k(ENV),5m(KERNEL),"
                    "5m(KERNEL_BACKUP),7m(MISC),7m(RO_FILES),5m(RTOS),5m(RTOS_BACKUP),"
                    "1m(RAMDISK),1m(RAMDISK_BACKUP),89344k(ubia) nohz=off")
        # bootargs = ("ubi.mtd=ubia,2048 root=/dev/ram rdinit=/linuxrc initrd=0x21800000,0x100000 "
        #             "rootwait LX_MEM=0x8000000 mma_heap=mma_heap_name0,miu=0,sz=0x5000000 "
        #             "mma_memblock_remove=1 cma=2M disable_rtos=1 loglevel=3 "
        #             "mtdparts=nand0:1664k@1280k(BOOT),1664k(BOOT_BAK),256k(ENV),256k(ENV1),"
        #             "5m(KERNEL),5m(KERNEL_BACKUP),7m(MISC),7m(RO_FILES),5m(RTOS),5m(RTOS_BACKUP),"
        #             "1m(RAMDISK),1m(RAMDISK_BACKUP),87m(ubia) nohz=off")
        #cmd_set_default_bootargs = (f"setenv bootargs_linux_only {bootargs}")
        result = SysappRebootOpts.cold_reboot_to_uboot(self.uart)
        if result:
            result = SysappRebootOpts.set_bootenv(self.uart, "bootargs_linux_only", bootargs)
            if result:
                result = SysappRebootOpts.reboot_to_kernel(self.uart)
            else:
                logger.error("uboot set str_crc env fail")
        else:
            logger.error("the device is not at uboot")
            result = False

        if result:
            logger.info("set_default_bootargs success")
        else:
            logger.error("set_default_bootargs fail")
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
        result = self.reboot_test()
        #result = self.set_default_bootargs()
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
        logger.warning("test reboot")
        logger.warning("cmd: RebootTest")
