import sys

from variables import str_crc_counts as TEST_COUNTS
sys.path.append("..")
from AOV.str_crc.str_crc import system_runcase as runcase
from AOV.stress_case.stress_common import StressCase

TEST_REPORT_PATH = "AOV/stress_case/out/test_report/"
TEST_REPORT_FILE = "{}str_crc_stress.txt".format(TEST_REPORT_PATH)

RESULT_PASS = 0
SLEEP_TIME = 5         # Time between two tests. Second

def system_runcase(args):
    result = RESULT_PASS

    str_crc_stress = StressCase(TEST_COUNTS,
                                SLEEP_TIME,
                                TEST_REPORT_PATH,
                                TEST_REPORT_FILE,
                                args)
    str_crc_stress.register_runcase_hook(runcase)
    result = str_crc_stress.run()
    return result

def system_help(args):
    print("str_crc stress test")
