#!/bin/sh

############################## security_boot ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt

AddCaseSystem 0x0100 /bsp/complex_cases/security_boot "suite/bsp/complex_cases/security_boot/sysapp_bsp_security_boot_manual.py" Test_For_SecurityBoot_With_Manual

if CheckConfigExsit "PROJECT_DEFCONFIG" "CONFIG_IPC-RTOS"; then
  AddCaseSystem 0x0100 /bsp/complex_cases/security_boot "suite/bsp/complex_cases/security_boot/sysapp_bsp_security_boot_automatic_dualos.py" Test_For_SecurityBoot_On_Dualos
else
  AddCaseSystem 0x0100 /bsp/complex_cases/security_boot "suite/bsp/complex_cases/security_boot/sysapp_bsp_security_boot_automatic_purelinux.py" Test_For_SecurityBoot_On_Purelinux
fi
############################## security_boot ##############################
