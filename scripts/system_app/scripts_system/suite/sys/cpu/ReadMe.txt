
一、依赖描述
1.为了运行rtos perf, 请在编译image时添加CONFIG_SYS_PERF_SUPPORT=y指令以默认开启该功能，不然无法通过SystemApp Cpu Case进行自动化测试，手动测试rtos perf请参考http://sswiki:8090/pages/viewpage.action?pageId=55069492

2.为了自动化运行ptree切换不同pipeline 请编译image时添加CONFIG_CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable指令
  --->为了能够放下ptree以及对应的json文件，所以nor flash无法满足空间需求，所以想要自动化切换dualos pipe系统测试必须使用nand falsh

3.为了cpu能够支持perf event, 请在编译时在对应的kernel defconfig中添加CONFIG_PERF_EVENTS=y CONFIG_FTRACE=y选项
    echo -e "CONFIG_PERF_EVENTS=y\nCONFIG_FTRACE=y" >> $(find ../kernel -name $(grep -oP 'CONFIG_KERNEL_CONFIG="\K[^"]*' ".config"))

二、操作
   1. make xxxx_defconfig
   2. 执行 echo -e "CONFIG_PERF_EVENTS=y\nCONFIG_FTRACE=y" >> $(find ../kernel -name $(grep -oP 'CONFIG_KERNEL_CONFIG="\K[^"]*' ".config"))
   3. 执行 make image -jx CONFIG_SYS_PERF_SUPPORT=y CONFIG_CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable
