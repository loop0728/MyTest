#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/08/26 14:57:05
# @file        : exit_server.py
# @description :

import json
import socket
from PythonScripts.variables import net_connect_port
from PythonScripts.logger import logger

def exit_server(wait_timeout = 5, delimiter = 'mstar'):
    """
    通知server端退出server.py

    Args:
        NA

    Returns:
        bool: True or False
    """
    logger.print_info("Exit server.")
    host = 'localhost'
    port = int(net_connect_port)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        logger.print_info(f'Connect to server {host}:{port}')
    except Exception as e:
        logger.print_warning(f'maybe sever is offline:error[{e}]')
        raise

    old_timeout = client_socket.gettimeout()
    client_socket.settimeout(wait_timeout)       # 设置5秒超时
    try:
        msg = {"case_name": "exit_server","cmd": "server_exit"}
        msg = json.dumps(msg)
        full_msg = f"{msg}{delimiter}"
        client_socket.sendall(full_msg.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8', errors='replace')
        if 'recv_ok' in response:
            result = True
        else:
            result = False
    except Exception as e:
        logger.print_warning(f"Exception e:{e} {__file__}:"
                             f"{e.__traceback__.tb_lineno}")
        client_socket.settimeout(old_timeout)
        return False
    client_socket.settimeout(old_timeout)
    return result

def main():
    exit_server()

if __name__ == "__main__":
    main()
else:
    print('[*] ERROR: Please run this script directly')