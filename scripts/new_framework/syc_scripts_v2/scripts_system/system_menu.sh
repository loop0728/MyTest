server_cleanup()
{
    echo "exit server py"
    python -B  client.py server_exit
    final_result1=$?
    echo final_result1===$final_result1===
    exit $final_result
}

source ./ss_menu.sh

generate_json() {
    #1: case path, 2: sh result 3: case name. 4: case stage 5: output json 6:case_run_time

    if [ "$5" = "on" ]; then
        mkdir -p ${out_path}/${1}
    else
        return
    fi

    # 当 json 文件已经存在
    if [ -f  ${out_path}/${1}/${3}.json ]; then
        json_stage=`awk 'NR==5{print $2}' ${out_path}/${1}/${3}.json`
        json_stage=${json_stage//[\"\,]/}
        case_stage=$((stage | json_stage))
        json_result=`awk 'NR==3{print $2}' ${out_path}/${1}/${3}.json`
        json_result=${json_result//[\"\,]/}
        json_result=$((json_result))
    else
        json_stage=0
        case_stage=$((stage))
        json_result=0
    fi

    if [ "$2" -eq 0 ]; then
        case_result=$((stage))
        case_result=$((case_result | json_result))
    elif [ "$2" -eq 255 ]; then
        case_result=$((~$((stage))))
        case_result=$((case_result & json_result))
    elif [ "$2" -eq 127 ]; then
        case_result=0
        case_stage=0
    fi

    case_result=$(printf "0x%X" $case_result)
    case_stage=$(printf "0x%X" $case_stage)
    local json_content='{
        "case_name": "'"${3}"'",
        "case_result": "'"$case_result"'",
        "case_run_time": '"${6}"',
        "case_stage": "'"$case_stage"'",
        "case_stage_range": "'"${4}"'"
    }'

     echo "$json_content" > "${out_path}/${1}/${3}.json"
}

generate_json_before_test() {
    #1: path
    current_menu=${1}
    eval time_begin_${current_menu}=`date +%s`
    eval menu_count=\${menu_${current_menu}_count}
    eval case_count_${current_menu}=0
    #echo Travel Start In Menu: ${current_menu//__sep__/\/}
    ValueCombineByOrder 0 ${menu_count}
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
        if [ -z "${next_menu_count}" ]; then
            case_path=${current_menu//__sep__/\/}
            case_path=${case_path/[^A-Za-z0-9_]/}
            eval case_json=\${case_json_${current_menu}_${case_name}}
            if [ "${case_json}" != "off" ]; then
                eval let case_count_${current_menu}++
                if [ -f  ${out_path}/${current_menu//__sep__/\/}/${case_name}.json ]; then
                    rm -rf ${out_path}/${current_menu//__sep__/\/}/${case_name}.json
                fi
                generate_json ${case_path} 127 "${case_name}" "${case_stage}" ${case_json} 0
            fi
            continue
        fi
        generate_json_before_test ${next_menu}
        current_menu=${1}
        eval loop_id=\${loop_id_${current_menu}}
        eval menu_count=\${menu_${current_menu}_count}
        if [ "${current_menu}" == "__sep__" ]; then
            eval next_menu=__sep__\${menu_${current_menu}_${loop_id}}
        else
            eval next_menu=${current_menu}__sep__\${menu_${current_menu}_${loop_id}}
        fi
    done
}


RunCaseDebug()
{
    #1: case path, 2: script+parameters 3: case name. 4: case stage 5: output json 6: log opt
    start_time=$(date +%s)
    python3 -B client.py ${2} ${3}
    result=$?
    if [ $result -ne 0 ]; then
        final_result=$result
    fi
    end_time=$(date +%s)
    execution_time=$((end_time - start_time))
    echo -e "${green_hl}[AUTO_TEST][Time_Consuming][${execution_time}s]"
    if [ $result -eq 0 ];then
        generate_json ${1} 0 ${3} ${4} ${5} ${execution_time}
        echo -e "${green_hl}[AUTO_TEST][Success][$3]${nc}"
    elif [ $result -eq 255 ];then
        generate_json ${1} 255 ${3} ${4} ${5} ${execution_time}
        echo -e "${red_hl}[AUTO_TEST][Fail][$3]${nc}"
    elif [ $result -eq 127 ];then
        generate_json ${1} 127 ${3} ${4} ${5} ${execution_time}
        echo -e "${yellow_hl}[AUTO_TEST][UnTest][$3]${nc}"
    fi

    #if [ $4 == 0x01 ] || [ $4 == 0x1 ] || [ $4 == 1 ] || [ $4 == 0X01 ] || [ $4 == 0X1 ];then
    #    read -p "test finish, please press any key to continue" key
    #fi
}
AddCaseSystem()
{

    if [ $(((${1} & ${stage}))) -eq 0 ]; then
        return
    fi
    AddMenu ${2}
    AddCaseIn ${1} ${2} "${3}" ${4} on ${5}
}

System_Help()
{
    echo "USAGE: $0 help2"
    echo "USAGE: $0 stage=0x01 modules=str os_switch ttff_ttcl traverse=random"
    echo "USAGE: $0 stage=0x01 traverse=sorted"
    echo "Parameter:"
    echo "[help2]"
    echo "[stage] Filter value of cases"
    echo "    --->Tip:The value of the stage must be stated, and only one bit can be set to 1"
    echo "[modules] Module you want to test"
    echo "    --->Default:$module_list"
    echo "[conv2json] Whether to generate default json"
    echo "    --->Default:0"
    echo "[traverse]: [sorted/random]"
    echo "    --->Default:${run_all_solution}"
}

ParseInitParamSystem()
{
    key=${1%=*}
    if [ "${key}" != "${1}" ]; then
        prev_key=
    fi
    case ${key} in
        "modules")
            module_list=${1#*=}
            prev_key=module_list
        ;;
        "help2")
            System_Help
        ;;
        *)
            if [ -n "${prev_key}" ]; then
                echo "ParseInitParamSystem prev_key:${prev_key}"
                eval ${prev_key}=\"\${${prev_key}} ${1}\"
            fi
        ;;
    esac
}


IsStageSingleBitSet() {
    # Check if the number is positive

    if [ $((stage)) -lt 0 ]; then
        return 255
    fi
    # cover to d%
    dec_value=$((stage))

    count=0
    while [ $dec_value -ne 0 ]; do
        bit=$((dec_value & 1))
        if [ $bit -eq 1 ]; then
        count=$((count+1))
        fi
        dec_value=$((dec_value >> 1))
        #echo $count
    done
    if [ $count -eq 1 ]; then
        return 0
    else
        return 255
    fi
}

# help
case_help()
{
    # $1 is the path/name of *.sh   $2 case name
    python3 -B client.py $@ help
}

run_case_help=case_help
run_case="RunCaseDebug"
python3 -B server.py &
sleep 5
# 捕获kill信号，并执行cleanup函数
trap server_cleanup SIGTERM SIGINT ERR
for param in $@
do
   ParseInitParamSystem ${param}
   if [ $? -ne 0 ]; then
      final_result=255
   fi
done

# stage only one bit can be set to 1

IsStageSingleBitSet

result=$?
if [ $result -ne 0 ]; then
    echo "Wrong stage value ${stage}. Only one bit can be set to 1. "
    System_Help
    final_result=255
    exit $final_result
fi

if [ ${conv2json} -ne 0 ]; then
    generate_json_before_test "__sep__"
    exit $final_result
fi

case_list()
{
    if [ -z "${module_list}" ]; then
        module_list="reboot str str_crc ttff_ttcl os_switch stress_case"
    fi
    echo "[module_list] ${module_list}"
    for param in ${module_list}
    do
        source ./AOV/${param}/setup.sh
    done
}

case_list
SetupUi
server_cleanup
wait
exit $final_result
