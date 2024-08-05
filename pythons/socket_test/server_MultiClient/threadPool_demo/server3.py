# -*- coding: utf-8 -*-
import socket
import threading
import select
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor

r_list = []
r_list_lock = threading.Lock()
server_running = False

def handle_client(client_socket, client_address):
    """处理客户端连接的函数"""
    global r_list, r_list_lock, server_running
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # 如果没有接收到数据，跳出循环
            print(f"Received from {client_address}: {data.decode()}")
            client_socket.sendall(data)  # 回显接收到的数据
            if data.decode() == 'server_exit':
                print(f'server exit response done and exit now')
                break
    finally:
        with r_list_lock:
            server_running = False
            r_list.remove(client_socket.fileno())
            print(f"remove socket, r_list; {r_list} ===================")
        client_socket.close()    
        print(f"Connection with {client_address} closed")

def start_server(host='127.0.0.1', port=12345, max_workers=10):
    global r_list, r_list_lock, server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #绑定该端口的socket关闭后，端口可以立即重新绑定socket和使用
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.setblocking(False)  # 设置socket为非阻塞模式
    # 将socket添加到文件描述符集合中
    r_list = [server_socket.fileno()]
    server_running = True
    server_socket_err = False
    
    run_time = 0

    print(f"Server listening on {host}:{port}")

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=max_workers)

    try:
        while True:
            #recv_socket, recv_address = server_socket.accept()
            with r_list_lock:
                rlist = r_list
                if r_list is None:
                    break
                if server_running == False:
                    break
            
            print(f'select {run_time} server_running: {server_running}================================')
            readable, writable, exceptional = select.select(rlist, [], rlist, 5)  #5s超时，不设置时为阻塞模式
            
            if exceptional:
                for s in exceptional:
                    if s is server_socket.fileno():
                        server_socket_err = True
                        break
                if server_socket_err:
                    # 检查 socket 错误
                    error = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    print(f"Socket error: {error}")
                    if error != 0:
                        print(f"Socket error: {error}")
                        break
            
            if readable:
                for s in readable:
                    if s is server_socket.fileno():  #判断可读的socket是否和server_socket是同一个(基于身份的判断于对象的内容无关)
                        #接受新的连接
                        recv_socket, recv_address = server_socket.accept()
                        print(f"Accepted connection from {recv_address}")
                        with r_list_lock:
                            r_list.append(recv_socket.fileno())
                    else:
                        #接收数据
                        print(f'thread pool {run_time} ================================')
                        print(f"server recv: Connected to {recv_address}, len(readable): {len(readable)}, len(rlist): {len(rlist)}")
                        # 将客户端连接分配给线程池中的线程
                        executor.submit(handle_client, recv_socket, recv_address)
                        run_time += 1
                        time.sleep(3)
    except KeyboardInterrupt:
        print("Shutting down the server...")
    finally:
        # 销毁线程池，拒绝接收新的任务
        executor.shutdown(wait=False)
        # 关闭服务端socket
        server_socket.close()
        print('server close')

if __name__ == '__main__':
    start_server()
