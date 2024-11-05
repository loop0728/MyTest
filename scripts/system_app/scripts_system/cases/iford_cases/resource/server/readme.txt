dtb2unfdt:
    功能：获取dts的工具
    获取方式：动态获取
    源地址：kernel/scripts/
    打包方式：/sdk/verify/bsp_demo/bsp_scene_test.mk

dtc:
    功能：获取dts和生产dts的工具
    获取方式：静态上code(受限于linux服务器环境)
    源地址：sdk/verify/bsp_demo/scripts_bsp/resource/tool
    打包方式：sdk/verify/bsp_demo/scripts_bsp/resource/tool

mkimage:
    功能：给image更新头部信息
    获取方式：动态获取
    源地址：kernel/scripts/
    打包方式：/sdk/verify/bsp_demo/bsp_scene_test.mk

otapack:
    功能：ota打包
    获取方式：动态获取
    源地址：sdk/verify/sstar_ota
    打包方式：/sdk/verify/bsp_demo/bsp_scene_test.mk

rtos_replace_sys:
    功能：包含动态更换rtos-sys文件的工具
    获取方式：动态获取
    源地址：xxxx
    打包方式：/sdk/verify/bsp_demo/bsp_scene_test.mk

szsplit，szdec，sz:
    功能：sz压缩的工具
    获取方式：动态获取
    源地址：kernel/scripts/
    打包方式：/sdk/verify/bsp_demo/bsp_scene_test.mk

szrestore:
    功能：sz解压缩的工具
    获取方式：动态获取
    源地址：project/image/security_boot_tools/tools/unsz/szrestore
    打包方式：/sdk/verify/bsp_demo/bsp_scene_test.mk
