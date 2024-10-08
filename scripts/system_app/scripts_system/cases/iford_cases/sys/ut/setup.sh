#!/bin/sh

############################## UT ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_client.py" SysappUtClient on
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_dm.py" SysappUtDm on
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_common.py" SysappUtCommon on
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_stat_timecost.py" SysappUtStatTimecost on
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_reboot_opts.py" SysappUtRebootTest on
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_register_opts.py" SysappUtRegisterTest on
AddCaseSystem 0x80 /ut "suite/sys/ut/sysapp_ut_device_opts.py" SysappUtDeviceTest on
############################## UT ##############################