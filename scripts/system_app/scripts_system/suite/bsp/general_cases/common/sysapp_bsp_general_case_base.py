""" case base for Bsp Mid """
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import importlib
import os
from suite.common.sysapp_common_logger import sysapp_print
import  suite.bsp.general_cases.common.sysapp_bsp_general_case_report as bsp_general_report

REPORT_FILE_PATH = "./suite/bsp/general_cases/bsp_cases/report_bsp_general.xlsx"
COLUMN_HEADER = ['测试项','模块','结果','具体信息']

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
    def __init__(self,case_name):
        """ Init func. """

        self.bsp_mid_mod_info = {}
        self.bsp_mid_class_info = []
        self.test_name = ""
        self.report_handle = None
        self.create_runcase_sheet(case_name)
        self.bsp_mid_mod_info = self.__import_bsp_mid_modinfo_init__("suite/bsp/general_cases/mid")

    def set_runcasetest_name(self,test_name):
        """ run middle function.

        Args: Use for report file
        """
        self.test_name = test_name

    def create_runcase_sheet(self,test_name):
        """ Use for runcase to create its sheet.

        Args:
            runcase report test name
        """
        report_handle = bsp_general_report.SysappBspGeneralReport(REPORT_FILE_PATH,COLUMN_HEADER)
        report_handle.add_sheet_layout(test_name)
        self.report_handle = report_handle
        self.test_name = test_name

    @sysapp_print.print_line_info
    def run_mid_func(self, func, args=None):
        """ run middle function.

        Args:
            args: to be filled be each middle class

        return:
            imported module and it's class dict
        """

        ret = 0
        valid_mid_mod = 0
        report_handle = self.report_handle
        detil_info = []
        result = None
        all_ret = 0
        test_type="auto_"
        if int(args[1],16) & (1 << 9):
            test_type="manual_"

        for class_info in self.bsp_mid_class_info:

            try:
                callback = getattr(class_info, test_type+func)
            except AttributeError:
                continue

            if callable(callback):
                ret,detil_info= callback(args)
                if ret==0:
                    result = "PASS"
                else:
                    result = "FAIL"

                valid_mid_mod += 1

                report_handle.fill_all_result(str(class_info),result,detil_info)
                all_ret |= ret
            else:
                print("No support function")

        report_handle.file_test_item(self.test_name,valid_mid_mod)

        return all_ret
