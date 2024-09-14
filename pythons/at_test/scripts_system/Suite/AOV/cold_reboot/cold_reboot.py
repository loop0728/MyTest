import sys
import time
import re
import os
import json
from PythonScripts.logger import logger
import threading
import inspect
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common

class cold_reboot(CaseBase):
    cnt_check_keyword_dict = {}

    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")

    @logger.print_line_info
    def runcase(self):
        sys_common.cold_reboot()
        return 0

    @logger.print_line_info
    def system_help(args):
        logger.print_warning("dev power off, then power on")

