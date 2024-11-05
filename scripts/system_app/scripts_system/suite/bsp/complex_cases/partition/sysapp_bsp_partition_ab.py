"""partition AB backup case."""
import time
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
import suite.common.sysapp_common_utils as sys_common
from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from sysapp_client import SysappClient

class SysappBspPartitionAb(CaseBase):
    """partition AB backup case."""

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
    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """
        API test Case.

        Args:
            case_name: case name
            case_run_cnt: case run cnt
            script_path: script_path
            case_stage: case stage
        """
        super().__init__(case_name, case_run_cnt, script_path)
        self.uart = SysappClient(case_name, "uart", "uart")
        self.storage = SysappBspStorage(self.uart)
        self.partition_info_backup=[]
        self.env_partition_info=[]
        self.slot_metadata=[]
        self.slot_number=0
        self.slot_select=0

    def get_boot_part(self) -> bool:
        """
        get boot part info.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        partition_info_boot=[]
        SysappRebootOpts.reboot_to_uboot(self.uart)
        ret, data=sys_common.write_and_match_keyword(self.uart,"mtdparts","SigmaStar #",True,30)
        if ret is False:
            logger.error(f"mtdparts failed")
            return ret
        # self.partition_info_boot
        splitline=data.splitlines()
        for line in splitline:
            if line.strip():
                if line.strip()[0].isdigit():
                    match=line.strip().split()
                    _,name, size, offset, _ = match
                    print(name, size, offset)
                    partition_info_boot.append(self.SysappPartitionInfo(name,offset,size))
        if partition_info_boot:
            logger.info(f"parse boot partition success")
        else:
            logger.error(f"get partition_info_boot failed")
            return False

        for main_part in partition_info_boot:
            for backup in partition_info_boot:
                if main_part.name+"_BAK" == backup.name or main_part.name+"_BACKUP" == backup.name:
                    self.partition_info_backup.append(main_part)
                    backup.name=main_part.name+"_BACKUP"
                    self.partition_info_backup.append(backup)
                    logger.info(f"main:{main_part.name}, back_up:{backup.name}")
        if self.partition_info_backup:
            logger.info(f"get partition_info_backup success")
        else:
            logger.error(f"can not get backup partition")
            return False

        return True


    def erase_part(self,env_name) -> bool:
        """
        erase part by name

        Args:
            env_name(str): env part name,ENV or ENV1
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False
        if self.partition_info_backup == 0:
            logger.error(f"get_boot_part must be execute first")
            return False

        ret=SysappRebootOpts.reboot_to_uboot(self.uart)
        if ret is False:
            logger.error(f"reboot_to_uboot failed")
            return False

        for backup_part in self.partition_info_backup:
            if env_name == "main" and "_BACKUP" not in backup_part.name:
                ret=self.storage.erase(backup_part.name,None)
                if ret is False:
                    logger.error(f"erase {backup_part.name} start:{backup_part.start_addr}, "
                                f"size:{backup_part.part_size} failed")
                    return False
            elif env_name == "backup" and "_BACKUP" in backup_part.name:
                ret=self.storage.erase(backup_part.start_addr,backup_part.part_size)
                if ret is False:
                    logger.error(f"erase {backup_part.name} start:{backup_part.start_addr}, "
                                f"size:{backup_part.part_size} failed")
                    return False

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
        for i in range(2):
            ret, data=sys_common.write_and_match_keyword(self.uart,"saveenv","SigmaStar #")
            if ret is False:
                logger.error(f"saveenv {i} time failed")
                return ret
            logger.info(f" {data} ")
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

    def set_boot_part(self,boot_part) -> bool:
        """
        set boot part

        Args:
            boot_part: boot image source.main or backup
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        if boot_part=="main":
            pori=[0x7f,0x7e]
        elif boot_part=="backup":
            pori=[0x7e,0x7f]

        for index in range(len(self.slot_metadata)):
            self.slot_metadata[index]=pori[index]
            cmd=f"setenv slot_metadata {self.slot_metadata[index]},"
        cmd=f"setenv slot_metadata {hex(self.slot_metadata[0])},{hex(self.slot_metadata[1])}"
        ret, data=sys_common.write_and_match_keyword(self.uart,cmd,"SigmaStar #")
        if ret is False:
            logger.error(f"{cmd} failed")
            return ret
        logger.info(f"{cmd}:{data}")
        ret=self.save_env()
        if ret is False:
            logger.error(f"{cmd} failed")
            return ret
        return True


    def get_slot_info(self) -> bool:
        """
        get slot info

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False
        ret, data=sys_common.write_and_match_keyword(self.uart,"printenv","SigmaStar #",True,100)
        if ret is False:
            logger.error(f"printenv failed")
            return ret
        time.sleep(10)
        splitline=data.splitlines()
        for line in splitline:
            if "slot_number" in line:
                lot_number_find=True
                self.slot_number=int(line.strip().split("=")[1])
                logger.info(f"slot_number:{self.slot_number}")
        if self.slot_number == 0 or lot_number_find is False:
            logger.error(f"must find slot_number first,do not find slot_number!")
            return lot_number_find
        for line in data:
            if "slot_select" in line:
                self.slot_select=line.strip().split("=")[1]
                logger.info(f"slot_select:{self.slot_select}")
            elif "slot_metadata" in line:
                temp=line.strip().split("=")[1]
                for index in range(self.slot_number):
                    self.slot_metadata.append(int(temp.split(",")[index],16))
                    logger.info(f"slot_metadata{index}:{hex(self.slot_metadata[index])}")
        if len(self.slot_metadata) != self.slot_number:
            logger.error(f"can not find slot_metadata!")
            return False

        return True

    def recovery_part(self,boot_part) -> bool:
        """
        recovery part

        Args:
            boot_part: ops boot parttiton.main or backup
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        read_from=None
        write_to=None
        ret=SysappRebootOpts.reboot_to_uboot(self.uart)
        if ret is False:
            logger.error(f"reboot_to_uboot failed")
            return ret

        for main_part in self.partition_info_backup:
            for backup_part in self.partition_info_backup:
                if boot_part=="main" and main_part.name+"_BACKUP" == backup_part.name:
                    print(main_part.name,main_part.start_addr,main_part.part_size)
                    read_from=backup_part
                    write_to=main_part
                elif boot_part=="backup" and main_part.name+"_BACKUP" == backup_part.name:
                    read_from=main_part
                    write_to=backup_part
                else:
                    continue

                ret=self.storage.read(read_from.start_addr,read_from.part_size,"0x21000000")
                if ret is False:
                    logger.error(f"erase {read_from.name} start:{read_from.start_addr} "
                                f"size:{read_from.part_size} failed")
                    return ret

                ret=self.storage.erase(write_to.start_addr,write_to.part_size)
                if ret is False:
                    logger.error(f"erase {write_to.name} start:{write_to.start_addr} "
                                f"size:{write_to.part_size} failed")
                    return ret
                ret=self.storage.write(write_to.start_addr,write_to.part_size,"0x21000000")
                if ret is False:
                    logger.error(f"write {write_to.name} start:{write_to.start_addr},"
                                f"size:{write_to.part_size} failed")
                    return ret
        return True



    def test_part(self,part_name) -> bool:
        """
        test  part

        Args:
            part_name: ops boot parttiton.main or backup
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False
        if part_name == "main":
            erase_part="main"
            recovery_part="backup"
        elif part_name == "backup":
            erase_part="backup"
            recovery_part="main"
        else:
            logger.error(f"do not support {part_name}")
            return False
        ret=self.erase_part(erase_part)
        if ret is False:
            logger.error(f"erase_part failed")
            return ret
        ret=self.set_boot_part(recovery_part)
        if ret is False:
            logger.error(f"set_boot_part failed")
            return ret
        ret=SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"reboot_to_kernel failed")

        ret=self.recovery_part(erase_part)
        if ret is False:
            logger.error(f"recovery_part failed")
            return ret
        return True
    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """
        ret= False
        result = SysappErrorCodes.FAIL
        SysappRebootOpts.init_uboot_env(self.uart)
        ret=self.get_boot_part()
        if ret is False:
            logger.error(f"get_boot_part failed")
            return result
        ret=self.get_slot_info()
        if ret is False:
            logger.error(f"get_slot_info failed")
            return result

        ret=self.test_part("main")
        if ret is False:
            logger.error(f"test_part mian failed")
            return result
        ret=self.test_part("backup")
        if ret is False:
            logger.error(f"test_part backup failed")
            return result
        ret=SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"reboot_to_kernel failed")
            return result
        return SysappErrorCodes.SUCCESS
