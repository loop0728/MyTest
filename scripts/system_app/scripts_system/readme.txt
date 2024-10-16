【SYSTEM_MENU注意事项】


【环境说明】
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : IPC_1SNR_SC4336P_AOV
配置说明     : http://sswiki.sigmastar.com.tw:8090/display/AW/IPC_1SNR_SC4336P_AOV
执行Stage值  :  0x01（默认）
可以测试场景 :
aov:
    ttff_ttcl（owner:harry1.zhang）
    os_switch（owner:harry1.zhang）
    str（owner:koda.xu）
    str_crc（owner:koda.xu）
idac（owner:koda.xu）
cpu（owner:junqiang.bi）
interrupts（owner:junqiang.bi）
memory（owner:junqiang.bi）
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : IPC_1SNR_IMX415_LINUX
配置说明     : http://sswiki.sigmastar.com.tw:8090/display/AW/IPC_1SNR_IMX415_LINUX
执行Stage值  : 0x02
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : IPC_2SNR_SC4336P_LINUX
配置说明     : http://sswiki.sigmastar.com.tw:8090/display/AW/IPC_2SNR_SC4336P_LINUX
执行Stage值  : 0x04
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : IPC_1SNR_IMX415_DUALOS
配置说明     : http://sswiki.sigmastar.com.tw:8090/display/AW/IPC_1SNR_IMX415_DUALOS
执行Stage值  : 0x08
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


【运行说明】
(1)把scripts_system放到挂载目录下
(2)设置sysapp_platform.py中的LOG_PATH PLATFORM_UART PLATFORM_RELAY PLATFORM_RELAY_PORT PLATFORM_NET_CONNECT_PORT等值
(3)修改脚本权限 find . -type f -name "*.sh" -exec chmod 777 {} +
(4)进入scripts_system目录
(5)执行命令./system_menu.sh stage=0x01 stage根据当前运行环境决定，参考"执行Stage值"。
(6)输入m
(7)根据测试的场景输入数字

参数说明：
LOG_PATH                   : 串口log文件
PLATFORM_UART              : 串口号
PLATFORM_RELAY             : 继电器串口号
PLATFORM_RELAY_PORT        : 继电器路数
PLATFORM_NET_CONNECT_PORT  : 网络端口号
