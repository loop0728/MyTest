"""emac Mid Class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from suite.common.sysapp_common_logger import sysapp_print
from suite.bsp.general_cases.mid.sysapp_bsp_mid_base import SysappBspMidBase

class SysappBspMidEmac(SysappBspMidBase):
    """ Base class for bsp common case"""

    @staticmethod
    @sysapp_print.print_definition_info
    def cross_system(args):
        """ test function for cross_system. """
        pass

    @staticmethod
    @sysapp_print.print_definition_info
    def feature(args):
        """ test function for feature. """
        pass

    @staticmethod
    @sysapp_print.print_definition_info
    def hotplug(args):
        """ test function for hotplug. """
        pass

    @staticmethod
    @sysapp_print.print_definition_info
    def module_loading(args):
        """ test function for module_loading. """
        pass

    @staticmethod
    @sysapp_print.print_definition_info
    def reboot(args):
        """ test function for reboot. """
        pass

    @staticmethod
    @sysapp_print.print_definition_info
    def str(args):
        """ test function for str. """
        pass
