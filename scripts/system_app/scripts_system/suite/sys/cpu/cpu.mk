# SigmaStar trade secret
# Copyright (c) [2019~2022] SigmaStar Technology.
# All rights reserved.
#
# Unless otherwise stipulated in writing, any and all information contained
# herein regardless in any format shall remain the sole proprietary of
# SigmaStar and be kept in strict confidence
# (SigmaStar Confidential Information) by the recipient.
# Any unauthorized act including without limitation unauthorized disclosure,
# copying, use, reproduction, sale, distribution, modification, disassembling,
# reverse engineering and compiling of the contents of SigmaStar Confidential
# Information is unlawful and strictly prohibited. SigmaStar hereby reserves the
# rights to any and all damages, losses, costs and expenses resulting therefrom.
#

.PHONY: resource_release

-include $(ALKAID_PROJ)/configs/current.configs

CPU_RESOURCE_PATH := $(OUT_PATH)/scripts_system/suite/sys/cpu/resource

resource_release:
	@echo "ALKAID_PROJ:$(ALKAID_PROJ)"
	@echo "RTOS_CONFIG:$(RTOS_CONFIG) out_path:$(OUT_PATH)"
	@echo "CPU_RESOURCE_PATH:$(CPU_RESOURCE_PATH)"
	@mkdir -p $(CPU_RESOURCE_PATH)/FlameGraph
	-cp -rf $$(find $(ALKAID_PROJ)/../rtos/proj -name $$(echo $(RTOS_CONFIG) | sed 's/_defconfig$$//')*.perf.use.map) $(CPU_RESOURCE_PATH)/FlameGraph/
	-cp -rf $(ALKAID_PROJ)/../rtos/proj/tools/perf/* $(CPU_RESOURCE_PATH)/FlameGraph/

