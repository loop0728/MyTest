#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""dts operations interfaces"""

from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_net_opts import SysappNetOpts
import suite.common.sysapp_common_utils as SysappUtils

class SysappDtsOpts():
    """
    A class representing devicetree options
    Attributes:
        None:
    """

    @staticmethod
    def _dump_devicetree_blob(device: object, dump_path):
        """dump devicetree files
        Args:
            dump_path (str): destination relative path to dump to
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False
        if device.check_kernel_phase():
            result = SysappNetOpts.dump_files(device, "/sys/firmware/devicetree/base", dump_path)
            if result:
                logger.info("dump devicetree ok")
            else:
                logger.error("dump devicetree fail")
        else:
            logger.error("Dump dts fail, device is not in kernel phase now")

        return result

    @staticmethod
    def _convert_devicetree_blob_to_dts(mount_path):  # need ATP server support mount this dir
        """
        convert dumped devicetree files to dts file
        Args:
            mount_path (str): mount path
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False
        tool = "./dtc"
        cmd_convert_dts = ([tool, '-I', 'fs', '-O', 'dts', 'base', '-o', "fdt.dts"])

        # cd mount path
        result = SysappUtils.change_server_dir(mount_path)
        if not result:
            return result

        # convert to dts
        result, _ = SysappUtils.run_server_cmd(cmd_convert_dts)
        return result

    @classmethod
    def dump_dts_from_memory(cls, device: object, dump_path, local_mount_path):
        """
        Dump dts
        Args:
            device (object): client handle
            dump_path (str): dump path relative to '/mnt'
            local_mount_path (str): the mount path of mount server on ATP server
        Returns:
            result (bool): execute success, return True; else, return False
        """
        result = False
        print(f"local_mount_path:{local_mount_path}")

        logger.warning("begin to dump devicetree blob...")
        result = cls._dump_devicetree_blob(device, dump_path)
        if not result:
            return result

        logger.warning("begin to convert devicetree blob to dts ...")
        result = cls._convert_devicetree_blob_to_dts(local_mount_path)

        return result
