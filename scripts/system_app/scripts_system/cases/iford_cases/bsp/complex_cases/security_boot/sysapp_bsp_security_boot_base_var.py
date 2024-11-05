#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Attributes:
    This dictionary SECURITY_BOOT_PARTITION_EXPECTED_ERRORS contains the expected
    error messages when booting different partition images ( This image contains
    all partitions, where all partitions except the current one are properly
    signed and encrypted ). Each key represents a specific partition or image type,
    and its corresponding value is the expected error message during the boot
    process.
"""
SECURITY_BOOT_PARTITION_EXPECTED_LOG = {
    "ipl": "LoadBL ERR",
    "earlyinit": "Fail ld EINIT",
    "optee": "Fail ld OPTEE",
    "ipl_cust": "Fail ld IPL_CUST",
    "uboot": "Fail ld Uboot",
    "vmm": "Fail ld VMM",
    "rtos": "Fail ld RTK",
    "ramdisk.gz": "Fail ld RAMFS",
    "kernel": "Fail ld KERNEL",
}
