#!/bin/sh

############################## cold_reboot ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /Suite/AOV/cold_reboot "Suite/AOV/cold_reboot/cold_reboot.py" cold_reboot on

############################## str ##############################
