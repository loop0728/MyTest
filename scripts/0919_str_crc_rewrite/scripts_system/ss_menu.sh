#!/bin/sh

script=shell
stage=0xFFFFFFFF
#prog="./sstar_console --socket=192.168.1.10"
#prog="./sstar_console --shm"
#prog=./prog_${module}
menu_root_prev=root
out_path=./json
case_id=0
conv2json=0
run_all_solution=

nc='\e[0m'
red='\e[0;31m'
red_hl='\e[1;31m'
green='\e[0;32m'
green_hl='\e[1;32m'
yellow='\e[0;33m'
yellow_hl='\e[1;33m'
blue='\e[0;34m'
blue_hl='\e[1;34m'
funchsin='\e[0;35m'
funchsin_hl='\e[1;35m'
cyan='\e[0;36m'
cyan_hl='\e[1;36m'

ShowHelp()
{
    echo "USAGE: $0"
    echo "USAGE: $0 stage=${stage} ..."
    echo "Parameter:"
    echo "[help]"
    echo "[stage] Filter value of cases"
    echo "    --->Default:${stage}"
    echo "[script] shell/json]"
    echo "    --->Default:${script}"
    echo "[prog] ./prog_hvp]"
    echo "    --->Default:${prog}"
    echo "[conv2json] 0/1]"
    echo "    --->Default:${conv2json}"
    echo "[traverse]: [sorted/random]"
    echo "    --->Default:${run_all_solution}"
}
ParseInitParam()
{
    # $1: prepared to be parsed string, $2 default string val
    key=${1%=*}
    if [ "${key}" != "${1}" ]; then
        prev_key=
    fi
    case ${key} in
        "stage")
            stage=${1#*=}
        ;;
        "script")
            script=${1#*=}
        ;;
        "prog")
            prog=${1#*=}
            prev_key=prog
        ;;
        "conv2json")
            conv2json=${1#*=}
        ;;
        "traverse")
            run_all_solution=${1#*=}
        ;;
        "help")
            ShowHelp
            exit
        ;;
        *)
            if [ -n "${prev_key}" ]; then
                eval ${prev_key}=\"\${${prev_key}} ${1}\"
            fi
        ;;
    esac
}
for param in $@
do
    ParseInitParam ${param}
done

prev_key=
run_case="RunCase"
#Add for AT for checking result by machine.
if [ -z "${menu_in_cb}" ]; then
    menu_in_cb="AutoTestCheckDef"
fi
if [ -z "${menu_out_cb}" ]; then
    menu_out_cb="AutoTestCheckDef"
fi
if [ -z "${case_exec_cb}" ]; then
    case_exec_cb="AutoTestCheckDef"
fi

AutoTestCheckDef()
{
    return
}

ShowHelpStart()
{
    #p1: case path, p2: case name
    echo -e "${cyan_hl}----------------------------------------------------------------------------------------------------"
    echo -e "${green_hl}CASE_PATH : ${yellow_hl}/${1} ${green_hl}NAME: ${funchsin_hl}${2} ${green_hl}Help Information:"
    echo -e "\n${cyan_hl}"
}

ShowHelpEnd()
{
    echo -e "\n"
    echo -e "${cyan_hl}----------------------------------------------------------------------------------------------------${nc}"
    read -p "Press any key to continue." __key
}

CostTime()
{
    _begin=$1
    _end=`date +%s`
    _total=$(($_end - $_begin))
    _hour=$(($_total/3600))
    _minute=$(($_total%3600/60))
    _second=$(($_total%3600%60))
    _pass_time=`printf "%02d:%02d:%02d" $_hour $_minute $_second`
    echo $_pass_time
}

