【SYSTEM_MENU注意事项】


【环境说明】
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : STR场景介绍
配置说明     :
执行Stage值  :  0x01（默认）
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : 高低帧率切换场景介绍
配置说明     :
执行Stage值  : 0x01
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : 双系统切换场景介绍
配置说明     :
执行Stage值  : 0x01
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

【压测场景说明】
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
环境配置     : 压测场景介绍
配置说明     :
执行Stage值  : 0x10
可以测试场景 :
reboot_stress（owner:harry1.zhang）
ttff_ttcl_stress（owner:harry1.zhang）
str_stress（owner:harry1.zhang）
str_crc_stress（owner:harry1.zhang）
OS_switch_stress（owner:harry1.zhang）
change_fps_stress（owner:harry1.zhang）
注意事项：
测试前请修改压测次数，压测次数对应platform.sh文件中的"CASE STRESS"
通过"AOV/stress_case/out/test_report/"位置记录每条case执行情况
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


【运行说明】
(1)把scripts_system放到挂载目录下
(2)设置platform.sh中的LOG PLATFORM_UART PLATFORM_RELAY PLATFORM_RELAY_PORT PLATFORM_NET_CONNECT_PORT
(3)修改脚本权限 find . -type f -name "*.sh" -exec chmod 777 {} +
(4)进入scripts_system目录
(5)执行命令./system_menu.sh stage=0x01 stage根据当前运行环境决定，参考"执行Stage值"。
(6)输入m
(7)根据测试的场景输入数字

参数说明：
LOG                        : 串口log文件
PLATFORM_UART              : 串口号
PLATFORM_RELAY             : 继电器串口号
PLATFORM_RELAY_PORT        : 继电器路数
PLATFORM_NET_CONNECT_PORT  : 网络端口号