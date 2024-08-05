# -*- coding: utf-8 -*-
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

def handle_client(client_socket, client_address):
    """处理客户端连接的函数"""
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

def start_server(host='127.0.0.1', port=12345, max_workers=10):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=max_workers)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected to {client_address}")
            # 将客户端连接分配给线程池中的线程
            executor.submit(handle_client, client_socket, client_address)
    except KeyboardInterrupt:
        print("Shutting down the server...")
    finally:
        # 销毁线程池，拒绝接收新的任务
        executor.shutdown(wait=False)
        # 关闭服务端socket
        server_socket.close()

if __name__ == '__main__':
    start_server()
