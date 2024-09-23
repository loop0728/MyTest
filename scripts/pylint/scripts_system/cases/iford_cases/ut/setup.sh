#!/bin/sh

############################## UT ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x80 /ut "suite/ut/sysapp_ut_client.py" SysappUtClient on
AddCaseSystem 0x80 /ut "suite/ut/sysapp_ut_dm.py" SysappUtDm on
AddCaseSystem 0x80 /ut "suite/ut/sysapp_ut_common.py" SysappUtCommon on
AddCaseSystem 0x80 /ut "suite/ut/sysapp_ut_stat_timecost.py" SysappUtStatTimecost on
############################## UT ##############################