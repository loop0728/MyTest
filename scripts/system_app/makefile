# SigmaStar trade secret
# Copyright (c) [2019~2020] SigmaStar Technology.
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

BUILD_TOP := $(shell pwd)
ALKAID_PATH ?= $(BUILD_TOP)/../../..
ALKAID_PROJ := $(ALKAID_PATH)/project
ALKAID_PROJ_CONFIG := $(ALKAID_PATH)/project/configs/current.configs
OUT_PATH := $(BUILD_TOP)/out

-include $(ALKAID_PROJ_CONFIG)

CASE_PATH := $(BUILD_TOP)/scripts_system/cases/$(CHIP)_cases

CONDA_PREFIX := /tools/software/anaconda3
CONDA_ACTIVATE := source $(CONDA_PREFIX)/etc/profile.d/conda.sh && conda activate
PYTHON_ENV := $(CONDA_ACTIVATE) py3.7.3-jenkins

export CASE_PATH OUT_PATH

.PHONY: all check release clean

all: release

check:
	$(PYTHON_ENV);sh auto_check.sh

release:
	@if [ -d "$(OUT_PATH)" ]; then \
		rm -rf "$(OUT_PATH)"; \
	fi
	@if [ -d "$(CASE_PATH)" ]; then \
		mkdir -p $(OUT_PATH)/scripts_system/cases/platform; \
		echo "Copying $(CASE_PATH) to $(OUT_PATH)"; \
		find "$(CASE_PATH)" -mindepth 1 -maxdepth 1 -exec cp -r {} "$(OUT_PATH)/scripts_system/cases/platform" \;; \
	else \
		echo "Directory $(CASE_PATH) does not exist"; \
		exit -1;\
	fi
	@rsync -av --exclude 'cases' scripts_system/ $(OUT_PATH)/scripts_system

clean:
	rm -rf "$(OUT_PATH)"
