"""emac Mid Class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_net_opts import SysappNetOpts
from suite.bsp.general_cases.mid.sysapp_bsp_mid_base import SysappBspMidBase
from suite.bsp.common.sysapp_bsp_emac import SysappBspEmac
class SysappBspMidEmac(SysappBspMidBase):
    """ Base class for bsp common case"""

    @staticmethod
    @sysapp_print.print_definition_info
    def auto_cross_system(args):
        """ test function for cross_system. """
        detial_info = ["1.xxx","2.yyy"]
        logger.info(args)
        return 1,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def auto_feature(args):
        """ test function for feature. """
        detial_info = []
        ret_mid=255

        ret = True
        cmd=args[2]
        emac=SysappBspEmac(args[0])
        if cmd == "run":
            ret = ret and SysappNetOpts.setup_network(args[0])
            ret = ret and emac.insmod()
            ret = ret and emac.run("forever",True)
            if ret is False:
                logger.error("emac.insmod failed")
                detial_info.append("emac.insmod failed")
                ret_mid=255
            detial_info.append("emac func test success")
            ret_mid=0
        elif cmd == "check_result":
            ret = ret and emac.check_result(None)
            if ret is False:
                logger.error("emac.check_result failed")
                detial_info.append("emac.check_result failed")
                ret_mid=255
            detial_info.append("emac check_result success")
            ret_mid=0
        elif cmd == "exit":
            ret = ret and emac.exit(None)
            if ret is False:
                logger.error("emac.exit failed")
                detial_info.append("emac.exit failed")
                ret_mid=255
            detial_info.append("emac exit success")
            ret_mid=0
        return ret_mid,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def manual_hotplug(args):
        """ test function for hotplug. """
        detial_info = []
        ret_mid=0
        ret = True
        info_mesg = """
                        请完成以下操作后

                        0.拔掉并重新插上网线

                    输入Y/y:
                    """

        emac=SysappBspEmac(args[0])
        ret = ret and SysappNetOpts.setup_network(args[0])
        ret = ret and emac.insmod()
        if ret is False:
            logger.error("emac.insmod failed")
            detial_info.append("emac.insmod failed")
            ret_mid=255
            return ret_mid,detial_info
        user_answer = input(info_mesg)
        while True:
            if(user_answer == "Y" or user_answer == "y"):
                ret=emac.run("forever",True)
                ret = ret and emac.check_result(None)
                ret =ret and emac.exit(None)
                if ret is False:
                    logger.error("emac.run failed")
                    detial_info.append("network is not connect")
                    ret_mid=255
                break
            else:
                user_answer = input("                    输入Y/y:")

        return ret_mid,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def auto_module_loading(args):
        """ test function for module_loading. """
        detial_info = ["1.zzz","2.kkk"]
        logger.info(args)
        return 0,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def auto_reboot(args):
        """ test function for reboot. """
        detial_info = []
        ret_mid=0
        ret = True

        emac=SysappBspEmac(args[0])
        ret = ret and SysappNetOpts.setup_network(args[0])
        ret = ret and emac.insmod()
        ret= ret and emac.run("forever",True)
        ret = ret and emac.check_result(None)
        ret =ret and emac.exit(None)
        if ret is False:
            logger.error("emac.insmod failed")
            detial_info.append("before reboot network is break")
            ret_mid=255
            return ret_mid,detial_info

        detial_info.append("before reboot network is connect")
        ret=SysappRebootOpts.reboot_to_kernel(args[0])
        if ret is False:
            logger.error("reboot_to_kernel failed")
            detial_info.append("reboot_to_kernel failed")
            ret_mid=255
            return ret_mid,detial_info

        ret = ret and SysappNetOpts.setup_network(args[0])
        ret = ret and emac.insmod()
        ret= ret and emac.run("forever",True)
        ret = ret and emac.check_result(None)
        ret =ret and emac.exit(None)
        if ret is False:
            logger.error("emac.insmod failed")
            detial_info.append("after reboot network is break")
            ret_mid=255
            return ret_mid,detial_info
        detial_info.append("after reboot network is connect")
        return ret_mid,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def auto_str(args):
        """ test function for str. """
        detial_info = []
        logger.info(args)
        return 0,detial_info
