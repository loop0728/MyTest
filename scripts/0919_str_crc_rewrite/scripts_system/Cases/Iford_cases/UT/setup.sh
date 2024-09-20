#!/bin/sh

############################## UT ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x80 /Suite/UT/api_test "Suite/UT/api_test/api_test.py" api_test on
AddCaseSystem 0x80 /Suite/UT/device_manager_test "Suite/UT/device_manager_test/device_manager_test.py" device_manager_test on
AddCaseSystem 0x80 /Suite/UT/system_common_test "Suite/UT/system_common_test/system_common_test.py" system_common_test on
AddCaseSystem 0x80 /Suite/UT/stat_timecost_test "Suite/UT/stat_timecost_test/stat_timecost_test.py" StatTimeCostTest on
AddCaseSystem 0x80 /Suite/UT/reboot_test "Suite/UT/reboot_test/reboot_test.py" RebootTest on
############################## UT ##############################