

current_os=$1
casename=$(basename $2 .json)
resultpath=""

if [ -z "$current_os" ]; then
    echo "current_os is null assign to purelinux"
    current_os="purelinux"
fi
echo "current_os:$current_os"
if [ "$casename" == ".json" ]; then
    echo "casename $casename is null"
    exit -1
elif [ "$casename" == "" ]; then
    echo "casename: $casename is null"
    exit -1
else
    echo "casename: $casename"
fi

resultpath=/mnt/out/Memory/$current_os/$casename

mkdir -p $resultpath

if [ "$current_os" = "dualos" ]; then
    echo "cat dualos memory"
    echo cli memstat --usage > /proc/dualos/rtos
    cat /proc/dualos/log | tee $resultpath/rtos_usage.txt
    sleep 3
    echo cli taskstat  > /proc/dualos/rtos
    cat /proc/dualos/log | tee $resultpath/rtos_task.txt
fi

sleep 3
echo "cat mma heap"
cat /proc/mi_modules/mi_sys_mma/mma_heap_name0 | tee $resultpath/mma_heap.txt
sleep 3
echo "cat meminfo"
cat /proc/meminfo | tee $resultpath/meminfo.txt


