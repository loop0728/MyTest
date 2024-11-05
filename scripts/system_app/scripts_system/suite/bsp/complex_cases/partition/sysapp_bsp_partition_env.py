"""partition dev backup case."""

import re
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
import suite.common.sysapp_common_utils as sys_common
from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts


from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from sysapp_client import SysappClient

class SysappBspPartitionEnv(CaseBase):
    """partition dev backup case."""

    class SysappPartitionInfo:
        """Partition Info."""
        def __init__(self, name, start_addr=0, part_size=0):
            """
            init func

            Args:
                name: part name
                start_addr: part start addr
                part size: part size
            """
            self.name=name
            self.start_addr=start_addr
            self.part_size=part_size

        def do_nothing(self):
            """
            do nothing.

            Args:
                Na
            """
            logger.info(f"{self.name},{self.start_addr},{self.part_size}")

    def __init__(self, case_name,case_run_cnt=1, script_path="./"):
        """
        API test Case.

        Args:
            case_name: case name
            case_run_cnt: case run cnt
            script_path: script_path
            case_stage: case stage
        """
        super().__init__(case_name, case_run_cnt, script_path)
        self.case_name = case_name
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.storage = SysappBspStorage(self.uart)
        self.env_partition_info=[]
        self.dst_addr=["0x21000000","0x22000000"]
        self.header_szie=8

    def get_env_part(self) -> bool:
        """
        get env part info.

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
        # self.partition_info_boot
        splitline=data.splitlines()
        for line in splitline:
            if line.strip():
                if line.strip()[0].isdigit() and "ENV" in line:
                    match=line.strip().split()
                    _,name, size, offset, _ = match
                    # logger.info(name, size, offset)
                    self.env_partition_info.append(self.SysappPartitionInfo(name,offset,size))
        if self.env_partition_info:
            logger.info("get_env_part SUCCESS ")
        else:
            logger.error(f"parse boot partition failed")
            return False
        return True

    def erase_env_by_name(self,env_name) -> bool:
        """
        erase env part by name

        Args:
            env_name(str): env part name,ENV or ENV1
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        result=False

        if self.env_partition_info:
            logger.info("get_env_part SUCCESS ")
        else:
            logger.error(f"get_env_part must be execute first")
            return False

        for backup_part in self.env_partition_info:
            if backup_part.name == env_name:
                print(backup_part.name,backup_part.start_addr,backup_part.part_size)
                ret=SysappRebootOpts.reboot_to_uboot(self.uart)
                if ret is False:
                    logger.error(f"goto_uboot failed")
                    return result
                ret=self.storage.erase(backup_part.name,None)
                if ret is False:
                    logger.error(f"erase {backup_part.name} start:{backup_part.start_addr}"
                        f"size:{backup_part.part_size} failed")
                    return result
        return True

    def save_env(self) -> bool:
        """
        save env

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
        for i in range(len(self.env_partition_info)):
            ret, data=sys_common.write_and_match_keyword(self.uart,"saveenv","SigmaStar #")
            if ret is False:
                logger.error(f"saveenv {i} time failed")
                return ret
            logger.info(f"saveenv {data}")
        return True

    def recovery_scene(self) -> bool:
        """
        recovery scene

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        return self.save_env()

    def read_cmp_env(self) -> bool:
        """
        read and cmp env info

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False

        ret=SysappRebootOpts.reboot_to_uboot(self.uart)
        if ret is False:
            logger.error(f"goto_uboot failed")

        ret=self.save_env()
        if ret is False:
            logger.error(f"save_env failed")
            return ret
        for index, backup_part in enumerate(self.env_partition_info, start=0):
            env_partsize=hex(int(backup_part.part_size,16)-self.header_szie)
            ret=self.storage.read(backup_part.name,"",self.dst_addr[index])
            if ret is False:
                logger.print_error(f"read {backup_part.name} to {self.dst_addr[index]} failed")
                return ret
            self.dst_addr[index]=hex(int(self.dst_addr[index],16)+self.header_szie)

        cmd=f"cmp.b {self.dst_addr[0]} {self.dst_addr[1]} {env_partsize}"
        ret, data=sys_common.write_and_match_keyword(self.uart,cmd,"Total of")
        if ret is False:
            logger.error(f"write_and_match_keyword failed")
            return ret

        match = re.search(r'\b\d+\b', data)
        if match:
            number = int(match.group())
            if int(env_partsize,16) == number:
                logger.info(f"saveenv test success")
                return True
            else:
                logger.warnning(f"ENV1 /ENV is not same")
                return False
        return False

    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """
        ret= False
        result = SysappErrorCodes.FAIL

        ret=self.get_env_part()
        if ret is False:
            logger.error(f"get_env_part failed")
            return result

        ret= self.erase_env_by_name("ENV")
        if ret is False:
            logger.error(f"part:ENV failed")
            return result
        ret=SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"goto_kernel failed")

        ret=self.read_cmp_env()
        if ret is False:
            logger.error(f"goto_kernel failed")
            return result

        ret= self.erase_env_by_name("ENV1")
        if ret is False:
            logger.error(f"part:ENV1 failed")
            return result
        ret=SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"goto_kernel failed")

        self.recovery_scene()
        if ret is False:
            logger.error(f"recovery_scene failed")
            return result
        logger.info(f"recovery scene success")
        ret=SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"goto_kernel failed")
        return SysappErrorCodes.SUCCESS
