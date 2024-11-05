"""emmc flash ops"""
from sysapp_client import SysappClient
from suite.common.sysapp_common_logger import logger
import suite.common.sysapp_common_utils as sys_common
from cases.platform.bsp.common.sysapp_bsp_emmc_var import BLOCK_SIZE, EMMC_RESOURCE_DIR


class SysappBspEmmc():
    """Bsp Emmc flash Base

    Attributes:
            uart_name (str): case uart handle
    """
    def __init__(self, uart_name):
        """
        init func

        Args:
            uart_name: uart name
        """
        if not isinstance(uart_name, SysappClient):
            raise TypeError(f"{uart_name} parameters must be SysappClient ")

        if uart_name.is_open is True:
            self.uart = uart_name
        else:
            raise ValueError("uart_name.is_open must be True ")

    def boot_ops(self, ops, offset, size, dst) -> bool:
        """
        boot_ops emmc flash operations in the uboot

        Args:
            ops(str): Operation method selection
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        cmd = None
        check_keyword = "eMMC"
        ret = False
        data = None
        number_emmc_dev = 0
        start_blk = 0
        count_blk = 0
        # Find the mmc dev where emmc is located
        ret, data = sys_common.write_and_match_keyword(self.uart, "mmc list", check_keyword)
        if ret is True:
            number_emmc_dev = data.split(':')[1].split()[0]
            check_keyword = f"mmc{number_emmc_dev}(part 0) is current device"
            ret, data = sys_common.write_and_match_keyword(
                self.uart, f"mmc dev {number_emmc_dev} 0", check_keyword, False, 10)
            if ret is False:
                logger.error(f"mmc dev {number_emmc_dev} 0 cmd fail")
                return False
            logger.info("emmc dev check ok")
        else:
            logger.error("cmd mmc list fail")
            return False

        if ops == "erase":
            if offset[0].isdigit():
                start_blk = int(offset[0]) // int(BLOCK_SIZE)
                count_blk = int(size) // int(BLOCK_SIZE)
                cmd = f"mmc erase {start_blk} {count_blk}"
                check_keyword = "OK"
            else:
                cmd = f"emmc remove {offset}"
                check_keyword = "success"

        elif ops == "read" or ops == "dump":
            cmd = f"emmc {ops}.p.continue {dst} {offset} {size}"
            check_keyword = "OK"
        elif ops == "write":
            cmd = f"emmc write.p.continue {dst} {offset} {size}"
            check_keyword = "success"
        elif ops == "create":
            cmd = f"emmc create {offset} {size}"
            check_keyword = "success"
        else:
            logger.error(f"{ops} is not support")
            return False

        ret, data = sys_common.write_and_match_keyword(
            self.uart, cmd, check_keyword, False, 100, 15)
        if ret is False:
            logger.error(f"cmd is {cmd} fail,data is {data}")
        return True

    def kernel_ops(self, ops, offset, size, dst) -> bool:
        """
        kernel_ops emmc flash operations in the kernel

        Args:
            ops(str): Operation method selection
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        ops_emmc = ["read", "write", "dump", "erase"]
        check_keyword = "/ #"
        cmd_run_on_board = ""
        ret = False
        data = None

        if ops not in ops_emmc:
            logger.error(f"emmc flash kernel ops must be one of: {ops_emmc}")
            return False
        if ops == "read" or ops == "dump":
            count = int(size, 16) // int(BLOCK_SIZE)
            cmd = f"dd if={offset} of={dst} bs={BLOCK_SIZE} count={count}"
            check_keyword = "copied"
        elif ops == "write":
            count = int(size, 16) // int(BLOCK_SIZE)
            cmd = f"dd if={dst} of={offset} bs={BLOCK_SIZE} count={BLOCK_SIZE}"
            check_keyword = "copied"
        elif ops == "erase":
            count = int(size, 16) // int(BLOCK_SIZE)
            cmd_run_on_board = (f'dd if=/dev/zero bs={BLOCK_SIZE} '
                                f'count={count} | tr "\0" "\xFF" > '
                                f'{EMMC_RESOURCE_DIR["board_dir_for_server"]}/erase.bin')
            ret = sys_common.run_server_cmd(cmd_run_on_board)
            if ret is False:
                logger.error(f"{cmd_run_on_board} failed to execute")
                return False
            cmd = (f"dd if={EMMC_RESOURCE_DIR['board_dir_for_board']}/erase.bin of={offset} "
                   f"bs={BLOCK_SIZE} count={count}")
            check_keyword = "complete"
        else:
            logger.error(f"{ops} is not support")
            return False

        ret, data = sys_common.write_and_match_keyword(self.uart, cmd, check_keyword, False, 30, 20)
        if ret is False:
            logger.error(f"{cmd} failed,data is {data}")
            return False
        return True

    def read(self, offset, size, dst) -> bool:
        """
        emmc flash read data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret = False

        if self.uart.check_kernel_phase():
            ret = self.kernel_ops("read", offset, size, dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret = self.boot_ops("read", offset, size, dst)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret

    def write(self, offset, size, dst) -> bool:
        """
        emmc flash write data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret = False
        if self.uart.check_kernel_phase():
            ret = self.kernel_ops("write", offset, size, dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret = self.boot_ops("write", offset, size, dst)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret

    def dump(self, offset, size, dst) -> bool:
        """
        emmc flash dump data of [size] from [offset] start address [0] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        ret = None
        if self.uart.check_kernel_phase():
            ret = self.kernel_ops("dump", offset, size, dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret = self.boot_ops("dump", offset, None, None)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret

    def erase(self, offset, size) -> bool:
        """
        emmc flash erase data of [size] from start address [offset]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        ret = None

        if self.uart.check_kernel_phase():
            ret = self.kernel_ops("erase", offset, None, None)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret = self.boot_ops("erase", offset, size, None)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret
