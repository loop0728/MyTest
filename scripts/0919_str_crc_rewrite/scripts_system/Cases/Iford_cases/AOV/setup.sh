#!/bin/sh

############################## os_switch ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /Suite/AOV/os_switch "Suite/AOV/os_switch/os_switch.py" os_switch on
AddCaseSystem 0x01 /Suite/AOV/reboot "Suite/AOV/reboot/reboot.py" could_reboot on
AddCaseSystem 0x01 /Suite/AOV/reboot "Suite/AOV/reboot/reboot.py" kernel_reboot on
AddCaseSystem 0x01 /Suite/AOV/reboot "Suite/AOV/reboot/reboot.py" uboot_rest_reboot on
AddCaseSystem 0x01 /Suite/AOV/str "Suite/AOV/str/str.py" Str on
AddCaseSystem 0x01 /Suite/AOV/str_crc "Suite/AOV/str_crc/str_crc.py" StrCrc on
AddCaseSystem 0x01 /Suite/AOV/ttff_ttcl "Suite/AOV/ttff_ttcl/ttff_ttcl.py" ttff_ttcl on
AddCaseSystem 0x01 /Suite/AOV/cold_reboot "Suite/AOV/cold_reboot/cold_reboot.py" ColdReboot on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/reboot/reboot.py" uboot_rest_reboot_stress_3 on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/reboot/reboot.py" kernel_reboot_stress_3 on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/change_fps/change_fps.py" change_fps_stress_3 on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/ttff_ttcl/ttff_ttcl.py" ttff_ttcl_stress_3 on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/os_switch/os_switch.py" os_switch_stress_3 on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/str/str.py" Str_stress_3 on
AddCaseSystem 0x10 /Suite/AOV/stress_case "Suite/AOV/str_crc/str_crc.py" StrCrc_stress_3 on
############################## os_switch ##############################