RunCase()
{
    #1: case path, 2: script+parameters, 3: case name 4: case stage 5: output json 6: log opt

    if [ ${conv2json} -eq 1  ]; then
        mkdir -p ${out_path}/${1}
        echo GEN_JSON: ${1}/${3}
        if [ ${5} != "off" ]; then
            ${prog} --shell "${2}" --case-name=${3} --stage=${stage} --stage-range=${4} --conv2json -l=0 -o ${out_path}/${1}/${3}.json &> /dev/null
        fi
        return
    fi
    if [ ${script} == "shell"  ]; then
        mkdir -p ${out_path}/${1}
        if [ ${5} != "off" ]; then
            ${prog} --shell "${2}" --case-name=${3} --stage=${stage} --stage-range=${4} -l=${6} -o ${out_path}/${1}/${3}.json
        else
            ${prog} --shell "${2}"
        fi
    fi
    if [ ${script} == "json"  ]; then
        if [ ${5} != "off" ]; then
            ${prog} --json ${out_path}/${1}/${3}.json --stage=${stage} --stage-range=${4} -l=${6} -o ${out_path}/${1}/${3}.json
        else
            ${prog} --json ${out_path}/${1}/${3}.json
        fi
    fi
}

GenReport()
{
     ${prog} -t ./${module}_test_report.json --gen-report --script-path ${out_path}/
}

