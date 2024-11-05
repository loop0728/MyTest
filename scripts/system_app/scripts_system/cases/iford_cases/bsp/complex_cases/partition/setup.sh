#!/bin/sh

############################## parttition ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt

AddCaseSystem 0x0100 /bsp/complex_cases/parttition "suite/bsp/complex_cases/partition/sysapp_bsp_partition_backup.py" Test_For_Parttition_Backup_Boot_Flow
AddCaseSystem 0x0100 /bsp/complex_cases/parttition "suite/bsp/complex_cases/partition/sysapp_bsp_partition_env.py" Test_For_Parttition_ENV_Backup_Boot_Flow
AddCaseSystem 0x0100 /bsp/complex_cases/parttition "suite/bsp/complex_cases/partition/sysapp_bsp_partition_ab.py" Test_For_Parttition_Backup_AB_Boot_Flow

############################## parttition ##############################
