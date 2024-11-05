#!/bin/sh

############################## padmux ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt

AddCaseSystem 0x0100 /bsp/complex_cases/padmux "suite/bsp/complex_cases/padmux/sysapp_bsp_padmux_purelinux.py" Judge_GPIO_Setting_In_PureLinux
AddCaseSystem 0x0100 /bsp/complex_cases/padmux "suite/bsp/complex_cases/padmux/sysapp_bsp_padmux_dualos.py" Judge_GPIO_Setting_In_Dualos
############################## padmux ##############################