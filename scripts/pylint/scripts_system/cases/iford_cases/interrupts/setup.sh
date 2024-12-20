#!/bin/sh

############################## Interrupts ##############################
#1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt
if [ -z "$1" ]; then
    AddCaseSystem 0x60 /interrupts/show_interrupts "suite/interrupts/show_interrupts.py" ShowInterrupts on
else
    module_list=${1#*=}
    for module in ${module_list}
    do
        case ${module} in
            "show_interrupts")
                case_class="ShowInterrupts"
            ;;
            *)
                echo "no module named ${module}"
                continue
            ;;
        esac
        AddCaseSystem 0x01 /interrupts/${module} "suite/interrupts/${module}.py" ${case_class} on skip
    done
fi
############################## Interrupts ##############################
