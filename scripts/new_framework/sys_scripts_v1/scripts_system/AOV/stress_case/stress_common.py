import time
import os
from logger import logger

# 全局变量定义
RESULT_PASS = 0
RESULT_UNKNOWN = 1
RESULT_FAIL = 255

class StressCase():
    def __init__(self, TEST_COUNTS, SLEEP_TIME, TEST_REPORT_PATH, TEST_REPORT_FILE, args):
        self.Case_Name = args[0]
        self.TEST_COUNTS = TEST_COUNTS
        self.SLEEP_TIME = SLEEP_TIME
        self.TEST_REPORT_PATH = TEST_REPORT_PATH
        self.TEST_REPORT_FILE = TEST_REPORT_FILE
        self.args = args
        self.runcase = None

    def register_runcase_hook(self, runcase):
        """ 注册执行单条case的钩子函数 """
        self.runcase = runcase

    def clean_test_report(self):
        """ 清空test report """
        if not os.path.exists(self.TEST_REPORT_PATH):
            os.makedirs(self.TEST_REPORT_PATH)
        with open(self.TEST_REPORT_FILE, "w") as file:
            file.write("################ start test ################\n")

    def add_test_report(self, counts, result):
        """ 添加当前case执行结果 """
        text = "caseName: \"{}\" num: \"{}\" res: \"{}\"!\n".format(
                                                            self.Case_Name,
                                                            counts,
                                                            result)
        with open(self.TEST_REPORT_FILE, "a") as file:
            file.write(text)

    def run(self):
        """ 执行压测case """
        result = RESULT_PASS
        current_counts = 0
        # step1 test report init
        self.clean_test_report()
        # step2 循环执行单条case
        while current_counts < self.TEST_COUNTS:
            logger.info("[sys_app]: The current count is [%d]!\n" %current_counts)
            if self.runcase is not None:
                # step2.1 执行单条case
                result_tmp = self.runcase(self.args)
            else:
                logger.error("[sys_app]: unhooked. nothing to runcase!\n")
                result_tmp = RESULT_UNKNOWN
            time.sleep(self.SLEEP_TIME)
            # step2.2 添加当前case执行结果到test report
            self.add_test_report(current_counts, result_tmp)
            if result_tmp != RESULT_PASS:
                text = "[sys_app]: caseName: \"{}\" num: \"{}\" res: \"{}\"!\n".format(
                                                                            self.Case_Name,
                                                                            current_counts,
                                                                            result_tmp)
                logger.error(text)
                result = result_tmp
            else:
                text = "[sys_app]: caseName: \"{}\" num: \"{}\" PASS!\n".format(
                                                                    self.Case_Name,
                                                                    current_counts,
                                                                    result_tmp)
                logger.info(text)
            current_counts += 1
        return result