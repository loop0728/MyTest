"""Common Class for aov case."""
import os
import time
from suite.common.sysapp_common_logger import logger
import suite.common.sysapp_common_utils as SysappUtils
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts

class SysappAovCommon():
    """
    AOV case

    Attributes:
        name: case name
    """
    def __init__(self, name):
        """
        init func

        Args:
            name: AOV case name
        """
        self.name = name

    @staticmethod
    def save_time_info(name, info) -> int:
        """
        Save time info to "out/case_name/time.txt".

        Args:
            name (str): AOV case name
            info (str): test time infomation

        Returns:
            int: result
        """
        file = None
        result = 0
        file_path = f"out/{name}/time.txt"

        try:
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(info)

        except FileNotFoundError:
            result = 255
        except PermissionError:
            result = 255

        return result

    @staticmethod
    def get_ko_insmod_state(uart: object, koname=''):
        """ get_ko_insmod_state
            uart (object): client handle
            koname (str): mi_sys
        """
        result = ""
        cmd = f"lsmod | grep {koname} | wc -l"
        res = uart.write(cmd)
        if res is False:
            logger.error(f"{uart} is disconnected.")
            return "Unknown"
        wait_keyword = "0"
        status, data = uart.read()
        if status  is True:
            if wait_keyword in data:
                result = "none"
            else:
                result = "insmod"
        else:
            result = "Unknown"
        return result

    @classmethod
    def check_insmod_ko(cls, uart: object, koname=''):
        """ check_insmod_ko
            uart (object): client handle
            koname (str): mi_sys
        """
        wait_keyword = "none"
        ko_path = f"/config/modules/5.10/{koname}.ko"
        data = cls.get_ko_insmod_state(uart, f"{koname}")
        if wait_keyword in data:
            cmd = f"insmod {ko_path}"
            logger.warning(f"we will {cmd}")
            uart.write(cmd)
            result = "true"
        else:
            logger.warning(f"we no need insmod {koname}")
            result = "false"
        return result

    @classmethod
    def get_current_os(cls, uart: object):
        """ get_current_os
            uart (object): client handle
        """
        wait_keyword = "none"
        data = cls.get_ko_insmod_state(uart, "mi_sys")
        if wait_keyword in data:
            result = "dualos"
        else:
            result = "purelinux"
        return result

    @classmethod
    # used by aov scenarios
    def switch_os_aov(cls, uart: object, target_os=''):
        """ switch_os by aov pipe case
            uart (object): client handle
            target_os (str): purelinux or dualos
        """
        result = 0
        cur_os = cls.get_current_os(uart)
        if cur_os == target_os:
            logger.warning(f"current os is match {target_os}")
            return 0

        logger.warning(f"will switch to OS({target_os})!")
        if target_os == "dualos":
            cmd = "cd /customer/sample_code/bin/"
            uart.write(cmd)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = uart.read()
            if status is True:
                if wait_keyword not in data:
                    return 255
            else:
                logger.error(f"Read fail,no keyword: {wait_keyword}")
                return 255
            cmd = "./prog_aov_aov_demo -t"
            uart.write(cmd)
            time.sleep(10)
            cmd = "c"
            uart.write(cmd)

        if target_os == "purelinux":
            cmd = "cd /customer/sample_code/bin/"
            uart.write(cmd)
            time.sleep(1)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = uart.read()
            if status is True:
                if wait_keyword not in data:
                    result = 255
                    return result

            cmd = "./prog_preload_linux -t"
            wait_keyword = "press c to change mode"
            result, data = SysappUtils.write_and_match_keyword(uart, cmd, wait_keyword)
            if result is False:
                return 255

            cmd = "c"
            uart.write(cmd)

        time.sleep(20)
        return result

    @classmethod
    def switch_os_common(cls, uart: object, target_os=''):
        """ switch_os by common
            uart (object): client handle
            target_os (str): purelinux or dualos
        """
        oscode = 0
        cur_os = cls.get_current_os(uart)
        if cur_os == target_os:
            logger.warning(f"current os is match {target_os}")
            return 0
        if target_os == "dualos":
            oscode = 1
        if target_os == "purelinux":
            oscode = 3
        cmd = f"echo {oscode} > /sys/class/sstar/rtcpwc/save_in_sw3"
        uart.write(cmd)
        time.sleep(3)
        result = SysappRebootOpts.reboot_to_kernel(uart)
        time.sleep(20)
        return result
