#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Attributes:
    board_dir_for_server: board directory fot run server cmd
    server_dir_for_server: server directory fot run server cmd
    server_dir_for_board: board directory fot run board cmd
    board_dir_for_board: server directory fot run board cmd
"""
EMMC_RESOURCE_DIR = {
    "board_dir_for_server": "./cases/platform/resource/board/",
    "server_dir_for_server": "./cases/platform/resource/server/",
    "server_dir_for_board": "/mnt/scripts_system/cases/platform/resource/server/",
    "board_dir_for_board": "/mnt/scripts_system/cases/platform/resource/board/"
}
"""
Attributes:
    BLOCK_SIZE: EMMC Block Size
"""
BLOCK_SIZE = 512
