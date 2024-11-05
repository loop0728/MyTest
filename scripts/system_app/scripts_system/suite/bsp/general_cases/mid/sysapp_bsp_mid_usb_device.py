"""USB device Mid Class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from suite.common.sysapp_common_logger import sysapp_print
from suite.bsp.general_cases.mid.sysapp_bsp_mid_base import SysappBspMidBase

class SysappBspMidUsbDevice(SysappBspMidBase):
    """ Base class for bsp common case"""

    @staticmethod
    @sysapp_print.print_definition_info
    def cross_system(args):
        """ test function for cross_system. """
        detial_info = ["1.xxx","2.yyy"]

        return 0,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def feature(args):
        """ test function for feature. """
        detial_info = []

        return 0,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def hotplug(args):
        """ test function for hotplug. """
        detial_info = []

        return 0,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def module_loading(args):
        """ test function for module_loading. """
        detial_info = ["1.zzz","2.kkk"]

        return 0,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def reboot(args):
        """ test function for reboot. """
        detial_info = []

        return 0,detial_info

    @staticmethod
    @sysapp_print.print_definition_info
    def str(args):
        """ test function for str. """
        detial_info = []

        return 0,detial_info
