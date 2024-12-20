#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""IDAC test scenarios"""

from PythonScripts.logger import logger
from Common.case_base import CaseBase
from Common.reboot_opts import RebootOpts
import Common.system_common as sys_common
from client import Client

class RebootTest(CaseBase):
    """A class representing reboot test flow
    Attributes:
        uart (Device): device handle
        reboot_opt (RebootOpts): reboot opts instance
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
        self.reboot_opt = RebootOpts(self.uart)
        self.borad_cur_state = ''
        self.cmd_uboot_reset = "reset"
        self.reboot_timeout = 30

    def reboot_test(self):
        """reboot test
        Args:
            None
        Returns:
            result (int): test success, return 0; else, return 255
        """
        result = 255
        result = self.reboot_opt.check_kernel_env()
        if result != 0:
            return result

        logger.print_info("reboot to uboot")
        result = self.reboot_opt.kernel_to_uboot()
        if result != 0:
            return result
        cmd_set_overdrive = "setenv overdrive 2;saveenv"
        self.uart.write(cmd_set_overdrive)
        logger.print_info("reset to uboot for testing ...")
        result = self.reboot_opt.uboot_to_uboot()
        if result != 0:
            return result
        logger.print_info("reset to kernel for testing ...")
        result = self.reboot_opt.uboot_to_kernel()
        if result != 0:
            return result
        logger.print_info("reboot to kernel for testing ...")
        result = self.reboot_opt.kernel_to_kernel()
        if result != 0:
            return result
        return result

    def set_default_bootargs(self):
        """set default bootargs
        Args:
            None
        Returns:
            result (int): test success, return 0; else, return 255
        """
        result = 255
        bootargs = ("ubi.mtd=ubia,2048 root=/dev/ram rdinit=/linuxrc initrd=0x21800000,0x100000 "
                    "rootwait LX_MEM=0x10000000 mma_heap=mma_heap_name0,miu=0,sz=0xb000000 "
                    "mma_memblock_remove=1 cma=2M disable_rtos=1 loglevel=3 "
                    "mtdparts=nand0:1664k@1280k(BOOT),1664k(BOOT_BAK),256k(ENV),5m(KERNEL),"
                    "5m(KERNEL_BACKUP),7m(MISC),7m(RO_FILES),5m(RTOS),5m(RTOS_BACKUP),1m(RAMDISK),"
                    "1m(RAMDISK_BACKUP),89344k(ubia) nohz=off")
        #cmd_set_default_bootargs = (f"setenv bootargs_linux_only {bootargs}")
        sys_common.cold_reboot()
        result = self.reboot_opt.check_uboot_phase()
        if result == 0:
            result = self.reboot_opt.uboot_set_bootenv("bootargs_linux_only", bootargs)
            if result == 0:
                result = self.reboot_opt.uboot_to_kernel()
            else:
                logger.print_error("uboot set str_crc env fail")
        else:
            logger.print_error("the device is not at uboot")
            result = 255

            if result == 0:
                logger.print_info("uboot set_default_bootargs success")
            else:
                logger.print_error("uboot set_default_bootargs fail")
        return result


    @logger.print_line_info
    def runcase(self):
        """test function body
        Args:
            None
        Returns:
            result (int): result of test
        """
        result = 255
        #result = self.reboot_test()
        result = self.set_default_bootargs()

        return result

    @logger.print_line_info
    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.print_warning("test reboot")
        logger.print_warning("cmd: RebootTest")
