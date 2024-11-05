一、依赖描述
    1. 为了自动化运行ptree切换不同pipeline 请编译image时添加make image -jx CONFIG_SYS_PERF_SUPPORT=y CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable CONFIG_PIPELINE_TREE_USING_JSON=y CONFIG_CONFIG_PIPELINE_TREE_FILE="1snr_isp_scl_v  enc_ptree.json" CONFIG_APPLICATION_AOV=n CONFIG_APPLICATION_SAMPLE=n指令
       --->为了能够放下ptree以及对应的json文件，所以nor flash无法满足空间需求，所以想要自动化切换dualos pipe系统测试必须使用nand falsh

二、操作
    1. make xxxx_defconfig

    2. 执行 make image -jx CONFIG_SYS_PERF_SUPPORT=y CONFIG_PIPELINE_TREE=y CONFIG_VERIFY_PTREE=y CONFIG_RTOS_APPLICATION=ptree verify_ptree=enable CONFIG_PIPELINE_TREE_USING_JSON=y CONFIG_CONFIG_PIPELINE_TREE_FILE="1snr_isp_scl_v  enc_ptree.json" CONFIG_APPLICATION_AOV=n CONFIG_APPLICATION_SAMPLE=n
