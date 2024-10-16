#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Attributes:
    ott_time_standard: ott_time_standard in booting time (IPL-Next_Flow us)
    autok_time_standard: autok_time_standard in booting time (IPL-Next_Flow us)
"""
BOOTING_TIME_STANDARD = {
    "OTT_TIME_STANDARD": 200000,
    "AUTOK_TIME_STANDARD": 550000,
}
"""
Attributes:
    AUTOK_FLAG OTT_FLAG: Flag bit about force ott in ott partition
"""
OTT_FORCE_FLAG = {
    "AUTOK_FLAG": "656e3d31",
    "OTT_FLAG": "656e3d30",
}
"""
Attributes:
    USE_DEFUL ...: Different return values of ddr_ott mode in the uboot command
"""
OTT_MODE_UBOOT_KEYWORD = {
    "USE_DEFUL": "ddr initail with default settings",
    "USE_TRAIN_DATA": "ddr initail with training data applied",
    "RUN_AUTOK": "ddr initail with force training"
}
"""
Attributes:
    BANK OFFSET: Register address that marks the current ott and autok status
    USE_DEFUL ...: Different states represent different values
"""
OTT_MODE_REG = {
    "BANK": "0x1004",
    "OFFSET": "0xB",
    "USE_DEFUL": "0x0000",
    "USE_TRAIN_DATA": "0x0001",
    "RUN_AUTOK": "0x0002"
}
"""
Attributes:
    DUMP FORCE_AUTOK ...: About ott related boot cmd in uboot
"""
OTT_CMD_UBOOT = {
    "DUMP": "ddr_ott dump 0x21000000",
    "FORCE_AUTOK": "ddr_ott force 1",
    "FORCE_OTT": "ddr_ott force 0",
    "MODE": "ddr_ott mode"
}
OTT_PARTITION_NAME = "DDRTRAIN"
