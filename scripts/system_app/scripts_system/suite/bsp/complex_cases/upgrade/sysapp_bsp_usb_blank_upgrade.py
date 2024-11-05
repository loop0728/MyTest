"""USB Blank Upgrade case."""

import time
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase
from suite.common.sysapp_common_types import SysappErrorCodes
import suite.common.sysapp_common_utils as sys_common
import suite.bsp.complex_cases.autok.sysapp_bsp_autok_base as autok_base
from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
import sysapp_bsp_upgrade_common as upgrade_common
from sysapp_client import SysappClient

class SysappBspUsbBlankUpgrade(SysappCaseBase):
    """Case for USB Blank Upgrade ."""

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
        super().__init__(case_name, case_run_cnt, script_path)
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.check_boot_storage_type = "none"
        self.storage = SysappBspStorage(self.uart)
        self.env_partition_info=[]
        self.autok_base = autok_base.SysappBspAutokBase(self.uart)
    def get_boot_storage_type(self):
        """get_boot_storage_type

        Args:
            na
        """
        return self.check_boot_storage_type

    def get_all_part(self) -> bool:
        """
        get all part info.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret = False
        ret=SysappRebootOpts.reboot_to_uboot(self.uart)
        if ret is False:
            logger.error(f"goto_uboot failed")
            return ret
        ret, data=sys_common.write_and_match_keyword(self.uart,"mtdparts","SigmaStar #",True)
        if ret is False:
            logger.error(f"mtdparts failed")
            return ret
        #后续补emmc获取分区
        # self.partition_info_boot
        splitline=data.splitlines()
        for line in splitline:
            if line.strip():
                if line.strip()[0].isdigit():
                    match=line.strip().split()
                    _,name, size, offset, _ = match
                    # print(name, size, offset)
                    self.env_partition_info.append(upgrade_common.SysappPartitionInfo(name,\
                                                                            offset,size))
        return True

    @staticmethod
    def notice_prepare_hw():
        """notice_prepare_hw

        Args:
            na
        """
        info_mesg = """
                        二、请完成以下操作后

                        1.关闭板子电源
                        2:板子启动拨码开关拨到USB2.0
                        3:PC打开USB_Factory_Tool，选择模式：auto，并选择USB升级固件
                        4:板子USB口连接PC
                        5:打开板子电源上电,观察出现大容量存储设备
                        6:USB_Factory_Tool点击烧录按钮
                        7:显示step:"引导"，progress："100%",result:√.
                        8.如一直引导，选择N
                    输入Y：
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
                        三、请完成以下操作后

                        1.关闭PC的USB_Factory_Tool
                        2:关闭板子电源
                        3:板子启动拨码开关拨到{boot_type}
                        4:打开板子电源
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

    def start_usb_blank_upgrade(self):
        """start_usb_blank_upgrade

        Args:
            na
        """
        ret = True
        #in uboot?
        ret = self.is_in_uboot()

        if ret is False:
            logger.error(f"{self.uart} [usb_blank_upgrade]:I'm not in the special uboot")
            return ret
        else:
            logger.info("[usb_blank_upgrade]:I'm in the special uboot")

        #autok?
        ret = self.autok_alived()
        if ret is False:
            logger.error(f"{self.uart} [usb_blank_upgrade]:autok not alived")
            return ret
        else:
            logger.info("[usb_blank_upgrade]:autok  alive")

        #ufu
        ret = upgrade_common.start_upgrade(self,"ufu")
        if ret is False:
            logger.error(f"{self.uart} [usb_blank_upgrade]:Upgrade ERR")
            return ret
        else:
            logger.info("[usb_blank_upgrade]:Upgrade Success")

        time.sleep(10)

        #ufu after in uboot?
        ret = self.is_in_uboot()
        if ret is False:
            logger.perror(f"{self.uart} [usb_blank_upgrade]:ufu after not in uboot")
            return ret
        else:
            logger.info("[usb_blank_upgrade]:ufu after in uboot")

        return ret

    def autok_alived(self):
        """autok_alived

        Args:
            na
        """

        ret = self.autok_base.judge_ubootreg_ott_mode(self.autok_base.SysappOttMode.RUN_AUTOK)

        return ret

    def erase_flash_all(self):
        """erase_flash_all

        Args:
            na
        """
        time.sleep(10)

        ret = self.get_all_part()
        if ret is False:
            logger.info("Board is not blank,but get partition fail")
        else:
            logger.info("Current partitions:")
            index = 0
            while index < len(self.env_partition_info):
                print(self.env_partition_info[index].name,\
                      self.env_partition_info[index].start_addr,\
                      self.env_partition_info[index].part_size)
                index+=1

            index = 0
            while index < len(self.env_partition_info):
                logger.info("earsing partition :%s",self.env_partition_info[index].name)
                ret = self.storage.erase(self.env_partition_info[index].name,\
                                         self.env_partition_info[index].part_size)
                if ret is False:
                    logger.info("earse partition %s failed",self.env_partition_info[index].name)
                    break
                index+=1
        return ret

    @staticmethod
    def tell_is_blank():
        """tell_is_blank

        Args:
            na
        """
        is_blank = True
        info_mesg = """
                        一、请告知当前板子是否为空片
                    如是空片输入Y
                    如不是空片打开板子电源后输入N：
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
        ret = False

        logger.info("Testing USB Blank Uprade case.")

        if not self.tell_is_blank():
            ret = self.erase_flash_all()
            if ret is False:
                return SysappErrorCodes.FAIL

        if self.notice_prepare_hw():

            logger.info(f"{self.uart} booting...")
            #for time to boot in special uboot
            time.sleep(10)

            #ufu upgrade，after in uboot?
            ret = self.start_usb_blank_upgrade()
            if ret is False:
                logger.error(f"{self.uart} start_usb_blank_upgrade err!")
                return SysappErrorCodes.FAIL

            #change bootstrap for boot strorage
            ret = self.notice_change_bootstrap()
            if ret is False:
                logger.error(f"{self.uart} bootstrap err!")
                return SysappErrorCodes.FAIL

            logger.info(f"{self.uart} booting...")

            time.sleep(20)

            #in kernel?
            ret = self.is_in_kernel()
            if ret is False:
                logger.error(f"{self.uart} After ufu and change bootstrap ,\
                                            then reboot not in kernel.")
                return SysappErrorCodes.FAIL
        else:
            logger.error(f"{self.uart} HW not ready.")
            return SysappErrorCodes.FAIL

        logger.info("Testing USB Blank Uprade case finish!")

        return SysappErrorCodes.SUCCESS

    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("Test for USB Blank Upgrade Normal Image.")
