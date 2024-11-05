"""Uart Blank  Upgrade case."""
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from sysapp_client import SysappClient
import sysapp_common as sys_common
import sysapp_bsp_upgrade_common as upgrade_common




class SysappBspUartBlankUpgrade(SysappCaseBase):
    """Case for Uart Blank Upgrade ."""

    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """
        API test Case.

        Args:
            case_name: case name
            case_run_cnt: case run cnt
            script_path: script_path
            case_stage: case stage
        """
        self.case_name = case_name
        self.case_run_cnt = case_run_cnt
        self.script_path = script_path
        super().__init__(case_name, case_run_cnt, script_path)
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.check_boot_storage_type = "none"

    def get_boot_storage_type(self):
        """get_boot_storage_type

        Args:
            na
        """
        return self.check_boot_storage_type

    @staticmethod
    def notice_prepare_hw():
        """notice_prepare_hw

        Args:
            na
        """
        info_mesg = """
                    接下来的步骤请参考wiki:http://sswiki.sigmastar.com.tw:8090/pages/viewpage.action?pageId=72954507


                    如测试成功请按Y，否则N：
                    """

        user_answer = input(info_mesg)
        if(user_answer == "Y" or user_answer == "y"):
            done = 1
        else:
            done = 0
        return done

    def notice_change_bootstrap(self):
        """notice_change_bootstrap

        Args:
            na
        """
        boot_type = self.get_boot_storage_type()
        info_mesg = f"""
                        请完成以下操作后

                        1:关闭板子电源
                        2:板子启动拨码开关拨到{boot_type}
                        3.拔除U盘
                        3:打开板子电源
                    输入Y：
                    """

        user_answer = input(info_mesg)
        if(user_answer == "Y" or user_answer == "y"):
            done = True
        else:
            done = False

        return done

    def is_in_uboot(self):
        """is_in_uboot

        Args:
            na
        """
        state = self.uart.check_uboot_phase()

        return  state

    def is_in_kernel(self):
        """is_in_kernel

        Args:
            na
        """
        stage = self.uart.check_kernel_phase()

        return  stage

    def start_usb_storage_upgrade(self):
        """start_usb_storage_upgrade

        Args:
            na
        """
        ret = True
        #in uboot?
        ret = self.is_in_uboot()

        if ret is False:
            logger.warning(f"{self.uart} [usb_storage_upgrade]:I'm not in the  uboot,\
                                            reboot to uboot...")
            go_uboot_ret = SysappRebootOpts.reboot_to_uboot(self.uart)
            if go_uboot_ret is False:
                logger.error(f"{self.uart} [usb_storage_upgrade]:Can't goto uboot,Wrong image!")
                return ret
        else:
            logger.info("[usb_storage_upgrade]:I'm already in the uboot")

        #has usbstar cmd?
        ss_input = "?"
        keyword = "usbstar   - script via USB package"
        wait_line = 1000
        result, _ = sys_common.write_and_match_keyword(self.uart, ss_input, keyword, wait_line)
        if result is False:
            logger.error("The uboot has no usbstar cmd,.")
            return False

        #usbstar
        ret = upgrade_common.start_upgrade(self,"usbstar")
        if ret is False:
            logger.error(f"{self.uart} [usb_storage_upgrade]:Upgrade ERR")
            return ret
        else:
            logger.info("[usb_storage_upgrade]:Upgrade Success")

        return ret

    @staticmethod
    def erase_flash_all():
        """erase_flash_all

        Args:
            na
        """
        return

    @staticmethod
    def tell_is_blank():
        """tell_is_blank

        Args:
            na
        """
        is_blank = True
        info_mesg = """
                        一、请告知当前板子是否为空片
                    如是输入Y，否输入N：
                    """

        user_answer = input(info_mesg)
        if(user_answer == "Y" or user_answer == "y"):
            is_blank = True
        else:
            is_blank = False

        return is_blank

    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """

        logger.info("Testing Uart Blank Uprade case.")


        if self.notice_prepare_hw():

            logger.info(f"{self.uart}SUCCESS！")

        else:
            logger.error(f"{self.uart} Testing Uart Blank Uprade case fail.")
            return SysappErrorCodes.FAIL

        logger.info("Testing Uart Blank Uprade case finish!")

        return SysappErrorCodes.SUCCESS

    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("Test for Uart_Burn_Tool boot.")
