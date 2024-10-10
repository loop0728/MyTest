""" case base for Bsp Mid """
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import importlib
import os
from suite.common.sysapp_common_logger import sysapp_print

class SysappBspGeneralCaseBase:
    """ Base class for bsp general case """

    @sysapp_print.print_line_info
    def __import_bsp_mid_modinfo_init__(self, directory_path):
        """ module info init func.

        Args:
            directory_path: bsp mid module parsing directory

        return:
            imported module and it's class dict

            mod_info:
            such as:
            {
                "SysappBspMidGmac":
                {
                    "module":module
                    "class" :class
                }

            }

            class_info:
            [<class 'sysapp_bsp_mid_gmac.SysappBspMidGmac'>, ...]
        """
        module_list = {}
        class_list = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.py') \
                    and not filename.startswith('__') \
                    and not filename.startswith('sysapp_bsp_mid_base'):
                module_path = os.path.join(directory_path, filename)
                module_name = os.path.splitext(filename)[0]
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                class_name = ""
                for i in os.path.splitext(filename)[0].split("_"):
                    class_name += i.title()

                module_list[class_name] = {}
                module_list[class_name]["module"] = module
                module_list[class_name]["class"] = getattr(module, class_name)
                class_list.append(module_list[class_name]["class"])

        self.bsp_mid_mod_info = module_list
        self.bsp_mid_class_info = class_list

    @sysapp_print.print_line_info
    def __init__(self):
        """ Init func. """

        self.bsp_mid_mod_info = {}
        self.bsp_mid_class_info = []
        self.bsp_mid_mod_info = self.__import_bsp_mid_modinfo_init__("suite/bsp/general_cases/mid")

    @sysapp_print.print_line_info
    def run_mid_func(self, func, args=None):
        """ run middle function.

        Args:
            args: to be filled be each middle class

        return:
            imported module and it's class dict
        """
        ret = 0
        for class_info in self.bsp_mid_class_info:
            try:
                callback = getattr(class_info, func)
            except AttributeError:
                continue

            if callable(callback):
                ret |= callback(args)
            else:
                print("No support function")

        return ret
