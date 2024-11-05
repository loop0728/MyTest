#!/bin/sh

############################## os_switch ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x0F /cpu "suite/sys/cpu/sysapp_sys_show_perf.py" SysappSysShowPerf_dualos on
AddCaseSystem 0x0F /cpu "suite/sys/cpu/sysapp_sys_show_perf.py" SysappSysShowPerf_purelinux on
############################## os_switch ##############################
