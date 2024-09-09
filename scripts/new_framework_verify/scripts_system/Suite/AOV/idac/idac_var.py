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

class dvfs_state(Enum):
    DVFS_STATE_OFF = 0
    DVFS_STATE_ON  = 1
    DVFS_STATE_MAX = 2


iford_idac_qfn_dvfs_vcore_table = [
    # dvfs off
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 800, 820],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 830, 850],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 890, 920],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 890, 920],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 960, 980],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 960, 980],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 960, 980]   # dvfs off default; dvfs on: 890, 920
        ]
    ],
    # dvfs on
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 800, 820],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 830, 850],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 800, 820],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 830, 950],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 800, 820],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 830, 850],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ]
    ]
]

# QFN128: vcore equals to vcpu
# BGA11/BGA12: vcore and vcpu are independent
#
# volt[package][overdrive][freq-ic]
iford_idac_volt_core_table = [
    # QFN128
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 800, 820],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 830, 850],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 890, 920],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 890, 920],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 960, 980],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 960, 980],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 960, 980]   # dvfs off default; dvfs on: 890, 920
        ]
    ],
    # BGA11
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 770, 810],
            #700M Hz, fast, slow
            [700000000, 770, 810],
            #800M Hz, fast, slow
            [800000000, 770, 810],
            #900M Hz, fast, slow
            [900000000, 770, 810],
            #1000M Hz, fast, slow
            [1000000000, 770, 810],
            #1100M Hz, fast, slow
            [1100000000, 770, 810],
            #1200M Hz, fast, slow
            [1200000000, 770, 810]
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 870, 910],
            #700M Hz, fast, slow
            [700000000, 870, 910],
            #800M Hz, fast, slow
            [800000000, 870, 910],
            #900M Hz, fast, slow
            [900000000, 870, 910],
            #1000M Hz, fast, slow
            [1000000000, 870, 910],
            #1100M Hz, fast, slow
            [1100000000, 870, 910],
            #1200M Hz, fast, slow
            [1200000000, 870, 910]
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 930, 970],
            #700M Hz, fast, slow
            [700000000, 930, 970],
            #800M Hz, fast, slow
            [800000000, 930, 970],
            #900M Hz, fast, slow
            [900000000, 930, 970],
            #1000M Hz, fast, slow
            [1000000000, 930, 970],
            #1100M Hz, fast, slow
            [1100000000, 930, 970],
            #1200M Hz, fast, slow
            [1200000000, 930, 970]
        ]
    ],
    #BGA12
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 780, 810],
            #700M Hz, fast, slow
            [700000000, 780, 810],
            #800M Hz, fast, slow
            [800000000, 780, 810],
            #900M Hz, fast, slow
            [900000000, 780, 810],
            #1000M Hz, fast, slow
            [1000000000, 780, 810],
            #1100M Hz, fast, slow
            [1100000000, 780, 810],
            #1200M Hz, fast, slow
            [1200000000, 780, 810]
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 880, 910],
            #700M Hz, fast, slow
            [700000000, 880, 910],
            #800M Hz, fast, slow
            [800000000, 880, 910],
            #900M Hz, fast, slow
            [900000000, 880, 910],
            #1000M Hz, fast, slow
            [1000000000, 880, 910],
            #1100M Hz, fast, slow
            [1100000000, 880, 910],
            #1200M Hz, fast, slow
            [1200000000, 880, 910]
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 930, 970],
            #700M Hz, fast, slow
            [700000000, 930, 970],
            #800M Hz, fast, slow
            [800000000, 930, 970],
            #900M Hz, fast, slow
            [900000000, 930, 970],
            #1000M Hz, fast, slow
            [1000000000, 930, 970],
            #1100M Hz, fast, slow
            [1100000000, 930, 970],
            #1200M Hz, fast, slow
            [1200000000, 930, 970]
        ]
    ]
]

iford_idac_volt_cpu_table = [
    # QFN128
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 800, 820],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 830, 850],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 890, 920],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 890, 920],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 890, 920]   # dvfs off default; dvfs on: 890, 920
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 960, 980],   # dvfs off default; dvfs on: 800, 820
            #800M Hz, fast, slow
            [800000000, 960, 980],   # dvfs off default; dvfs on: 830, 850
            #1G Hz, fast, slow
            [1000000000, 960, 980]   # dvfs off default; dvfs on: 890, 920
        ]
    ],
    # BGA11
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 770, 800],
            #700M Hz, fast, slow
            [700000000, 820, 790],
            #800M Hz, fast, slow
            [800000000, 810, 850],
            #900M Hz, fast, slow
            [900000000, 840, 880],
            #1000M Hz, fast, slow
            [1000000000, 870, 900],
            #1100M Hz, fast, slow
            [1100000000, 910, 930],
            #1200M Hz, fast, slow
            [1200000000, 940, 970]
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 770, 800],
            #700M Hz, fast, slow
            [700000000, 790, 820],
            #800M Hz, fast, slow
            [800000000, 810, 850],
            #900M Hz, fast, slow
            [900000000, 840, 880],
            #1000M Hz, fast, slow
            [1000000000, 870, 900],
            #1100M Hz, fast, slow
            [1100000000, 910, 930],
            #1200M Hz, fast, slow
            [1200000000, 940, 970]
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 770, 800],
            #700M Hz, fast, slow
            [700000000, 790, 820],
            #800M Hz, fast, slow
            [800000000, 810, 850],
            #900M Hz, fast, slow
            [900000000, 840, 880],
            #1000M Hz, fast, slow
            [1000000000, 870, 900],
            #1100M Hz, fast, slow
            [1100000000, 910, 930],
            #1200M Hz, fast, slow
            [1200000000, 940, 970]
        ]
    ],
    #BGA12
    [
        # LD
        [
            #600M Hz, fast, slow
            [600000000, 760, 790],
            #700M Hz, fast, slow
            [700000000, 780, 810],
            #800M Hz, fast, slow
            [800000000, 800, 840],
            #900M Hz, fast, slow
            [900000000, 830, 870],
            #1000M Hz, fast, slow
            [1000000000, 860, 890],
            #1100M Hz, fast, slow
            [1100000000, 890, 920],
            #1200M Hz, fast, slow
            [1200000000, 920, 950]
        ],
        # NOD
        [
            #600M Hz, fast, slow
            [600000000, 760, 790],
            #700M Hz, fast, slow
            [700000000, 780, 810],
            #800M Hz, fast, slow
            [800000000, 800, 840],
            #900M Hz, fast, slow
            [900000000, 830, 870],
            #1000M Hz, fast, slow
            [1000000000, 860, 890],
            #1100M Hz, fast, slow
            [1100000000, 890, 920],
            #1200M Hz, fast, slow
            [1200000000, 920, 950]
        ],
        # OD
        [
            #600M Hz, fast, slow
            [600000000, 760, 790],
            #700M Hz, fast, slow
            [700000000, 780, 810],
            #800M Hz, fast, slow
            [800000000, 800, 840],
            #900M Hz, fast, slow
            [900000000, 830, 870],
            #1000M Hz, fast, slow
            [1000000000, 860, 890],
            #1100M Hz, fast, slow
            [1100000000, 890, 920],
            #1200M Hz, fast, slow
            [1200000000, 920, 950]
        ]
    ]
]

# overdrive: 0 -> LD,  IPL cpufreq 600M Hz
#            1 -> NOD, IPL cpufreq   1G Hz
#            2 -> OD,  IPL cpufreq   1G Hz
iford_ipl_overdrive_cpufreq_map = [600000000, 1000000000, 1000000000]
