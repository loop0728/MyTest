
一、依赖描述
    1. 为了运行rtos perf, 请在编译image时添加CONFIG_SYS_PERF_SUPPORT=y指令以默认开启该功能，不然无法通过SystemApp Cpu Case进行自动化测试，手动测试rtos perf请参考http://sswiki:8090/pages/viewpage.action?pageId=55069492

    2. 为了自动化运行ptree切换不同pipeline 请编译image时添加CONFIG_SYS_PERF_SUPPORT=y CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable CONFIG_PIPELINE_TREE_USING_JSON=y CONFIG_CONFIG_PIPELINE_TREE_FILE="1snr_isp_scl_venc_ptree.json" CONFIG_APPLICATION_AOV=n CONFIG_APPLICATION_SAMPLE=n指令
       --->为了能够放下ptree以及对应的json文件，所以nor flash无法满足空间需求，所以想要自动化切换dualos pipe系统测试必须使用nand falsh

    3. 为了cpu能够支持perf event, 请在编译时在对应的kernel defconfig中添加CONFIG_PERF_EVENTS=y CONFIG_FTRACE=y选项

    4. 为了能解析rtos perf,请将rtos/proj目录下build/xxxxxxxxxxx/out/xxxxxxxxxx.perf.use.map随着image一起release出来

    5. (此步为systemapp提前操作)\proj\tools\perf 下的gen_flamegraph.sh， SysPerfBinTrans.py， stack_funcname_map_lut.pl，SysPerfParse 复制到FlameGraph目录下

    6. (此步为systemapp case集成自动化运行)使用以下命令生成rtos perf火焰图 ./gen_flamegraph.sh -i ./perf.bin -o ./PerfOut.svg -m xxxxxxxxxx.perf.use.map

    7. (此步为systemapp case集成自动化运行)使用以下命令生成linux perf火焰图 ./stackcollapse-perf.pl sys_perf.bin &> perf.folder && ./flamegraph.pl perf.folder > perf.svg

二、操作
    1. make xxxx_defconfig

    2. 执行 echo -e "CONFIG_PERF_EVENTS=y\nCONFIG_FTRACE=y" >> $(find ../kernel -name $(grep -oP 'CONFIG_KERNEL_CONFIG="\K[^"]*' ".config"))

    3. 执行 make image -jx CONFIG_SYS_PERF_SUPPORT=y CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable CONFIG_PIPELINE_TREE_USING_JSON=y CONFIG_CONFIG_PIPELINE_TREE_FILE="1snr_isp_scl_venc_ptree.json" CONFIG_APPLICATION_AOV=n CONFIG_APPLICATION_SAMPLE=n

    4. 执行 cp $(find ../rtos/proj -name $(grep -oP 'CONFIG_RTOS_CONFIG="\K[^"]*' ".config" | sed 's/_defconfig$//')*.perf.use.map) image/output/images/
