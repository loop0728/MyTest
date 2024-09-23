#!/bin/sh

############################## aov ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
if [ -z "$1" ]; then
    AddCaseSystem 0x01 /aov/os_switch "suite/aov/os_switch/sysapp_aov_os_switch.py" SysappAovOsSwitch on
    AddCaseSystem 0x01 /aov/reboot "suite/aov/reboot/reboot.py" could_reboot on
    AddCaseSystem 0x01 /aov/reboot "suite/aov/reboot/reboot.py" kernel_reboot on
    AddCaseSystem 0x01 /aov/reboot "suite/aov/reboot/reboot.py" uboot_rest_reboot on
    AddCaseSystem 0x01 /aov/str "suite/aov/str/str.py" Str on
    AddCaseSystem 0x01 /aov/str_crc "suite/aov/str_crc/str_crc.py" StrCrc on
    AddCaseSystem 0x01 /aov/ttff_ttcl "suite/aov/ttff_ttcl/sysapp_aov_ttff_ttcl.py" SysappAovTtffTtcl on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/reboot/reboot.py" uboot_rest_reboot_stress_3 on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/reboot/reboot.py" kernel_reboot_stress_3 on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/change_fps/change_fps.py" change_fps_stress_3 on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/ttff_ttcl/sysapp_aov_ttff_ttcl.py" SysappAovTtffTtcl_stress_3 on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/os_switch/sysapp_aov_os_switch.py" SysappAovOsSwitch_stress_3 on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/str/str.py" Str_stress_3 on
    AddCaseSystem 0x10 /aov/stress_case "suite/aov/str_crc/str_crc.py" StrCrc_stress_3 on
    AddCaseSystem 0x01 /aov/template "suite/aov/template/template.py" template on
else
    module_list=${1#*=}
    for module in ${module_list}
    do
        case ${module} in
            "reboot")
                case_class="Reboot"
            ;;
            "str_crc")
                case_class="StrCrc"
            ;;
            "str")
                case_class="Str"
            ;;
            "ttff_ttcl")
                case_class="SysappAovTtffTtcl"
            ;;
            "os_switch")
                case_class="SysappAovOsSwitch"
            ;;
            *)
                echo "no module named ${module}"
                continue
            ;;
        esac
        AddCaseSystem 0x01 /suite/aov/${module} "suite/aov/${module}/sysapp_aov_${module}.py" ${case_class} on
    done
fi
############################## aov ##############################
