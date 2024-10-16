#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Common types definition"""

from enum import Enum


class SysappErrorCodes(Enum):
    """Error Codes Enum"""
    SUCCESS = 0
    FAIL = 1
    REBOOT = 2
    ESTAR = 3
    TOLINUX = 4

class SysappBootStage(Enum):
    """Boot Stage Enum."""
    E_BOOTSTAGE_UBOOT = 1
    E_BOOTSTAGE_KERNEL = 2
    E_BOOTSTAGE_UNKNOWN = 3

class SysappPackageType(Enum):
    """A class representing package type of chip"""
    PACKAGE_TYPE_QFN128 = 0
    PACKAGE_TYPE_BGA11 = 1
    PACKAGE_TYPE_BGA12 = 2
    PACKAGE_TYPE_MAX = 3

class SysappBootstrapType(Enum):
    """A class representing bootstrap type of device"""
    BOOTSTRAP_TYPE_NOR = 0
    BOOTSTRAP_TYPE_NAND = 1
    BOOTSTRAP_TYPE_EMMC = 2
    BOOTSTRAP_TYPE_MAX = 3

class SysappCornerIcType(Enum):
    """A class representing corner ic type"""
    CORNER_IC_TYPE_SLOW = 0
    CORNER_IC_TYPE_FAST = 1
    CORNER_IC_TYPE_MAX = 2

class SysappIdacPowerType(Enum):
    """A class representing power type of chip"""
    IDAC_POWER_TYPE_CORE = 0
    IDAC_POWER_TYPE_CPU = 1
    IDAC_POWER_TYPE_MAX = 2

class SysappOverdriveType(Enum):
    """A class representing overdrive type of chip"""
    OVERDRIVE_TYPE_LD = 0
    OVERDRIVE_TYPE_NOD = 1
    OVERDRIVE_TYPE_OD = 2
    OVERDRIVE_TYPE_MAX = 3

class SysappDvfsState(Enum):
    """A class representing dvfs setting of chip"""
    DVFS_STATE_OFF = 0
    DVFS_STATE_ON = 1
    DVFS_STATE_MAX = 2
