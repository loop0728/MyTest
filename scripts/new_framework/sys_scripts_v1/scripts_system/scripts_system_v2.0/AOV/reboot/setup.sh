#!/bin/sh

############################## reboot ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /AOV/reboot "AOV/reboot/reboot.py" could_reboot on
AddCaseSystem 0x01 /AOV/reboot "AOV/reboot/reboot.py" kernel_reboot on
AddCaseSystem 0x01 /AOV/reboot "AOV/reboot/reboot.py" uboot_rest_reboot on
############################## reboot ##############################
