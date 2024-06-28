import sys

from variables import change_fps_counts as TEST_COUNTS
sys.path.append("..")
from AOV.change_fps.change_fps import system_runcase as runcase
from AOV.stress_case.stress_common import StressCase

TEST_REPORT_PATH = "AOV/stress_case/out/test_report/"
TEST_REPORT_FILE = "{}change_fps_stress.txt".format(TEST_REPORT_PATH)

RESULT_PASS = 0
SLEEP_TIME = 5         # Time between two tests. Second

def system_runcase(args):
    result = RESULT_PASS

    change_fps_stress = StressCase(TEST_COUNTS,
                                   SLEEP_TIME,
                                   TEST_REPORT_PATH,
                                   TEST_REPORT_FILE,
                                   args)
    change_fps_stress.register_runcase_hook(runcase)
    result = change_fps_stress.run()

    return result

def system_help(args):
    print("change_fps stress test")