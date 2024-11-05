current_os=$1
casename=$(basename $2 .json)
resultpath=""

if [ -z "$current_os" ]; then
    echo "current_os is null assign to purelinux"
    current_os="purelinux"
fi
echo "pass param current_os:$current_os"
if [ "$casename" == ".json" ]; then
    echo "casename $casename is null"
    exit -1
elif [ "$casename" == "" ]; then
    echo "casename: $casename is null"
    exit -1
else
    echo "casename: $casename"
fi

resultpath=/mnt/out/Cpu/$current_os/$casename

mkdir -p $resultpath

if [ "$current_os" = "dualos" ]; then
    echo "dualos cli perf"
    echo cli perf > /proc/dualos/rtos
    sleep 5
    echo cli perf --dump "$resultpath/perf.bin" > /proc/dualos/rtos
    sleep 3
    echo cli taskstat  > /proc/dualos/rtos
    cat /proc/dualos/log | tee $resultpath/rtos_task.txt
else
    echo "linux cpu perf"
    ./perfbin/perf record -e cpu-clock -g -o $resultpath/sys.perf sleep 10
    sleep 1
    ./perfbin/perf script -i $resultpath/sys.perf > $resultpath/sys_perf.bin
fi
