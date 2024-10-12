
1.为了运行rtos perf, 请在编译image时添加CONFIG_SYS_PERF_SUPPORT=y指令以默认开启该功能，不然无法通过SystemApp Cpu Case进行自动化测试，手动测试rtos perf请参考http://sswiki:8090/pages/viewpage.action?pageId=55069492

2.为了自动化运行ptree切换不同pipeline 请编译image时添加CONFIG_CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable指令
  --->为了能够放下ptree以及对应的json文件，所以nor flash无法满足空间需求，所以想要自动化切换dualos pipe系统测试必       须使用nand falsh
