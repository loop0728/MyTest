
一、依赖描述
    1. 为了cpu能够支持perf event, 请在编译时在对应的kernel defconfig中添加CONFIG_PERF_EVENTS=y CONFIG_FTRACE=y选项

二、操作
    1. make xxxx_defconfig

    2. 执行 echo -e "CONFIG_PERF_EVENTS=y\nCONFIG_FTRACE=y" >> $(find ../kernel -name $(grep -oP 'CONFIG_KERNEL_CONFIG="\K[^"]*' ".config"))
