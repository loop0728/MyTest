#!/bin/sh

############################## os_switch ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /memory "suite/memory/show_memory.py" show_memory_dualos on
AddCaseSystem 0x01 /memory "suite/memory/show_memory.py" show_memory_purelinux on
############################## os_switch ##############################
