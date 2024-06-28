import sys

from variables import str_counts as TEST_COUNTS
sys.path.append("..")
from AOV.str.str import system_runcase as runcase
from AOV.stress_case.stress_common import StressCase

TEST_REPORT_PATH = "AOV/stress_case/out/test_report/"
TEST_REPORT_FILE = "{}str_stress.txt".format(TEST_REPORT_PATH)

RESULT_PASS = 0
SLEEP_TIME = 5         # Time between two tests. Second

def system_runcase(args):
    result = RESULT_PASS

    str_stress = StressCase(TEST_COUNTS,
                            SLEEP_TIME,
                            TEST_REPORT_PATH,
                            TEST_REPORT_FILE,
                            args)
    str_stress.register_runcase_hook(runcase)
    result = str_stress.run()
    return result

def system_help(args):
    print("str stress test")