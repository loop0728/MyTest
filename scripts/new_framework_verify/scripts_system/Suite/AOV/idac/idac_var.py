#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/23 14:48:35
# @file        : str_var.py
# @description :


##################### CASE IDAC ##################
from enum import Enum

class overdrive_type(Enum):
    OVERDRIVE_TYPE_LD  = 0
    OVERDRIVE_TYPE_NOD = 1
    OVERDRIVE_TYPE_OD  = 2
    OVERDRIVE_TYPE_MAX = 3

class package_type(Enum):
    PACKAGE_TYPE_QFN128 = 0
    PACKAGE_TYPE_BGA11  = 1
    PACKAGE_TYPE_BGA12  = 2
    PACKAGE_TYPE_MAX    = 3

class corner_ic_type(Enum):
    CORNER_IC_TYPE_SLOW = 0
    CORNER_IC_TYPE_FAST = 1
    CORNER_IC_TYPE_MAX  = 2

class idac_power_type(Enum):
    IDAC_POWER_TYPE_CORE = 0
    IDAC_POWER_TYPE_CPU  = 1
    IDAC_POWER_TYPE_MAX  = 2

# QFN128: vcore equals to vcpu
# BGA11/BGA12: vcore and vcpu are independent
#
# volt[package][overdrive][freq-ic]
iford_idac_volt_core_table = [
    # QFN128
    [
        # LD
        [
            #600M Hz, slow, fast
            [600000000, 820, 800],
        ],
        # NOD
        [
            #600M Hz, slow, fast
            [600000000, 920, 890],   # 820, 800
            #800M Hz, slow, fast
            [800000000, 920, 890],   # 850, 830
            #1G Hz, slow, fast
            [1000000000, 920, 890]
        ],
        # OD
        [
            #600M Hz, slow, fast
            [600000000, 980, 960],   # 820, 800
            #800M Hz, slow, fast
            [800000000, 980, 960],   # 850, 830
            #1G Hz, slow, fast
            [1000000000, 980, 960]   # 920, 890
        ]
    ],
    # BGA11
    [
        # LD
        [
            #600M Hz, slow, fast
            [600000000, 810, 770],
            #700M Hz, slow, fast
            [700000000, 810, 770],
            #800M Hz, slow, fast
            [800000000, 810, 770],
            #900M Hz, slow, fast
            [900000000, 810, 770],
            #1000M Hz, slow, fast
            [1000000000, 810, 770],
            #1100M Hz, slow, fast
            [1100000000, 810, 770],
            #1200M Hz, slow, fast
            [1200000000, 810, 770]
        ],
        # NOD
        [
            #600M Hz, slow, fast
            [600000000, 910, 870],
            #700M Hz, slow, fast
            [700000000, 910, 870],
            #800M Hz, slow, fast
            [800000000, 910, 870],
            #900M Hz, slow, fast
            [900000000, 910, 870],
            #1000M Hz, slow, fast
            [1000000000, 910, 870],
            #1100M Hz, slow, fast
            [1100000000, 910, 870],
            #1200M Hz, slow, fast
            [1200000000, 910, 870]
        ],
        # OD
        [
            #600M Hz, slow, fast
            [600000000, 970, 930],
            #700M Hz, slow, fast
            [700000000, 970, 930],
            #800M Hz, slow, fast
            [800000000, 970, 930],
            #900M Hz, slow, fast
            [900000000, 970, 930],
            #1000M Hz, slow, fast
            [1000000000, 970, 930],
            #1100M Hz, slow, fast
            [1100000000, 970, 930],
            #1200M Hz, slow, fast
            [1200000000, 970, 930]
        ]
    ],
    #BGA12
    [
        # LD
        [
            #600M Hz, slow, fast
            [600000000, 810, 780],
            #700M Hz, slow, fast
            [700000000, 810, 780],
            #800M Hz, slow, fast
            [800000000, 810, 780],
            #900M Hz, slow, fast
            [900000000, 810, 780],
            #1000M Hz, slow, fast
            [1000000000, 810, 780],
            #1100M Hz, slow, fast
            [1100000000, 810, 780],
            #1200M Hz, slow, fast
            [1200000000, 810, 780]
        ],
        # NOD
        [
            #600M Hz, slow, fast
            [600000000, 910, 880],
            #700M Hz, slow, fast
            [700000000, 910, 880],
            #800M Hz, slow, fast
            [800000000, 910, 880],
            #900M Hz, slow, fast
            [900000000, 910, 880],
            #1000M Hz, slow, fast
            [1000000000, 910, 880],
            #1100M Hz, slow, fast
            [1100000000, 910, 880],
            #1200M Hz, slow, fast
            [1200000000, 910, 880]
        ],
        # OD
        [
            #600M Hz, slow, fast
            [600000000, 970, 930],
            #700M Hz, slow, fast
            [700000000, 970, 930],
            #800M Hz, slow, fast
            [800000000, 970, 930],
            #900M Hz, slow, fast
            [900000000, 970, 930],
            #1000M Hz, slow, fast
            [1000000000, 970, 930],
            #1100M Hz, slow, fast
            [1100000000, 970, 930],
            #1200M Hz, slow, fast
            [1200000000, 970, 930]
        ]
    ]
]

