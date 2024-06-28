#!/bin/sh

############################## stress_case ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x10 /AOV/stress_case "AOV/stress_case/reboot_stress.py" reboot_stress on
AddCaseSystem 0x10 /AOV/stress_case "AOV/stress_case/ttff_ttcl_stress.py" ttff_ttcl_stress on
AddCaseSystem 0x10 /AOV/stress_case "AOV/stress_case/str_stress.py" str_stress on
AddCaseSystem 0x10 /AOV/stress_case "AOV/stress_case/str_crc_stress.py" str_crc_stress on
AddCaseSystem 0x10 /AOV/stress_case "AOV/stress_case/OS_switch_stress.py" OS_switch_stress on
############################## stress_case ##############################
