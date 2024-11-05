"""nor flash ops"""
from sysapp_client import SysappClient
from suite.common.sysapp_common_logger import logger
# import common.sysapp_common as sys_common
import suite.common.sysapp_common_utils as sys_common
from cases.platform.bsp.common.sysapp_bsp_nor_var import NOR_TOOL_DIR
BLOCK_SIZE = "1024"

class SysappBspNor():
    """Bsp nor flash Case

    Attributes:
            uart_name (str): case uart handle
    """
    def __init__(self, uart_name):
        """
        init func

        Args:
            uart_name: uart name
        """
        if not isinstance(uart_name,SysappClient):
            raise TypeError(f"{uart_name} parameters must be SysappClient ")

        if uart_name.is_open is True:
            self.uart = uart_name
        else:
            raise ValueError("uart_name.is_open must be True ")


    def boot_ops(self,ops,offset,size,dst) -> bool:
        """
        boot_ops nor flash operations in the uboot

        Args:
            ops(str): Operation method selection
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        cmd=None
        check_keyword="SigmaStar #"
        ret=False
        data=None
        ops_nor=["read","write","erase"]

        if ops not in ops_nor:
            logger.error(f"nor flash uboot ops must be one of: {ops_nor}")
            return False
        ret, data=sys_common.write_and_match_keyword(self.uart,"sf probe 0",check_keyword)
        if ret is False:
            logger.error("sf probe 0 failed")
            return ret

        if ops == "erase" :
            cmd=f"sf {ops} {offset} {size}"
            check_keyword="OK"
        elif ops == "read" or ops == "write" :
            cmd=f"sf {ops} {dst} {offset} {size}"
            check_keyword="OK"
        else:
            logger.error(f"{ops} is not support")
            return False
        ret, data=sys_common.write_and_match_keyword(self.uart,cmd,check_keyword,False,999,200)
        if ret is False:
            logger.error(f"{cmd} failed")
            return ret
        logger.info(f"{data}")
        return ret

    def kernel_ops(self,ops,offset,size,dst) -> bool:
        """
        kernel_ops sf flash operations in the kernel

        Args:
            ops(str): Operation method selection
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        # global BLOCK_SIZE
        ops_sf=["read","write","dump","erase"]
        check_keyword="/ #"
        ret=False
        data=None


        if ops not in ops_sf:
            logger.error(f"nor flash kernel ops must be one of: {ops_sf}")
            return False

        if ops == "read" :
            count=int(size,16)//int(BLOCK_SIZE)
            cmd=f"dd if={offset} of={dst} bs={BLOCK_SIZE} count={count}"
            check_keyword="copied"
        elif ops == "write" :
            count=int(size,16)//int(BLOCK_SIZE)
            cmd=f"dd if={dst} of={offset} bs={BLOCK_SIZE} count={count}"
            check_keyword="copied"
        elif ops == "dump" :
            cmd=f"{NOR_TOOL_DIR}/mtd_debug read {offset} 0x0 {size} {dst}"
            check_keyword="/ #"
        elif ops == "erase" :
            cmd=f"flash_eraseall {offset}"
            check_keyword="complete"
        else:
            logger.error(f"{ops} is not support")
            return False
        ret, data=sys_common.write_and_match_keyword(self.uart,cmd,check_keyword,False,999,200)
        if ret is False:
            logger.error(f"{cmd} failed")
            return ret
        logger.info(f"{data}")
        return ret


    def read(self,offset,size,dst) -> bool:
        """
        Nor flash read data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False

        if self.uart.check_kernel_phase():
            ret=self.kernel_ops("read",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret=self.boot_ops("read",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret


    def write(self,offset,size,dst) -> bool:
        """
        Nor flash write data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False

        if self.uart.check_kernel_phase():
            ret=self.kernel_ops("write",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret=self.boot_ops("write",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret


    def dump(self,offset,size,dst) -> bool:
        """
        Nor flash dump data of [size] from [offset] start address [0] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        ret=None

        if self.uart.check_kernel_phase():
            ret=self.kernel_ops("dump",offset,size,dst)
            if ret is False:
                logger.error("dump failed")
        else:
            logger.error("nor flash dump function is supported only under the kernel")
            return False
        return ret

    def erase(self,offset,size) -> bool:
        """
        Nor flash erase data of [size] from start address [offset]

        Args:
            stage(str): Operation method selection
            offset(str): Operation origin address
            size(str): Operation size
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=None

        if self.uart.check_kernel_phase():
            ret=self.kernel_ops("erase",offset,None,None)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret=self.boot_ops("erase",offset,size,None)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret
