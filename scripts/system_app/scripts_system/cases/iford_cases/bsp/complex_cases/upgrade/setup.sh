#!/bin/sh

############################## upgrade ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt

AddCaseSystem 0x0100 /bsp/complex_cases/upgrade "suite/bsp/complex_cases/upgrade/sysapp_bsp_usb_blank_upgrade.py" SysappUsbBlankUpgrade on
AddCaseSystem 0x0100 /bsp/complex_cases/upgrade "suite/bsp/complex_cases/upgrade/sysapp_bsp_sd_blank_upgrade.py" SysappSDBlankUpgrade on
AddCaseSystem 0x0100 /bsp/complex_cases/upgrade "suite/bsp/complex_cases/upgrade/sysapp_bsp_usb_storage_upgrade.py" SysappUSBStorageUpgrade on
AddCaseSystem 0x0100 /bsp/complex_cases/upgrade "suite/bsp/complex_cases/upgrade/sysapp_bsp_uart_blank_upgrade.py" SysappBspUartBlankUpgrade on
AddCaseSystem 0x0100 /bsp/complex_cases/upgrade "suite/bsp/complex_cases/upgrade/sysapp_bsp_usb_blank_secureboot_upgrade.py" SysappBspUsbBlankSecurebootUpgrade on
############################## upgrade ##############################
