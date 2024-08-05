# -*- coding: utf-8 -*-
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

# 定义处理客户端的函数
def handle_client(client_socket, client_address):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # 如果没有接收到数据，跳出循环
            print(f"Received from {client_address}: {data.decode()}")
            client_socket.sendall(data)  # 回显接收到的数据
    finally:
        client_socket.close()
        print(f"Connection with {client_address} closed")

# 启动服务端的函数
def start_server(host='127.0.0.1', port=12345, max_workers=10):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    # 创建线程池
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected to {client_address}")
            # 将客户端连接分配给线程池中的线程
            executor.submit(handle_client, client_socket, client_address)

if __name__ == '__main__':
    start_server()