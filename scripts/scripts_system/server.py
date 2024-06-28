import sys
import os
import time
import socket
import threading
import logging
from PythonScripts.variables import net_connect_port
from pathlib import Path
sys.path.append("PythonScripts")
from uart_record import create_and_start_uartlog_contrl,stop_and_close_uartlog_contrl
#from PythonScripts.uart_record import create_and_start_uartlog_contrl,stop_and_close_uartlog_contrl

test_handler  = None
client_handler = None
thread_run    = True
# 创建 Socket 对象
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def system_case_Run(param_list):
    Module_Path_Name = param_list[0]
    #print("param_list[1:]:", Module_Path_Name)
    Module_Path = "/".join(Module_Path_Name.split("/")[:-1])
    Module_Name = Module_Path_Name.split("/")[-1].split(".")[0]
    sys.path.append(Module_Path)
    module = __import__(Module_Name)

    #print("param_list[1:]:", param_list[1:])
    if param_list[1] == "help":
        module.system_help(param_list[1:])
        return 0

    result = module.system_runcase(param_list[1:])
    return result

def handle_client():
    global thread_run
    global server_socket
    while thread_run is True:
        client,addr = server_socket.accept()
        #print(f"[INFO] Accepted connection from {addr[0]}:{addr[1]}")
        request = client.recv(1024)
        #print(f"Received: {request.decode('utf-8')}")
        param = request.decode('utf-8').split("+")

        #判断exit处理server退出
        if len(param) == 1 and param[0] == "exit":
            client.send("OK".encode('utf-8'))
            print("get exit msg, exit server py")
            thread_run = False
            client.close()
            server_socket.close()
            stop_and_close_uartlog_contrl()
            server_socket = None
            return 0

        #判断param参数正确，运行case
        if len(param) >= 2:
            try:
               ret = system_case_Run(param)
               if ret != 0:
                   client.send("NG".encode('utf-8'))
               else:
                   client.send("OK".encode('utf-8'))
            except Exception as e:
                client.send("NG".encode('utf-8'))
                client.close()
                logging.exception("Error processing client request")
        else:
            client.send("NG".encode('utf-8'))

        client.close()
        #server_socket.close()


def server_Init():
    print("server_Init\n")
    global thread_run
    global server_socket

    # 绑定 IP 和端口
    server_socket.bind(('localhost', int(net_connect_port)))

    # 监听连接
    server_socket.listen(5)
    thread_run = True
    create_and_start_uartlog_contrl()
    global client_handler
    client_handler = threading.Thread(target=handle_client)
    client_handler.start()


if __name__ == "__main__":
    server_Init()
