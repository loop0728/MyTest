#!/bin/sh

############################## str ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
#AddCaseSystem 0x01 /AOV/str "AOV/str/str.py" str on
AddCaseSystem 0x01 /AOV/str "AOV/str/str_crc.py" str_crc on
AddCaseSystem 0x01 /AOV/str "AOV/str/str_crc.py" str_crc_no_crc on

############################## str ##############################
