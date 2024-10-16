#!/bin/sh

############################## show_memory ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /memory/show_memory "suite/sys/memory/sysapp_sys_show_memory.py" SysappSysShowMemory_dualos on
AddCaseSystem 0x01 /memory/show_memory "suite/sys/memory/sysapp_sys_show_memory.py" SysappSysShowMemory_purelinux on
############################## show_interrupts ##############################