SetMenuIo()
{
    __path_val=${1//[^A-Za-z0-9_]/ }
    __path_val=${1//[^A-Za-z0-9_]/__sep__}
    if [ "${__path_val}" == "__sep__" ]; then
        eval menu___sep__${__path_val}_in_cb=${2}
        eval menu___sep__${__path_val}_in_para=\"\${3}\"
        eval menu___sep__${__path_val}_out_cb=${4}
        eval menu___sep__${__path_val}_out_para=\"\${5}\"
    else
        eval menu_${__path_val}_in_cb=${2}
        eval menu_${__path_val}_in_para=\"\${3}\"
        eval menu_${__path_val}_out_cb=${4}
        eval menu_${__path_val}_out_para=\"\${5}\"
    fi
}

AddMenuStep()
{
    #1: exist path 2: new path name
    __path_val=${1//[^A-Za-z0-9_]/__sep__}
    eval menu_count=\${menu_${__path_val}_count}
    if [ -z "${menu_count}" ]; then
        eval menu_${__path_val}_count=0
        menu_count=0
    fi
    if [ "${__path_val}" == "__sep__" ]; then
        eval sub_menu_check=\${menu___sep__${2}_prev}
        if [ -n "${sub_menu_check}" ]; then
            #Avoid the same sub menu to be appeared.
            return
        fi
        eval menu___sep__${2}_prev=__sep__
    else
        eval sub_menu_check=\${menu_${__path_val}__sep__${2}_prev}
        if [ -n "${sub_menu_check}" ]; then
            #Avoid the same sub menu to be appeared.
            return
        fi
        eval menu_${__path_val}__sep__${2}_prev=${__path_val}
    fi
    eval menu_${__path_val}_${menu_count}=${2}
    let menu_${__path_val}_count=menu_${__path_val}_count+1
}

AddMenu()
{
    menu_str=${1//[^A-Za-z0-9_]/ }
    last_str=
    for param in ${menu_str}
    do
        if [ -n "${last_str}" ]; then
            AddMenuStep ${last_str} ${param}
        else
            AddMenuStep / ${param}
        fi
        last_str="${last_str}/${param}"
    done
}

AppendMenuInfo()
{
    __path_val=${1//[^A-Za-z0-9_]/__sep__}
    eval menu_${__path_val}_info=\"\${menu_${__path_val}_info} \${2}\\n\"
}

ShuffleAlgorithm()
{
    #1: min value, 2: max value
    value_out=
    __loop_id=${1}
    while [ ${__loop_id} -lt ${2} ]; do
       eval __value_${__loop_id}=${__loop_id}
       let __loop_id=${__loop_id}+1
    done
    __loop_id=${1}
    while [ ${__loop_id} -lt ${2} ]; do
        __random=$((${RANDOM}%(${2}-${1})+${1}))
        eval __tmp_val=\${__value_${__loop_id}}
        eval __value_${__loop_id}=\${__value_${__random}}
        eval __value_${__random}=${__tmp_val}
        let __loop_id=${__loop_id}+1
    done
    __loop_id=${1}
    eval value_out="\${__value_${__loop_id}}"
    let __loop_id=${__loop_id}+1
    while [ ${__loop_id} -lt ${2} ]; do
       eval __tmp_val="\${__value_${__loop_id}}"
       value_out="${value_out} ${__tmp_val}"
       let __loop_id=${__loop_id}+1
    done
}

ValueCombineByOrder()
{
    #1: min value, 2: max value
    __loop_id=${1}
    value_out=${__loop_id}
    let __loop_id=${__loop_id}+1
    while [ ${__loop_id} -lt ${2} ]; do
        value_out="${value_out} ${__loop_id}"
        let __loop_id=${__loop_id}+1
    done
}

TraverseCase()
{
    #1: path 2:depended or not
    current_menu=${1}
    eval time_begin_${current_menu}=`date +%s`
    eval menu_count=\${menu_${current_menu}_count}
    if [ -z "${menu_count}" ]; then
        err_menu=${current_menu//__sep__/\/}
        echo -e "${yellow_hl}"No test case in the menu : ${err_menu} "${nc}"
        return
    fi
    eval case_count_${current_menu}=0
    echo Traverse Start In Menu: ${current_menu//__sep__/\/}
    ${loop_order_func} 0 ${menu_count}
    for loop_id in ${value_out}
    do
        eval loop_id_${current_menu}=${loop_id}
        eval case_name=\${menu_${current_menu}_${loop_id}}
        eval case_stage=\${case_stage_${current_menu}_${case_name}}
        if [ "${current_menu}" == "__sep__" ]; then
            eval next_menu=__sep__\${menu_${current_menu}_${loop_id}}
        else
            eval next_menu=${current_menu}__sep__\${menu_${current_menu}_${loop_id}}
        fi
        eval next_menu_count=\${menu_${next_menu}_count}
        eval next_menu_in_cb=\${menu_${next_menu}_in_cb}
        eval io_menu_${next_menu}=\${menu_${current_menu}_${loop_id}}
        if [ -z "${next_menu_count}" ] && [ -n "${case_stage}" ]; then
            case_path=${current_menu//__sep__/\/}
            case_path=${case_path/[^A-Za-z0-9_]/}
            eval case_para="\${case_para_${current_menu}_${case_name}}"
            eval case_json=\${case_json_${current_menu}_${case_name}}
            if [ "${case_json}" != "off" ]; then
                eval case_para_ext0="\${case_para_ext0${current_menu}_${case_name}}"
                eval case_para_ext1="\${case_para_ext1${current_menu}_${case_name}}"
                eval case_json_ext0=\${case_json_ext0${current_menu}_${case_name}}
                eval case_json_ext1=\${case_json_ext1${current_menu}_${case_name}}
                eval let case_count_${current_menu}++
                echo RUN_CASE: ${case_path}/${case_name}
                if [ "${2}" == "depended" ]; then
                    eval case_logopt=\${case_logopt_${current_menu}_${case_name}}
                    ${run_case} ${case_path} "${case_para}" "${case_name}" "${case_stage}" ${case_json} ${case_logopt}
                    if [ -n "${case_para_ext0}" ]; then
                        eval case_logopt_ext0=\${case_logopt_ext0${current_menu}_${case_name}}
                        ${run_case} ${case_path} "${case_para_ext0}" "${case_name}" "${case_stage}" ${case_json_ext0} ${case_logopt_ext0}
                    fi
                    if [ -n "${case_para_ext1}" ]; then
                        eval case_logopt_ext1=\${case_logopt_ext1${current_menu}_${case_name}}
                        ${run_case} ${case_path} "${case_para_ext1}" "${case_name}" "${case_stage}" ${case_json_ext1} ${case_logopt_ext1}
                    fi
                else
                    ${run_case} ${case_path} "${case_para}" "${case_name}" "${case_stage}" ${case_json} 2
                    if [ -n "${case_para_ext0}" ]; then
                        ${run_case} ${case_path} "${case_para_ext0}" "${case_name}" "${case_stage}" ${case_json_ext0} 2
                    fi
                    if [ -n "${case_para_ext1}" ]; then
                        ${run_case} ${case_path} "${case_para_ext1}" "${case_name}" "${case_stage}" ${case_json_ext1} 2
                    fi
                fi
                ${case_exec_cb} "${case_path}/${case_name}"
            fi
            continue
        elif [ -n "${next_menu_in_cb}" ]; then
            #Do something when enter_menu the menu.
            echo MENU_I: ${next_menu//__sep__/\/}
            eval ${next_menu_in_cb} ${current_menu//__sep__/\/} \${io_menu_${next_menu}} \"\${menu_${next_menu}_in_para}\"
            ${menu_in_cb} ${next_menu//__sep__/\/}
        fi
        TraverseCase ${next_menu} ${2}
        current_menu=${1}
        eval loop_id=\${loop_id_${current_menu}}
        eval menu_count=\${menu_${current_menu}_count}
        if [ "${current_menu}" == "__sep__" ]; then
            eval next_menu=__sep__\${menu_${current_menu}_${loop_id}}
        else
            eval next_menu=${current_menu}__sep__\${menu_${current_menu}_${loop_id}}
        fi
        eval next_menu_out_cb=\${menu_${next_menu}_out_cb}
        if [ -n "${next_menu_out_cb}" ]; then
            #Do something when exit the menu.
            echo MENU_O: ${next_menu//__sep__/\/}
            eval ${next_menu_out_cb} ${current_menu//__sep__/\/} \${io_menu_${next_menu}} \"\${menu_${next_menu}_out_para}\"
            ${menu_out_cb} ${next_menu//__sep__/\/}
        fi
    done
    eval prev_menu=\${menu_${current_menu}_prev}
    eval let case_count_${prev_menu}=\${case_count_${prev_menu}}+\${case_count_${current_menu}}
    eval _time_begin_current_menu=\${time_begin_${current_menu}}
    eval cost_time_${current_menu}=$(CostTime $_time_begin_current_menu)
    eval echo Traverse End In Menu: ${current_menu//__sep__/\/} case count: \${case_count_${current_menu}} cost time: \${cost_time_${current_menu}}
}

RunCaseAll()
{
    if [ "${1}" == "sorted" ];then
        loop_order_func=ValueCombineByOrder
    elif [ "${1}" == "random" ];then
        loop_order_func=ShuffleAlgorithm
    else
        echo -e "${red_hl}Error for bad value of parameter[1]:${1}${nc}."
        return
    fi
    TraverseCase __sep__ ""
}

ShowMenu()
{
    prev_menu=__sep__
    current_menu=__sep__
    while true; do
        eval menu_count=\${menu_${current_menu}_count}
        if [ -z "${menu_count}" ]; then
            err_menu=${current_menu//__sep__/\/}
            echo -e "${yellow_hl}"No test case in the menu : ${err_menu} "${nc}"
            break
        fi
        echo -e "${cyan_hl}--------------------------------------------------------------------------${nc}\n"
        eval menu_info=\${menu_${current_menu}_info}
        if [ -n "${menu_info}" ]; then
            echo -e "${yellow_hl}${menu_info}${nc}"
        fi
        echo -e ${cyan_hl}MENU PATH: ${yellow_hl}${current_menu//__sep__/\/}
        echo -e "\n${cyan_hl}--------------------------------------------------------------------------${nc}"
        loop_id=0
        b_show_help=0
        show_menu_id=0
        show_menu_case_id=0
        show_folder_delay=
        while [ ${loop_id} -lt ${menu_count} ]; do
            eval case_name=\${menu_${current_menu}_${loop_id}}
            eval case_stage=\${case_stage_${current_menu}_${case_name}}
            if [ -n "${case_stage}" ]; then
                #Judge if it is a case.
                if [ -f  ${out_path}/${current_menu//__sep__/\/}/${case_name}.json ]; then
                    json_result=`awk 'NR==3{print $2}' ${out_path}/${current_menu//__sep__/\/}/${case_name}.json`
                    json_stage=`awk 'NR==5{print $2}' ${out_path}/${current_menu//__sep__/\/}/${case_name}.json`
                    json_result=${json_result//[\"\,]/}
                    json_stage=${json_stage//[\"\,]/}
                    if [ $((${json_result} & ${stage})) -eq $((${stage})) ]; then
                        eval echo -e "\${cyan_hl}${show_menu_case_id}: \${green_hl}[P]\${menu_${current_menu}_${loop_id}}\${nc}"
                    elif [ $((${json_stage} & ${stage})) -eq 0 ]; then
                        eval echo -e "\${cyan_hl}${show_menu_case_id}: \${funchsin_hl}[N]\${menu_${current_menu}_${loop_id}}\${nc}"
                    else
                        eval echo -e "\${cyan_hl}${show_menu_case_id}: \${red_hl}[F]\${menu_${current_menu}_${loop_id}}\${nc}"
                    fi
                else
                    eval echo -e "\${cyan_hl}${show_menu_case_id}: \${funchsin_hl}\${menu_${current_menu}_${loop_id}}\${nc}"
                fi
                eval select_${show_menu_case_id}=\${loop_id}
                let show_menu_case_id=show_menu_case_id+1
            else
                eval show_folder_delay=\"${show_folder_delay} \${menu_${current_menu}_${loop_id}}\"
                eval select_menu_${show_menu_id}=\${loop_id}
                let show_menu_id=show_menu_id+1
            fi
            let loop_id=loop_id+1
        done
        loop_id=0
        show_menu_id=${show_menu_case_id}
        for __folder in ${show_folder_delay}
        do
            echo -e "${cyan_hl}${show_menu_id}: ${yellow_hl}|-${__folder}${nc}"
            eval select_${show_menu_id}=\${select_menu_${loop_id}}
            eval select_menu_${loop_id}=
            let show_menu_id=show_menu_id+1
            let loop_id=loop_id+1
        done
        while true; do
            eval __selection=\${select_${show_menu_id}}
            if [ -z "${__selection}" ]; then
                break
            fi
            eval select_${show_menu_id}=
            let show_menu_id=show_menu_id+1
        done
        echo -e "${cyan_hl}--------------------------------------------------------------------------${nc}"
        if [ "${current_menu}" == "__sep__" ]; then
            echo -e ${cyan_hl}Press ${yellow_hl}\"q\" ${cyan_hl}to get back to main menu.${nc}
        else
            echo -e ${cyan_hl}Press ${yellow_hl}\"q\" ${cyan_hl}to get back to previous menu.${nc}
        fi
        echo -e ${cyan_hl}Press ${yellow_hl}\"a/all\" ${cyan_hl}to run all cases in order under current menu.${nc}
        echo -e ${cyan_hl}Press ${yellow_hl}\"r/random\" ${cyan_hl}to run all cases in random order under current menu.${nc}
        echo -e ${cyan_hl}Press ${yellow_hl}\"an\" ${cyan_hl}to run all cases in order under current menu without judgment.${nc}
        echo -e ${cyan_hl}Press ${yellow_hl}\"rn\" ${cyan_hl}to run all cases in random order under current menu without judgment.${nc}
        echo -e ${cyan_hl}Press ${yellow_hl}\"hn\" ${cyan_hl}to show case\'s help infomation. \'n\' represends case\'s selection id.${nc}
        printf "${cyan_hl}Choose: ${nc}"
        read -p "" choice

        if echo "${choice}" | grep -q '[^[:alnum:]_]'; then
            continue
        fi

        if [ "${choice}" == "q" ] && [ "${current_menu}" == "__sep__" ]; then
            #Current menu is root, exit the shell program.
            break
        fi
        if [ "${choice}" == "q" ] && [ "${current_menu}" != "__sep__" ]; then
            #Go back to the previous menu.
            eval current_menu_out_cb=\${menu_${current_menu}_out_cb}
            eval current_menu_out_para=\"\${menu_${current_menu}_out_para}\"
            eval current_menu=\${menu_${current_menu}_prev}
            eval prev_menu=\${menu_${current_menu}_prev}
            if [ -n "${current_menu_out_cb}" ]; then
                eval ${current_menu_out_cb} ${current_menu//__sep__/\/} ${next_menu_io} \"${current_menu_out_para}\"
            fi
            continue
        fi
        if [ "${choice}" == "a" ] || [ "${choice}" == "all" ]; then
            #Run all cases under current menu
            loop_order_func=ValueCombineByOrder
            TraverseCase ${current_menu} depended
            continue
        fi
        if [ "${choice}" == "r" ] || [ "${choice}" == "random" ]; then
            #Run all cases under current menu
            loop_order_func=ShuffleAlgorithm
            TraverseCase ${current_menu} depended
            continue
        fi
        if [ "${choice}" == "an" ]; then
            #Run all cases under current menu
            loop_order_func=ValueCombineByOrder
            TraverseCase ${current_menu} ""
            continue
        fi
        if [ "${choice}" == "rn" ]; then
            #Run all cases under current menu
            loop_order_func=ShuffleAlgorithm
            TraverseCase ${current_menu} ""
            continue
        fi
        case "${choice}" in
            h[0-9]*)
                b_show_help=1
                choice=${choice/h/}
                ;;
            *)
                ;;
        esac
        #Get the selected menu name or case name.
        eval choice=\${select_${choice}}
        if [ "${current_menu}" == "__sep__" ]; then
            eval next_menu=__sep__\${menu_${current_menu}_${choice}}
        else
            eval next_menu=${current_menu}__sep__\${menu_${current_menu}_${choice}}
        fi
        eval next_menu_count=\${menu_${next_menu}_count}
        eval next_menu_in_cb=\${menu_${next_menu}_in_cb}
        if [ -z "${next_menu_count}" ]; then
            #Next one is end.
            eval case_name=\${menu_${current_menu}_${choice}}
            eval case_stage=\${case_stage_${current_menu}_${case_name}}
            if [ -n "${case_stage}" ]; then
                #Judge if it is a case.
                case_path=${current_menu//__sep__/\/}
                case_path=${case_path/[^A-Za-z0-9_]/}
                eval case_para="\${case_para_${current_menu}_${case_name}}"
                eval case_json=\${case_json_${current_menu}_${case_name}}
                eval case_logopt=\${case_logopt_${current_menu}_${case_name}}
                eval case_para_ext0="\${case_para_ext0${current_menu}_${case_name}}"
                eval case_para_ext1="\${case_para_ext1${current_menu}_${case_name}}"
                eval case_json_ext0=\${case_json_ext0${current_menu}_${case_name}}
                eval case_json_ext1=\${case_json_ext1${current_menu}_${case_name}}
                if [ ${b_show_help} -eq 1 ] && [ -n "${run_case_help}" ]; then
                    ShowHelpStart ${case_path} "${case_name}"
                    ${run_case_help} ${case_para}
                    ShowHelpEnd
                else
                    echo "-------------------------------------------"
                    echo "${run_case} ${case_path} ${case_para} ${case_name} ${case_stage} ${case_json} ${case_logopt}"
                    echo "-------------------------------------------"
                    ${run_case} ${case_path} "${case_para}" "${case_name}" "${case_stage}" ${case_json} ${case_logopt}
                    if [ -n "${case_para_ext0}" ]; then
                        eval case_logopt_ext0=\${case_logopt_ext0${current_menu}_${case_name}}
                        ${run_case} ${case_path} "${case_para_ext0}" "${case_name}" "${case_stage}" ${case_json_ext0} ${case_logopt_ext0}
                    fi
                    if [ -n "${case_para_ext1}" ]; then
                        eval case_logopt_ext1=\${case_logopt_ext1${current_menu}_${case_name}}
                        ${run_case} ${case_path} "${case_para_ext1}" "${case_name}" "${case_stage}" ${case_json_ext1} ${case_logopt_ext1}
                    fi
                fi
            fi
            continue
        elif [ ${b_show_help} -eq 1 ]; then
            continue
        elif [ -n "${next_menu_in_cb}" ]; then
            #Do something when enter_menu the menu.
            eval next_menu_io=\${menu_${current_menu}_${choice}}
            eval ${next_menu_in_cb} ${current_menu//__sep__/\/} ${next_menu_io} \"\${menu_${next_menu}_in_para}\"
        fi

        #If next is menu name, turn it into current.
        prev_menu=${current_menu}
        current_menu=${next_menu}
    done
}

AddCaseExt0()
{
    #1: case_path, 2: script, 3: case_name 4: json_out onoff 5: log opt
    __path_val=${1//[^A-Za-z0-9_]/__sep__}
    eval was_added=\${case_para_${__path_val}_${3}}
    if [ -z "${was_added}" ]; then
        echo "CASE WAS NOT ADDED!!, NAME:${3}"
    fi
    eval case_para_ext0${__path_val}_${3}="\${2}"
    eval case_json_ext0${__path_val}_${3}=${4}
    eval case_logopt_ext0${__path_val}_${3}=${5}
}

AddCaseExt1()
{
    #1: case_path, 2: script, 3: case_name 4: json_out onoff 5: log opt
    __path_val=${1//[^A-Za-z0-9_]/__sep__}
    eval was_added=\${case_para_${__path_val}_${3}}
    if [ -z "${was_added}" ]; then
        echo "CASE WAS NOT ADDED!!, NAME:${3}"
    fi
    eval case_para_ext1${__path_val}_${3}="\${2}"
    eval case_json_ext1${__path_val}_${3}=${4}
    eval case_logopt_ext1${__path_val}_${3}=${5}
}

AddCaseIn()
{
    #1: case_stage, 2: case_path, 3: script, 4: case_name 5: json_out onoff 6: log opt

    AddMenuStep ${2} ${4}
    __path_val=${2//[^A-Za-z0-9_]/__sep__}
    eval was_added=\${case_para_${__path_val}_${4}}
    if [ -n "${was_added}" ]; then
        echo "CASE DUPLICATED !!! ID${case_id} ${2}/${4}"
        exit
    fi
    eval case_para_${__path_val}_${4}="\${3}"
    eval case_stage_${__path_val}_${4}=${1}
    eval case_json_${__path_val}_${4}=${5}
    eval case_logopt_${__path_val}_${4}=${6}
    if [ "${5}" != "off" ]; then
        let case_id=case_id+1
    fi
    if [ ${case_id} -eq 0 ];then
        return
    fi
    if [ "${__first_entry}" == "" ];then
        __first_entry=1
        echo "Loading Case ${case_id}"
        return
    fi
    printf "\e[1A"
    printf "\e[13C"
    echo ${case_id}
}
AddCaseMenuCheck()
{
    #1: case_stage, 2: case_path, 3: script, 4: case_name

    if [ $((${1} & ${stage})) -eq 0 ]; then
        return
    fi
    __path_val=${2//[^A-Za-z0-9_]/__sep__}
    eval menu_count=\${menu_${__path_val}_count}
    if [ -z "${menu_count}" ]; then
        echo "Can't find the menu ${2}!!!"
        return
    fi
    AddCaseIn ${1} ${2} "${3}" ${4} on 2
}
AddCase()
{
    #1: case_stage, 2: case_path, 3: script, 4: case_name

    if [ $((${1} & ${stage})) -eq 0 ]; then
        return
    fi
    AddMenu ${2}
    AddCaseIn ${1} ${2} "${3}" ${4} on 2
}

SetupUi()
{
    if [ -n "${run_all_solution}" ];then
        RunCaseAll ${run_all_solution}
        #这里与 mixer 不同，mixer 直接exit，使用return是因为在使用 traverse 参数的时候还需要执行 SetupUi 函数 之后的代码
        return
    fi
    echo -e "${blue_hl}----------------------------------------------------------------------------------------------------"
    echo "                                                        #                                       "
    echo "   #####                                      ##########       +++++                            "
    echo " ##     ##  ###                             ###       ###    ++++++++   + +                     "
    echo " ##                ###  #   # ##   ###    ###  ++++++   ##   ++++     +++++++    +++++        + "
    echo "   ######    #   ###  ###  ###  ###  ###  ## ++++++  ++  ##   ++++++  +++++++  ++   ++++ +++++++"
    echo "         ##  #  ##      #  ##    #    ## ##  ++++++++++  ##      ++++  ++++     ++++++++ ++++   "
    echo " ##      #   #   ##    ##  ##    ##   ##  ##  ++++++++  ##  +++++++++  ++++++ ++++  +++  +++    "
    echo "   ######    #     ######  ##    #    ##   ###   ++    ##   +++++++     +++++  ++++++++  +++    "
    echo "                ###    ##                    ##########                                         "
    echo "                  #####                                                                         "
    echo -e "----------------------------------------------------------------------------------------------------${nc}"
    while true; do
        echo -e "${cyan_hl}--------------------------------------------------------------------------${nc}"
        echo -e ${cyan_hl}Sigmastar SS_CMD ${blue_hl}Menu${nc}:
        echo -e "${cyan_hl}Module Name : ${blue_hl}${module}${nc}"
        echo -e "${cyan_hl}Case Count  : ${blue_hl}${case_id}${nc}"
        echo -e "${cyan_hl}Press ${yellow_hl}'a/all'    ${cyan_hl}to run all cases in order.${nc}"
        echo -e "${cyan_hl}Press ${yellow_hl}'r/random' ${cyan_hl}to run all cases in random order.${nc}"
        echo -e "${cyan_hl}Press ${yellow_hl}'m/menu'   ${cyan_hl}to run case by menu selection.${nc}"
        echo -e "${cyan_hl}Press ${yellow_hl}'g/gen'    ${cyan_hl}to generate case report file from json output path.${nc}"
        echo -e "${cyan_hl}Press ${yellow_hl}'q/quit'   ${cyan_hl}to exit.${nc}"
        echo -e "${cyan_hl}--------------------------------------------------------------------------${nc}"
        printf "${cyan_hl}Choose: ${nc}"
        read -p "" select_menu
        if [ "${select_menu}" == "a"  ] || [ "${select_menu}" == "all"  ]; then
            RunCaseAll sorted
        elif [ "${select_menu}" == "r"  ] || [ "${select_menu}" == "random"  ]; then
            RunCaseAll random
        elif [ "${select_menu}" == "m"  ] || [ "${select_menu}" == "menu"  ]; then
            ShowMenu
        elif [ "${select_menu}" == "g"  ] || [ "${select_menu}" == "gen"  ]; then
            GenReport
        elif [ "${select_menu}" == "q"  ] || [ "${select_menu}" == "quit"  ]; then
            return
        else
            # Don't do anything.
            continue
        fi
    done
}
