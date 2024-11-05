"""partition backup case."""
import os
import re
import time
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
import suite.common.sysapp_common_utils as sys_common
from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts

from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from sysapp_client import SysappClient

class SysappBspPartitionBackup(CaseBase):
    """partition backup case."""

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
        self.case_name = case_name
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.storage = SysappBspStorage(self.uart)
        self.partition_info=[]
        self.partition_info_backup=[]
        self.partition_info_boot=[]



    def get_boot_part(self) -> bool:
        """
        get boot part info.

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
            logger.error(f"write_and_match_keyword failed")
            return ret
        splitline=data.splitlines()
        for line in splitline:
            if line.strip():
                if line.strip()[0].isdigit():
                    match=line.strip().split()
                    _,name, size, offset, _ = match
                    print(name, size, offset)
                    self.partition_info_boot.append(self.SysappPartitionInfo(name,offset,size))
        if self.partition_info_boot:
            logger.info(f"partition_info_boot get  success")
        else:
            logger.error(f"parse boot partition failed")
            return False
        return True


    def add_cis_info_to_bootargs(self) -> bool:
        """
        add cis info to bootargs.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret = False
        ret, bootargs=sys_common.write_and_match_keyword(self.uart,"printenv","SigmaStar #",True)
        if ret is False:
            logger.error(f"printenv failed")
            return ret
        time.sleep(2)
        splitline=bootargs.splitlines()
        for line in splitline:
            if "mtdparts" in line and "bootargs" in line and "1280k@0(CIS)" not in line:
                print(line)
                mtdparts_match = re.search(r'mtdparts=.*?(?=\s)', line)
                if mtdparts_match:
                    mtdparts = mtdparts_match.group()
                    updated_mtdparts = mtdparts + ",1280k@0(CIS)"
                    updated_bootargs = line.replace(mtdparts, updated_mtdparts)
                    logger.info(updated_bootargs)
                    key, value = updated_bootargs.split("=",1)
                    cmd=f"setenv {key} {value}"
                    ret, data=sys_common.write_and_match_keyword(self.uart,cmd,"SigmaStar #")
                    if ret is False:
                        logger.error(f"setenv {key} {value} failed")
                        return ret
                    logger.info(f"{data}")
                    ret, data=sys_common.write_and_match_keyword(self.uart,f"saveenv \n","OK")
                    if ret is False:
                        logger.error(f"saveenv failed")
                        return ret
                    logger.info(f"{data}")
            else:
                logger.info("do not need add 1280k@0(CIS)")
        return True

    def distinguish_backup(self) -> bool:
        """
        distinguish backup

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        names_seen = set()

        for obj in self.partition_info:
            if obj.name in names_seen:
                temp=obj
                self.partition_info_backup.append(temp)
                obj.name += "_BAK"
            else:
                names_seen.add(obj.name)
        if self.partition_info_backup:
            for obj in self.partition_info_backup:
                logger.info(obj.name)
            return True
        else:
            logger.error("distinguish_backup failed")
            return False

    def get_onebin_part_info(self) -> bool:
        """
        get onebin part info.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret, data=sys_common.write_and_match_keyword(self.uart,f"cat proc/mtd","CIS")
        if ret is False:
            logger.error(f"cat proc/mtd failed")
            return ret
        cis_dev=data.split(":",1)[0]
        logger.info(f"cis dev :/dev/{cis_dev}")

        temp_pni_path="/mnt/scripts_system/suite/bsp/complex_cases/partition/test.pni"
        cmd=f"dd if=/dev/{cis_dev} of={temp_pni_path} bs=1 skip=2048 count=2048"
        ret, data=sys_common.write_and_match_keyword(self.uart,cmd,"copied")
        if ret is False:
            logger.error(f"{cmd} failed")
            return ret
        temp_pni_path=os.path.dirname(__file__)+"/test.pni"
        # temp_pni_path="/tmp/test.pni"
        with open(temp_pni_path, "rb") as file:
            file.seek(20,0)
            temp_byte=file.read(4)
            pni_size=int.from_bytes(temp_byte,'little')
            logger.info(f"partnum: {pni_size//32}")
            for i in range(pni_size//32):
                temp_byte=file.read(32)
                part_name=temp_byte[0:15]
                part_start_adddr=temp_byte[20:23]
                part_size=temp_byte[24:27]
                while part_name[-1:] == b'\x00':
                    part_name = part_name[:-1]

                self.partition_info.append(self.SysappPartitionInfo(part_name.decode('utf-8'),
                    hex(int.from_bytes(part_start_adddr,'little')),
                    hex(int.from_bytes(part_size,'little'))))
                logger.info(f"part_name {i}: {part_name}")
        if self.partition_info:
            return self.distinguish_backup()
        else:
            return False

    def get_backup_partition_info(self) -> bool:
        """
        get bckup part info.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret = False
        ret=SysappRebootOpts.reboot_to_uboot(self.uart)

        ret=self.get_boot_part()
        if ret is False:
            logger.error(f"get_boot_part failed")
            return ret
        ret=self.add_cis_info_to_bootargs()
        if ret is False:
            logger.error(f"add_cis_info_to_bootargs failed")
            return ret
        ret = SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"reboot_to_kernel failed")
            return ret

        ret = SysappNetOpts.setup_network(self.uart)

        ret = SysappNetOpts.mount_server_path_to_board(self.uart)
        if ret is False:
            logger.error(f"reboot_to_kernel failed")
            return ret

        ret=self.get_onebin_part_info()
        if ret is False:
            logger.error(f"reboot_to_kernel failed")
            return ret
        return True


    def recovery_scene(self) -> bool:
        """
        recovery scene

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
        for main in self.partition_info_boot:
            for backup in self.partition_info_boot:
                if main.name+"_BAK" == backup.name or main.name+"_BACKUP" == backup.name:
                    print(main.name,backup.name)
                    ret=self.storage.read(main.name,"","0x21000000")

                    ret=self.storage.erase(backup.name,None)

                    ret=self.storage.write(backup.name,"","0x21000000")

                    ret=self.storage.scrub(main.start_addr,"0x20000")
                    if ret is False:
                        logger.error(f"scrub {main.start_addr} failed")
                        return ret
                    ret=self.storage.erase(main.name,None)
                    if ret is False:
                        logger.error(f"erase {main.name} failed")
                        return ret
                    ret=self.storage.write(main.name,"","0x21000000")
                    if ret is False:
                        logger.error(f"write {main.name} from 0x21000000 failed")
                        return ret
        ret = SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"reboot_to_kernel failed")
            return ret
        return True

    def backup_part_test(self) -> bool:
        """
        backup part test.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        if self.partition_info_backup:
            logger.info(f"partition_info_backup is ready")
        else:
            logger.error(f"partition_info_backup is empty")
            return False
        for backup in self.partition_info_backup:
            for main in self.partition_info:
                if backup.name[:len(backup.name)-len("_BAK")] == main.name:
                    print(main.name,main.start_addr,main.part_size)
                    ret=SysappRebootOpts.reboot_to_uboot(self.uart)
                    if ret is False:
                        return ret
                    ret=self.storage.erase(main.start_addr,main.part_size)
                    if ret is False:
                        logger.error(f"erase {main.name} start:{main.start_addr},"
                                    f"size:{main.part_size} failed")
                        return ret
                    ret=SysappRebootOpts.reboot_to_kernel(self.uart)
                    if ret is False:
                        logger.error(f"part:{main.name} start:{main.start_addr},"
                                    f"size:{main.part_size} boot failed")
                        return ret
        logger.info("backup_part_test success")
        return True

    def start_write_back(self) -> bool:
        """
        start write back.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=self.storage.read("0x20000","0x20000","0x21000000")
        if ret is False:
            logger.error(f"read failed")
            return ret
        ret=self.storage.erase("0","0x20000")
        if ret is False:
            logger.error(f"erase failed")
            return ret
        ret=self.storage.write("0","0x20000","0x21000000")
        if ret is False:
            logger.error(f"write failed")
            return ret
        return True

    def bad_block_test_one_part(self,test_part,test_backup) -> bool:
        """
        bad block test one part.

        Args:
            test_part: part to mark bad
            test_backup: read part and write to  test_part
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=self.storage.markbad(test_part.start_addr)
        if ret is False:
            logger.error(f"markbad {test_part.start_addr} failed")
            return ret
        ret=self.storage.erase(test_part.name,None)
        if ret is False:
            logger.error(f"erase {test_part.name} failed")
            return ret
        ret=self.storage.read(test_backup.name,"","0x21000000")
        if ret is False:
            logger.error(f"read {test_backup.name} failed")
            return ret
        ret=self.storage.write(test_part.name,"","0x21000000")
        if ret is False:
            logger.error(f"write {test_part.name} failed")
            return ret
        ret=self.storage.erase(test_backup.name,None)
        if ret is False:
            logger.error(f"erase {test_backup.name} failed")
            return ret
        return True
    def bad_block_test(self) -> bool:
        """
        bad block test.

        Args:
            Na
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        if self.partition_info_boot:
            logger.info(f"partition_info_boot is ready")
        else:
            logger.error(f"partition_info_boot is empty")
            return False

        for main in self.partition_info_boot:
            for backup in self.partition_info_boot:
                if main.name+"_BAK" == backup.name or main.name+"_BACKUP" == backup.name:
                    ret=self.bad_block_test_one_part(main,backup)
                    if ret is False:
                        logger.error(f"bad_block_test_one_part failed")
                        return ret

        #触发回写
        ret=self.start_write_back()
        if ret is False:
            logger.error(f"start_write_back failed")
            return ret

        ret=SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error(f"reboot_to_kernel failed")
            return ret

        logger.info(f"bad block read/write/erase test success")
        return True

    def runcase(self):
        """
        Run case entry.

        Returns:
            int: Error code
        """
        ret= False
        result = SysappErrorCodes.FAIL

        ret=self.get_backup_partition_info()

        if ret is False:
            logger.error(f"get_backup_partition_info failed")
            return result
        # 开始测试 备份分区
        ret=self.backup_part_test()
        if ret is False:
            logger.error(f"backup_part_test failed")
            return result
        # return result
        logger.info(f"parttiton backup test success")
        # # mark bad
        ret=SysappRebootOpts.reboot_to_uboot(self.uart)
        if ret is False:
            logger.error(f"bad_block_test failed")
            return SysappErrorCodes.FAIL

        ret=self.bad_block_test()
        if ret is False:
            logger.error(f"bad_block_test failed")
            return SysappErrorCodes.FAIL

        ret=self.recovery_scene()
        if ret is False:
            logger.error(f"recovery_scene failed")
            return SysappErrorCodes.ESTAR

        logger.info(f"recovery scene success")
        return SysappErrorCodes.SUCCESS
