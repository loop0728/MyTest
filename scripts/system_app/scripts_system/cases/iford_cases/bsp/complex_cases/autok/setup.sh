#!/bin/sh

############################## autok ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt

AddCaseSystem 0x0100 /bsp/complex_cases/autok "suite/bsp/complex_cases/autok/sysapp_bsp_autok_ott_kernel.py" Test_For_AutokOtt_In_PureLinux_Flow
AddCaseSystem 0x0100 /bsp/complex_cases/autok "suite/bsp/complex_cases/autok/sysapp_bsp_autok_ott_uboot.py" Test_For_AutokOtt_By_UbootCmd
AddCaseSystem 0x0100 /bsp/complex_cases/autok "suite/bsp/complex_cases/autok/sysapp_bsp_autok_ott_str.py" Test_For_AutokOtt_In_StrScenc
AddCaseSystem 0x0100 /bsp/complex_cases/autok "suite/bsp/complex_cases/autok/sysapp_bsp_autok.py" Test_For_AutokOnly_In_PureLinux_Flow
AddCaseSystem 0x0100 /bsp/complex_cases/autok "suite/bsp/complex_cases/autok/sysapp_bsp_autok_str.py" Test_For_AutokOnly_In_StrScenc
############################## autok ##############################
