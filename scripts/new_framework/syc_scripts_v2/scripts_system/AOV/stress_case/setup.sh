#!/bin/sh

############################## stress_case ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x10 /AOV/stress_case "AOV/reboot/reboot.py" uboot_rest_reboot_stress_3 on
AddCaseSystem 0x10 /AOV/stress_case "AOV/reboot/reboot.py" kernel_reboot_stress_3 on
AddCaseSystem 0x10 /AOV/stress_case "AOV/change_fps/change_fps.py" change_fps_stress_3 on
AddCaseSystem 0x10 /AOV/stress_case "AOV/ttff_ttcl/ttff_ttcl.py" ttff_ttcl_stress_3 on
AddCaseSystem 0x10 /AOV/stress_case "AOV/os_switch/os_switch.py" os_switch_stress_3 on
AddCaseSystem 0x10 /AOV/stress_case "AOV/str/str.py" str_stress_3 on
AddCaseSystem 0x10 /AOV/stress_case "AOV/str_crc/str_crc.py" str_crc_stress_3 on
############################## stress_case ##############################
