#!/bin/sh

############################## IDAC ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
AddCaseSystem 0x01 /idac "suite/idac/idac.py" Idac on
AddCaseSystem 0x10 /idac "suite/idac/idac.py" Idac_stress_3 on
############################## IDAC ##############################
