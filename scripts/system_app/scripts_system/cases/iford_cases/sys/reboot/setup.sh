#!/bin/sh

############################## reboot ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode0.py" clod_reboot_check_uart_status on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode1.py" clod_reboot_check_uart_keyword on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode2.py" clod_reboot_check_board_net_status on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode3.py" clod_reboot_check_kmsg_keyword on

AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_kernel_reboot_mode0.py" kernel_reboot_check_uart_status on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_kernel_reboot_mode1.py" kernel_reboot_check_uart_keyword on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_kernel_reboot_mode2.py" kernel_reboot_check_board_net_status on

AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_uboot_reboot_mode0.py" uboot_reboot_check_uart_status on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_uboot_reboot_mode1.py" uboot_reboot_check_uart_keyword on
AddCaseSystem 0x01 /reboot "suite/sys/reboot/sysapp_sys_uboot_reboot_mode2.py" uboot_reboot_check_board_net_status on

############################## stress case #########################
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode0.py" cold_reboot_check_uart_status_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode1.py" cold_reboot_check_uart_keyword_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode2.py" cold_reboot_check_board_net_status_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_cold_reboot_mode3.py" clod_reboot_check_kmsg_keyword_stress_3 on

AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_kernel_reboot_mode0.py" kernel_reboot_check_uart_status_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_kernel_reboot_mode1.py" kernel_reboot_check_uart_keyword_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_kernel_reboot_mode2.py" kernel_reboot_check_board_net_status_stress_3 on

AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_uboot_reboot_mode0.py" uboot_reboot_check_uart_status_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_uboot_reboot_mode1.py" uboot_reboot_check_uart_keyword_stress_3 on
AddCaseSystem 0x10 /reboot "suite/sys/reboot/sysapp_sys_uboot_reboot_mode2.py" uboot_reboot_check_board_net_status_stress_3 on
############################## reboot ##############################