iford_idac_volt_cpu_table = [
    # QFN128
    [
        # LD
        [
            #600M Hz, slow, fast
            [600000000, 820, 800],
        ],
        # NOD
        [
            #600M Hz, slow, fast
            [600000000, 920, 890],   # 820, 800
            #800M Hz, slow, fast
            [800000000, 920, 890],   # 850, 830
            #1G Hz, slow, fast
            [1000000000, 920, 890]
        ],
        # OD
        [
            #600M Hz, slow, fast
            [600000000, 980, 960],   # 820, 800
            #800M Hz, slow, fast
            [800000000, 980, 960],   # 850, 830
            #1G Hz, slow, fast
            [1000000000, 980, 960]   # 920, 890
        ]
    ],
    # BGA11
    [
        # LD
        [
            #600M Hz, slow, fast
            [600000000, 800, 770],
            #700M Hz, slow, fast
            [700000000, 820, 790],
            #800M Hz, slow, fast
            [800000000, 850, 810],
            #900M Hz, slow, fast
            [900000000, 880, 840],
            #1000M Hz, slow, fast
            [1000000000, 900, 870],
            #1100M Hz, slow, fast
            [1100000000, 930, 910],
            #1200M Hz, slow, fast
            [1200000000, 970, 940]
        ],
        # NOD
        [
            #600M Hz, slow, fast
            [600000000, 800, 770],
            #700M Hz, slow, fast
            [700000000, 820, 790],
            #800M Hz, slow, fast
            [800000000, 850, 810],
            #900M Hz, slow, fast
            [900000000, 880, 840],
            #1000M Hz, slow, fast
            [1000000000, 900, 870],
            #1100M Hz, slow, fast
            [1100000000, 930, 910],
            #1200M Hz, slow, fast
            [1200000000, 970, 940]
        ],
        # OD
        [
            #600M Hz, slow, fast
            [600000000, 800, 770],
            #700M Hz, slow, fast
            [700000000, 820, 790],
            #800M Hz, slow, fast
            [800000000, 850, 810],
            #900M Hz, slow, fast
            [900000000, 880, 840],
            #1000M Hz, slow, fast
            [1000000000, 900, 870],
            #1100M Hz, slow, fast
            [1100000000, 930, 910],
            #1200M Hz, slow, fast
            [1200000000, 970, 940]
        ]
    ],
    #BGA12
    [
        # LD
        [
            #600M Hz, slow, fast
            [600000000, 790, 760],
            #700M Hz, slow, fast
            [700000000, 810, 780],
            #800M Hz, slow, fast
            [800000000, 840, 800],
            #900M Hz, slow, fast
            [900000000, 870, 830],
            #1000M Hz, slow, fast
            [1000000000, 890, 860],
            #1100M Hz, slow, fast
            [1100000000, 920, 890],
            #1200M Hz, slow, fast
            [1200000000, 950, 920]
        ],
        # NOD
        [
            #600M Hz, slow, fast
            [600000000, 790, 760],
            #700M Hz, slow, fast
            [700000000, 810, 780],
            #800M Hz, slow, fast
            [800000000, 840, 800],
            #900M Hz, slow, fast
            [900000000, 870, 830],
            #1000M Hz, slow, fast
            [1000000000, 890, 860],
            #1100M Hz, slow, fast
            [1100000000, 920, 890],
            #1200M Hz, slow, fast
            [1200000000, 950, 920]
        ],
        # OD
        [
            #600M Hz, slow, fast
            [600000000, 790, 760],
            #700M Hz, slow, fast
            [700000000, 810, 780],
            #800M Hz, slow, fast
            [800000000, 840, 800],
            #900M Hz, slow, fast
            [900000000, 870, 830],
            #1000M Hz, slow, fast
            [1000000000, 890, 860],
            #1100M Hz, slow, fast
            [1100000000, 920, 890],
            #1200M Hz, slow, fast
            [1200000000, 950, 920]
        ]
    ]
]

# overdrive: 0 -> LD,  IPL cpufreq 600M Hz
#            1 -> NOD, IPL cpufreq   1G Hz
#            2 -> OD,  IPL cpufreq   1G Hz
iford_ipl_overdrive_cpufreq_map = [600000000, 1000000000, 1000000000]
