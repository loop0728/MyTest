#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/23 14:48:35
# @file        : str_var.py
# @description :


##################### CASE STR ##################
# PLATFORM_STR: the target of STR
# PLATFORM_REDIRECT_KMSG: the tmp file to save STR kmsg

str_target = 120000
str_kmsg = "/tmp/.str_kmsg"
suspend_entry = "PM: suspend entry"
suspend_exit = "PM: suspend exit"
app_resume = "PM: app resume"
booting_time = "Total cost:"