import sys

from variables import ttff_ttcl_counts as TEST_COUNTS
sys.path.append("..")
from AOV.ttff_ttcl.ttff_ttcl import system_runcase as runcase
from AOV.stress_case.stress_common import StressCase

TEST_REPORT_PATH = "AOV/stress_case/out/test_report/"
TEST_REPORT_FILE = "{}ttff_ttcl_stress.txt".format(TEST_REPORT_PATH)

RESULT_PASS = 0
SLEEP_TIME = 5         # Time between two tests. Second

def system_runcase(args):
    result = RESULT_PASS

    ttff_ttcl_stress = StressCase(TEST_COUNTS,
                                  SLEEP_TIME,
                                  TEST_REPORT_PATH,
                                  TEST_REPORT_FILE,
                                  args)
    ttff_ttcl_stress.register_runcase_hook(runcase)
    result = ttff_ttcl_stress.run()
    return result

def system_help(args):
    print("ttff_ttcl stress test")