"""Exit server."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import socket
from python_scripts.variables import net_connect_port
from python_scripts.logger import logger

def exit_server(wait_timeout=5, delimiter='mstar'):
    """
    Notify server exit.

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
    client_socket.settimeout(wait_timeout)
    try:
        msg = {"case_name": "exit_server", "cmd": "server_exit"}
        msg = json.dumps(msg)
        full_msg = f"{msg}{delimiter}"
        client_socket.sendall(full_msg.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8', errors='replace')
        if 'recv_ok' in response:
            result = True
        else:
            result = False
    except Exception as e:
        logger.print_warning(f"Exception e:{e}")
        client_socket.settimeout(old_timeout)
        return False
    client_socket.settimeout(old_timeout)
    return result

def main():
    """Entry"""
    exit_server()

if __name__ == "__main__":
    main()
else:
    print('[*] ERROR: Please run this script directly')
