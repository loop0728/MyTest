"""storage case"""
from sysapp_client import SysappClient
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_device_opts import SysappDeviceOpts
from suite.common.sysapp_common_types import SysappBootstrapType
from suite.bsp.common.sysapp_bsp_nand import SysappBspNand
from suite.bsp.common.sysapp_bsp_nor import SysappBspNor
from suite.bsp.common.sysapp_bsp_emmc import SysappBspEmmc


class SysappBspStorage():
    """Bsp Storag Case

    Attributes:
            uart_name (handle): case uart handle
            type: flash type
            handle:flash handle
    """
    def __init__(self, uart_name):
        """
        init func

        Args:
            uart_name: uart name
        """
        self.uart=None
        self.type=None
        self.handle=None
        if not isinstance(uart_name,SysappClient):
            raise TypeError(f"{uart_name} parameters must be SysappClient ")

        if uart_name.is_open is True:
            self.uart = uart_name
        else:
            raise ValueError("uart_name.is_open must be True ")

        self.type = SysappDeviceOpts.get_bootstrap_type(self.uart)
        if self.type == SysappBootstrapType.BOOTSTRAP_TYPE_NAND:
            self.handle=SysappBspNand(self.uart)
        elif self.type == SysappBootstrapType.BOOTSTRAP_TYPE_NOR:
            self.handle=SysappBspNor(self.uart)
        elif self.type == SysappBootstrapType.BOOTSTRAP_TYPE_EMMC:
            self.handle=SysappBspEmmc(self.uart)
        else:
            raise ValueError(f"{self.type} not support")


    def read(self,offset,size,dst) -> bool:
        """
        Nand flash read data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False

        if self.uart.check_kernel_phase():
            ret=self.handle.kernel_ops("read",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret=self.handle.boot_ops("read",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret


    def write(self,offset,size,dst) -> bool:
        """
        Nand flash write data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=False

        if self.uart.check_kernel_phase():
            ret=self.handle.kernel_ops("write",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret=self.handle.boot_ops("write",offset,size,dst)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret


    def dump(self,offset,size,dst) -> bool:
        """
        Nand flash dump data of [size] from start address [offset] to address [dst]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
            dst(str): Operation target address
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        ret=None

        if self.uart.check_kernel_phase():
            ret=self.handle.kernel_ops("dump",offset,size,dst)
            if ret is False:
                logger.error("dump failed")
        elif self.uart.check_uboot_phase():
            ret=self.handle.boot_ops("dump",offset,None,None)
            if ret is False:
                logger.error("dump failed")
        else:
            logger.error("please check board state")
        return ret

    def erase(self,offset,size) -> bool:
        """
        Nand flash erase data of [size] from start address [offset]

        Args:
            offset(str): Operation origin address
            size(str): Operation size
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=None

        if self.uart.check_kernel_phase():
            ret=self.handle.kernel_ops("erase",offset,None,None)
            if ret is False:
                logger.error("erase failed")
        elif self.uart.check_uboot_phase():
            ret=self.handle.boot_ops("erase",offset,size,None)
            if ret is False:
                logger.error("erase failed")
        else:
            logger.error("please check board state")
        return ret

    def markbad(self,offset) -> bool:
        """
        Nand flash mark a block where address [offset] resides as bad block

        Args:
            offset(str): Operation origin address
        Returns:
            bool: The return value. True for success, False otherwise.
        """

        ret=None
        if self.uart.check_uboot_phase():
            ret=self.handle.boot_ops("markbad",offset,None,None)
            if ret is False:
                logger.error("markbad failed")
        else:
            logger.error(f"markbad must enter uboot.")
            return False
        return ret

    def scrub(self,offset,size) -> bool:
        """
        Remove the bad block mark of the block with starting address: [offset], length: [size]
        Args:
            offset(str): Operation origin address
            size(str): Operation size
        Returns:
            bool: The return value. True for success, False otherwise.
        """
        ret=None

        if self.uart.check_uboot_phase():
            ret=self.handle.boot_ops("scrub",offset,size,None)
            if ret is False:
                logger.error("scrub failed")
        else:
            logger.error(f"scrub must enter uboot.")
            return False
        return ret
