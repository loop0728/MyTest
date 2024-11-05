"""Conmon Upgrade method."""
from suite.common.sysapp_common_logger import logger

import suite.common.sysapp_common_utils as SysappUtils

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

def start_upgrade(device_handle,upgrade_type):
    """start_upgrade

        Args:
            na
    """
    logger.info("start_upgrade %s",  upgrade_type)

    ret = False
    if upgrade_type == "ufu":
        ret = ufu_upgrade(device_handle)

    elif upgrade_type == "sdstar":
        ret = sdstar_upgrade(device_handle)

    elif upgrade_type == "usbstar":

        ret = usbstar_upgrade(device_handle)

    return ret

def ufu_upgrade(device_handle):
    """ufu_upgrade

        Args:
            na
    """
    logger.info("ufu Start,Waiting Upgrade...")

    write_ret, data = SysappUtils.write_and_match_keyword(device_handle.uart,\
                                        "ufu","[UFU runcmd] reset",True,1000,300)
    if not bool(write_ret):
        logger.error("write fail")
        return False

    #后续补抓emmc的log，现在只抓了NAND和NOR
    try:

        data.index("Erasing NAND...\r\n")

        device_handle.check_boot_storage_type = "NAND"
    except ValueError:
        logger.warning("The Image is not NAND,maybe spinor.")

    try:

        data.index("[UFU runcmd] sf probe 0\r\n")

        device_handle.check_boot_storage_type = "NOR"
    except ValueError:
        if device_handle.check_boot_storage_type != "NAND":
            logger.warning("The Image is not NAND and is not NOR.")
            return False

    try:

        data.index("[UFU runcmd] reset\r\n")

        logger.info("ufu done")
        ret = True
    except ValueError:
        logger.warning("ufu fail")
        ret = False

    return ret

def sdstar_upgrade(device_handle):
    """sdstar_upgrade

        Args:
            na
    """
    logger.info("sdstar Start,Waiting Upgrade...")

    write_ret, data = SysappUtils.write_and_match_keyword(device_handle.uart,\
                                        "sdstar","resetting ...",True,1000,300)
    if not bool(write_ret):
        logger.error("write fail")
        return False


    try:

        data.index("Erasing NAND...\r\n")
        device_handle.check_boot_storage_type = "NAND"
    except ValueError:
        logger.warning("The Image is not NAND,maybe spinor.")

    try:

        data.index(">> sf probe 0 \r\n")
        device_handle.check_boot_storage_type = "NOR"
    except ValueError:
        if device_handle.check_boot_storage_type != "NAND":
            logger.warning("The Image is not NAND and is not NOR.")
            return False

    try:

        data.index("resetting ...\r\n")
        logger.info("sdstar done")
        ret = True
    except ValueError:
        logger.warning("sdstar fail")
        ret = False

    return ret

def usbstar_upgrade(device_handle):
    """usbstar_upgrade

        Args:
            na
    """
    logger.info("usbstar Start,Waiting Upgrade...")

    write_ret, data = SysappUtils.write_and_match_keyword(device_handle.uart,\
                                    "usbstar","[USBSTAR runcmd] reset",True,1000,300)
    if not bool(write_ret):
        logger.error("write fail")
        return False

    try:

        data.index("Erasing NAND...\r\n")
        device_handle.check_boot_storage_type = "NAND"
    except ValueError:
        logger.warning("The Image is not NAND,maybe spinor.")

    try:

        data.index(">> sf probe 0 \r\n")
        device_handle.check_boot_storage_type = "NOR"
    except ValueError:
        if device_handle.check_boot_storage_type != "NAND":
            logger.warning("The Image is not NAND and is not NOR.")
            return False
    try:

        data.index("[USBSTAR runcmd] reset\r\n")
        logger.info("usbstar done")
        ret = True
    except ValueError:
        logger.warning("usbstar fail")
        ret = False

    return ret
